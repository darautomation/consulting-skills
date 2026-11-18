#!/usr/bin/env python3
"""Convert a VTT or SRT transcript (Zoom, Teams, Google Meet, Whisper) into clean text.

Merges consecutive cues from the same speaker, strips timestamps, cue numbers and
inline tags. Keeps a [mm:ss] marker at each speaker change so quotes can be found.

Usage:
  python3 vtt_to_text.py meeting.vtt                 # prints to stdout
  python3 vtt_to_text.py meeting.vtt -o transcript.txt
  python3 vtt_to_text.py meeting.srt --no-times
"""
import argparse
import re
import sys

TIME_RE = re.compile(r"(\d{1,2}:)?(\d{1,2}):(\d{2})[.,](\d{1,3})\s*-->")
TAG_RE = re.compile(r"<[^>]+>")
VOICE_RE = re.compile(r"^<v\s+([^>]+)>")
SPEAKER_RE = re.compile(r"^([^:]{1,60}):\s+(.*)$")


def parse(text):
    cues = []
    cur_time = None
    for raw in text.splitlines():
        line = raw.strip("﻿").strip()
        if not line or line == "WEBVTT" or line.startswith(("NOTE", "STYLE", "Kind:", "Language:")):
            continue
        m = TIME_RE.search(line)
        if m:
            h = int((m.group(1) or "0:")[:-1])
            cur_time = h * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            continue
        if line.isdigit():
            continue
        speaker = None
        vm = VOICE_RE.match(line)
        if vm:
            speaker = vm.group(1).strip()
        line = TAG_RE.sub("", line).strip()
        if not speaker:
            sm = SPEAKER_RE.match(line)
            if sm and not sm.group(1).strip().startswith("http"):
                speaker, line = sm.group(1).strip(), sm.group(2).strip()
        if line:
            cues.append((cur_time or 0, speaker, line))
    return cues


def merge(cues, with_times=True):
    out = []
    last_speaker = object()
    buf = []
    for t, spk, line in cues:
        if spk != last_speaker and buf:
            out.append(" ".join(buf))
            buf = []
        if spk != last_speaker:
            stamp = f"[{t // 60:02d}:{t % 60:02d}] " if with_times else ""
            buf.append(f"{stamp}{spk + ': ' if spk else ''}{line}")
            last_speaker = spk
        else:
            if not buf or not buf[-1].endswith(line):  # drop exact rolling-caption repeats
                buf.append(line)
    if buf:
        out.append(" ".join(buf))
    return "\n\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("-o", "--out")
    ap.add_argument("--no-times", action="store_true", help="omit [mm:ss] markers")
    a = ap.parse_args()
    with open(a.file, encoding="utf-8", errors="replace") as f:
        result = merge(parse(f.read()), with_times=not a.no_times)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"wrote {a.out} ({len(result)} chars)", file=sys.stderr)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
