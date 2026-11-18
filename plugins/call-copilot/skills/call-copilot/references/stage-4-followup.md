# Stage 4. Follow-up: draft → approval → send

## Draft

Pick the channel the client actually uses (config `channels` or where the last conversation happened): messenger message is short, email can carry structure.

Messenger:
```
{First name}, here is the recap of today's call.

{client recap from stage 3}

{materials, if the consultant approved them: one line per item with link}
```

Email: subject `Recap {DD.MM}: {topic}`, same body, signature from config.

Tone: the consultant's voice from config (formal/informal address, language). No "Hope you're well", no "Feel free to reach out", no long dashes.

## Pre-send checklist (all must pass)

1. **Right person**: recipient's name is in the source notes; no other client's name, numbers or story in the text. Run `scripts/guard_check.py --to "{First name}" --text draft.md --others clients.txt`.
2. **No placeholders**: no `{...}`, `TODO`, `<name>`, `[insert]`.
3. **Links open**: every link works and is shared "anyone with the link can view" (most common failure: a Google Drive file the client cannot open).
4. **Commitments**: only materials the consultant said "yes" to.
5. **Stop-list**: the client is not on a do-not-contact or hold list; the conversation did not change since the call (client asked to reschedule, cancelled, complained). If it did, do not send, report to the consultant.
6. **Long messages** over ~3500 characters: split at paragraph boundaries.

## Send

Only after an explicit "yes / send / go" from the consultant for this specific message. Then report what went where (channel, time, message id or link). If a send fails, say so plainly with the error; do not retry silently more than once.

## After sending

- Log the send in the CRM note (date, channel).
- If the niche counts sessions, update the counter only from confirmed facts.
