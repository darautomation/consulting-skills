#!/usr/bin/env python3
"""Download Zoom cloud recordings, transcripts and AI Companion summaries.

Creates one folder per meeting:
  calls/2026-03-14_1530_weekly-session-anna/
    meta.json         topic, start, duration, participants count, share link
    transcript.txt    from Zoom's VTT (speaker-labelled), if Zoom transcribed
    audio.m4a         only with --audio (for transcribe.py when no VTT exists)
    ai_summary.txt    AI Companion meeting summary, if enabled (internal use)

Setup (once, 5 minutes):
  1. marketplace.zoom.us → Develop → Build App → Server-to-Server OAuth.
  2. Scopes: cloud_recording:read:list_user_recordings:admin (or :master),
     cloud_recording:read:recording:admin, meeting:read:summary:admin.
  3. Export credentials as environment variables:
       ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET

Usage:
  python3 zoom_pull.py --days 7 --out ./calls
  python3 zoom_pull.py --days 30 --audio --user me
Already downloaded meetings are skipped.
"""
import argparse
import base64
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vtt_to_text import merge, parse  # noqa: E402

API = "https://api.zoom.us/v2"


def token():
    acc, cid, sec = (os.environ.get(k) for k in ("ZOOM_ACCOUNT_ID", "ZOOM_CLIENT_ID", "ZOOM_CLIENT_SECRET"))
    if not all((acc, cid, sec)):
        sys.exit("set ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET (see --help)")
    req = urllib.request.Request(
        "https://zoom.us/oauth/token?" + urllib.parse.urlencode({"grant_type": "account_credentials", "account_id": acc}),
        method="POST",
    )
    req.add_header("Authorization", "Basic " + base64.b64encode(f"{cid}:{sec}".encode()).decode())
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


def get(tok, path, params=None):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code in (400, 404):
            return None
        raise


def download(tok, url, dest):
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(url + sep + "access_token=" + tok)
    with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)


def uuid_path(u):
    # Zoom requires double URL-encoding for UUIDs that start with / or contain //
    return urllib.parse.quote(urllib.parse.quote(u, safe=""), safe="")


def slug(s):
    s = re.sub(r"[^\w\s-]", "", s.lower(), flags=re.U)
    return re.sub(r"[\s_-]+", "-", s).strip("-")[:50] or "meeting"


def summary_text(s):
    if not s:
        return ""
    parts = [s.get("summary_title") or "", s.get("summary_overview") or ""]
    for d in s.get("summary_details") or []:
        parts.append(f"## {d.get('label', '')}\n{d.get('summary', '')}")
    if s.get("next_steps"):
        parts.append("## Next steps\n" + "\n".join(f"- {x}" for x in s["next_steps"]))
    return "\n\n".join(p for p in parts if p.strip()).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--out", default="./calls")
    ap.add_argument("--user", default="me", help="Zoom user id or email (default: me)")
    ap.add_argument("--audio", action="store_true", help="also download audio when there is no transcript")
    a = ap.parse_args()

    tok = token()
    to = dt.date.today()
    frm = to - dt.timedelta(days=a.days)
    os.makedirs(a.out, exist_ok=True)
    meetings, next_token = [], ""
    while True:
        params = {"from": frm.isoformat(), "to": to.isoformat(), "page_size": 100}
        if next_token:
            params["next_page_token"] = next_token
        page = get(tok, f"/users/{a.user}/recordings", params) or {}
        meetings += page.get("meetings", [])
        next_token = page.get("next_page_token")
        if not next_token:
            break

    new = 0
    for m in meetings:
        start = m.get("start_time", "")[:16].replace("T", "_").replace(":", "")
        folder = os.path.join(a.out, f"{start}_{slug(m.get('topic', ''))}")
        if os.path.exists(os.path.join(folder, "meta.json")):
            continue
        os.makedirs(folder, exist_ok=True)
        files = m.get("recording_files", [])
        vtt = next((f for f in files if f.get("file_type") == "TRANSCRIPT"), None)
        if vtt:
            tmp = os.path.join(folder, "transcript.vtt")
            download(tok, vtt["download_url"], tmp)
            with open(tmp, encoding="utf-8", errors="replace") as f:
                text = merge(parse(f.read()))
            with open(os.path.join(folder, "transcript.txt"), "w", encoding="utf-8") as f:
                f.write(text)
        elif a.audio:
            aud = next((f for f in files if f.get("file_type") == "M4A"), None)
            if aud:
                download(tok, aud["download_url"], os.path.join(folder, "audio.m4a"))
        summ = summary_text(get(tok, f"/meetings/{uuid_path(m['uuid'])}/meeting_summary"))
        if summ:
            with open(os.path.join(folder, "ai_summary.txt"), "w", encoding="utf-8") as f:
                f.write(summ + "\n")
        meta = {
            "topic": m.get("topic"),
            "start_time": m.get("start_time"),
            "duration_min": m.get("duration"),
            "share_url": m.get("share_url"),
            "has_transcript": bool(vtt),
            "has_ai_summary": bool(summ),
            "zoom_uuid": m.get("uuid"),
        }
        with open(os.path.join(folder, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        new += 1
        print(f"saved {folder}", file=sys.stderr)
    print(f"{len(meetings)} meetings found, {new} new", file=sys.stderr)


if __name__ == "__main__":
    main()
