#!/usr/bin/env python3
"""Transcribe a call recording through any OpenAI-compatible Whisper API.

Works with Groq (fast, cheap), OpenAI, or a local server (faster-whisper-server,
whisper.cpp server, LocalAI) so audio never leaves your machine.

Environment:
  WHISPER_API_KEY    API key (or GROQ_API_KEY / OPENAI_API_KEY)
  WHISPER_BASE_URL   default: https://api.groq.com/openai/v1 if GROQ_API_KEY is set,
                     else https://api.openai.com/v1
  WHISPER_MODEL      default: whisper-large-v3 (Groq) / whisper-1 (OpenAI)

Usage:
  python3 transcribe.py call.m4a -o transcript.txt --language en
  python3 transcribe.py call.mp4 --language ru --prompt "Anna, ETF, ипотека"
  python3 transcribe.py call.wav --base-url http://localhost:8000/v1 --model large-v3

Files over 20 MB or longer than --chunk minutes are split with ffmpeg (required then).
Silent chunks are skipped (Whisper hallucinates on silence) and known hallucination
lines are removed.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid

HALLUCINATIONS = [
    r"thank(s| you) for watching",
    r"subtitles? (by|from)",
    r"please subscribe",
    r"продолжение следует",
    r"субтитры (сделал|создавал|подготовил)",
    r"редактор субтитров",
    r"спасибо за просмотр",
    r"amara\.org",
    r"untertitel (im auftrag|von)",
]
HALL_RE = re.compile("|".join(HALLUCINATIONS), re.I)
MAX_BYTES = 20 * 1024 * 1024


def env_defaults():
    key = os.environ.get("WHISPER_API_KEY") or os.environ.get("GROQ_API_KEY") or os.environ.get("OPENAI_API_KEY")
    groq = bool(os.environ.get("GROQ_API_KEY")) and not os.environ.get("WHISPER_BASE_URL")
    base = os.environ.get("WHISPER_BASE_URL") or ("https://api.groq.com/openai/v1" if groq else "https://api.openai.com/v1")
    model = os.environ.get("WHISPER_MODEL") or ("whisper-large-v3" if "groq" in base else "whisper-1")
    return key, base, model


def multipart(fields, file_field, path):
    boundary = uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        if v is None:
            continue
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    with open(path, "rb") as f:
        data = f.read()
    name = os.path.basename(path)
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; filename=\"{name}\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n".encode() + data + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def transcribe_file(path, key, base, model, language, prompt, retries=5):
    body, ctype = multipart(
        {"model": model, "language": language, "prompt": prompt, "temperature": "0", "response_format": "json"},
        "file",
        path,
    )
    req = urllib.request.Request(base.rstrip("/") + "/audio/transcriptions", data=body, method="POST")
    req.add_header("Content-Type", ctype)
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    delay = 5
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(r.read().decode()).get("text", "").strip()
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                print(f"  HTTP {e.code}, retry in {delay}s", file=sys.stderr)
                time.sleep(delay)
                delay *= 2
                continue
            raise SystemExit(f"transcription failed: HTTP {e.code} {msg}")
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise SystemExit(f"transcription failed: {e}")
    return ""


def duration_sec(path):
    if not shutil.which("ffprobe"):
        return None
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    ).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return None


def mean_volume(path):
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", out)
    return float(m.group(1)) if m else 0.0


def split(path, chunk_min, tmp):
    pattern = os.path.join(tmp, "chunk_%03d.m4a")
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path, "-vn", "-ac", "1", "-ar", "16000",
         "-c:a", "aac", "-b:a", "48k", "-f", "segment", "-segment_time", str(chunk_min * 60), pattern],
        check=True,
    )
    return sorted(os.path.join(tmp, f) for f in os.listdir(tmp) if f.startswith("chunk_"))


def clean(text):
    lines = [s for s in re.split(r"(?<=[.!?])\s+", text) if s and not HALL_RE.search(s)]
    return " ".join(lines).strip()


def main():
    key, base, model = env_defaults()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("-o", "--out")
    ap.add_argument("--language", help="ISO code: en, ru, de... (recommended)")
    ap.add_argument("--prompt", help="names and terms to bias spelling")
    ap.add_argument("--base-url", default=base)
    ap.add_argument("--model", default=model)
    ap.add_argument("--chunk", type=int, default=10, help="chunk length in minutes (default 10)")
    ap.add_argument("--silence-db", type=float, default=-55.0, help="skip chunks quieter than this")
    a = ap.parse_args()

    if not key and "localhost" not in a.base_url and "127.0.0.1" not in a.base_url:
        sys.exit("set WHISPER_API_KEY (or GROQ_API_KEY / OPENAI_API_KEY), or use --base-url for a local server")

    size = os.path.getsize(a.file)
    dur = duration_sec(a.file)
    needs_split = size > MAX_BYTES or (dur and dur > a.chunk * 60 * 1.5)
    texts = []
    if needs_split:
        if not shutil.which("ffmpeg"):
            sys.exit("file is large: install ffmpeg so it can be split into chunks")
        with tempfile.TemporaryDirectory() as tmp:
            chunks = split(a.file, a.chunk, tmp)
            for i, c in enumerate(chunks, 1):
                if mean_volume(c) < a.silence_db:
                    print(f"chunk {i}/{len(chunks)}: silent, skipped", file=sys.stderr)
                    continue
                print(f"chunk {i}/{len(chunks)}: transcribing", file=sys.stderr)
                texts.append(clean(transcribe_file(c, key, a.base_url, a.model, a.language, a.prompt)))
    else:
        texts.append(clean(transcribe_file(a.file, key, a.base_url, a.model, a.language, a.prompt)))

    result = "\n\n".join(t for t in texts if t) + "\n"
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"wrote {a.out} ({len(result)} chars)", file=sys.stderr)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
