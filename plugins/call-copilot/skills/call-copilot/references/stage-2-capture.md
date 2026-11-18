# Stage 2. Capture: recording → transcript

Goal: a clean, speaker-labelled text file next to the recording, ready for stage 3.

## Choose the source (best first)

1. **Platform notes** written during the call (Zoom Notes / AI Companion, Otter, Fireflies, tl;dv, Google Meet notes, Teams recap). Save them as `notes.txt`. They become the client recap in stage 3.
2. **Platform transcript** (Zoom cloud VTT, Teams/Meet VTT). Convert: `python3 scripts/vtt_to_text.py meeting.vtt -o transcript.txt`.
3. **Audio/video file** without transcript. Transcribe: `python3 scripts/transcribe.py call.m4a -o transcript.txt --language en`.
4. **Zoom cloud recordings** in bulk: `python3 scripts/zoom_pull.py --days 7 --out ./calls` (needs a Zoom Server-to-Server OAuth app, see script `--help`). Creates one folder per meeting with `transcript.txt`, `ai_summary.txt` when Zoom produced one, and `meta.json`.

## Folder convention

```
calls/2026-03-14_anna-k/
  meta.json        # date, topic, duration, participants, recording link
  notes.txt        # platform notes (client-facing source)
  transcript.txt   # full text (internal source)
  ai_summary.txt   # long platform summary (internal only)
```

## Transcription settings that matter

- Language: set it explicitly (`--language ru`, `en`, `de`). Auto-detect fails on short or mixed calls.
- Long calls: the script splits into 10-minute chunks so a failed chunk loses 10 minutes, not the call.
- Silence: Whisper invents text on silent audio ("Thank you for watching!", "Subtitles by..."). The script skips silent chunks and drops known hallucination lines. Still skim the start and end.
- Names and jargon: pass `--prompt "Anna, Kowalski, ETF, mortgage pre-approval"` to bias spelling.

## Privacy

Before uploading audio to any API, check `references/privacy-consent.md`. For therapy, medical and legal calls prefer a local Whisper server (`--base-url http://localhost:8000/v1`) so audio never leaves the machine.
