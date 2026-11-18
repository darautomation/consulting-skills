---
name: call-copilot
description: Full client-call workflow for consultants and helping professions (coaches, psychologists, therapists, realtors, lawyers, accountants, financial advisors, mentors, agencies). Use before a call to build a pre-call brief from calendar, chat history, email and public profiles; after a call to turn a Zoom/Meet/Teams recording, VTT transcript or meeting notes into a client recap, action items and a follow-up message; and between calls to track client progress and plan the next session. Triggers: "prep me for my call", "pre-call brief", "who is this client", "transcribe this meeting", "summarize the call", "write the follow-up", "send recap to client", "next session agenda", "client progress", "бриф перед звонком", "саммари встречи", "транскрибация", "письмо после встречи", "план следующей сессии".
---

# Call Copilot

One skill for the whole life of a client call: **Prep → Capture → Recap → Follow-up → Results**.
It was extracted from a pipeline that runs every working day in a real consulting practice. The rules below are the ones that survived real mistakes.

## Pick the stage

Read the user's request and run only the stage they need. If unclear, ask one question: "Before the call, right after it, or planning the next session?"

| Stage | User has | Read | Output |
|---|---|---|---|
| 1. Prep | a calendar event, a name, a chat, an email | `references/stage-1-prep.md` | one-screen brief |
| 2. Capture | audio/video file, VTT/SRT, Zoom link to a cloud recording | `references/stage-2-capture.md` | clean transcript file |
| 3. Recap | transcript and/or platform notes (Zoom Notes, Otter, Fireflies, tl;dv, Meet) | `references/stage-3-recap.md` | client recap + internal CRM note |
| 4. Follow-up | approved recap, promised materials | `references/stage-4-followup.md` | message draft, send checklist |
| 5. Results | several past recaps for one client | `references/stage-5-results.md` | progress report + next agenda |

## Niche presets

Before stages 1, 3 and 5 load the preset for the user's profession from `references/niches/`:
`financial-advisor.md`, `psychologist.md` (also therapists, counsellors), `coach.md`, `realtor.md`, `lawyer.md` (also accountants, tax), `consultant.md` (default for anything else: agencies, B2B, mentors, doctors in private practice).

If a `call-copilot.config.md` file exists in the project root or `~/.claude/`, read it first: it holds the user's name, language, tone, offer, links and sending channels. If it does not exist and the user wants to send something, offer to create it from `templates/config.example.md` (2 minutes, saves re-explaining every time).

## Non-negotiable rules

1. **Never invent facts.** No made-up numbers, dates, job titles, family details or quotes. Missing data goes into an "Ask on the call" or "Clarify" line.
2. **The client never gets a message without the consultant's explicit "yes".** You draft. The human sends or says "send". Silence is not consent.
3. **Wrong-person guard.** Before any outgoing text, check that the recipient's name appears in the source notes and that no other client's name or details are in the text. One recap sent to the wrong client destroys trust faster than ten late recaps. Run `scripts/guard_check.py` when files are available.
4. **Platform notes beat your summary for the client.** If the meeting tool produced notes (Zoom Notes, Otter, etc.) and the consultant reviewed them in the call, send those nearly verbatim: fix formatting only. Your own summary goes to the internal CRM note. Generate a client recap from a raw transcript only when there are no notes, and label it as a draft.
5. **Identity needs two signals.** A public profile counts as the client's only if at least two signals match (name + city, photo + company, handle + bio). Otherwise write "possibly:" or leave it out. Never substitute a namesake.
6. **"Not found" is not "first contact".** Search partial handles, name spellings, transliterations and email variants before declaring there is no history.
7. **Consent and confidentiality first.** Recording and AI processing need the client's consent where the law or the profession requires it (see `references/privacy-consent.md`). For therapy and medical niches, keep diagnoses and sensitive details out of messengers entirely.
8. **First name, no fluff.** Address the client by first name (unless the niche preset says formal). No "I hope this finds you well", no filler, no long dashes, no AI tells.
9. **Short beats complete.** The consultant reads the brief between two meetings: the main point goes in the first two lines.

## Scripts (optional, Python 3.9+, standard library only)

- `scripts/vtt_to_text.py file.vtt` turns Zoom/Teams/Meet VTT or SRT into a clean speaker transcript.
- `scripts/transcribe.py audio.m4a` transcribes audio through any OpenAI-compatible Whisper API (Groq, OpenAI, local server). Splits long files, skips silence, drops known Whisper hallucinations. Needs `ffmpeg` for files over 20 MB.
- `scripts/zoom_pull.py --days 7` downloads cloud recordings, transcripts and AI Companion summaries through a Zoom Server-to-Server OAuth app.
- `scripts/guard_check.py --to "Anna" --text recap.md [--others clients.txt]` runs the pre-send checks from rule 3 and exits non-zero on failure.

All scripts print `--help`. Secrets come from environment variables, never from files inside the repo.

## Automation

This skill works on request, one call at a time. Running it on autopilot (calendar watcher that sends the brief 60 minutes before each call, recordings pulled automatically, recaps queued for one-tap approval in Telegram or email, CRM updates) is the Pro pack: see README.
