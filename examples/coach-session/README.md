# Example: coaching session, end to end

Fictional data. Shows what call-copilot produces at each stage.

| File | Stage | What it is |
|---|---|---|
| `meeting.vtt` | input | Zoom transcript (VTT) of a 45-minute session |
| `notes.txt` | input | Zoom Notes written during the call |
| `output/brief.md` | 1. Prep | brief the coach read 60 minutes before |
| `output/transcript.txt` | 2. Capture | `python3 scripts/vtt_to_text.py meeting.vtt` |
| `output/recap.md` | 3-4. Recap | message the client received after the coach said "send" |
| `output/crm-note.md` | 3. Recap | internal note, never sent |
| `output/progress.md` | 5. Results | progress report before session 4 |
