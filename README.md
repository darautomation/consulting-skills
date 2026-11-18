# Consulting Skills for Claude

**Stop writing call notes by hand.** Two open-source Claude skills that handle everything around a client call: the brief before it, the transcript, the recap the client gets, the follow-up, and the progress report before the next session.

Made for people who live on Zoom: coaches, psychologists, therapists, realtors, lawyers, accountants, financial advisors, consultants and agencies.

[Русская версия](README.ru.md) · [Example output](examples/coach-session) · [Pro and done-for-you](#pro-and-done-for-you)

```
Prep  →  Capture  →  Recap  →  Follow-up  →  Results
brief    transcript  client     approved     progress +
60 min   from Zoom,  recap +    message,     next session
before   audio, VTT  CRM note   guarded      agenda
```

## What you get

| Plugin | For | Does |
|---|---|---|
| [**call-copilot**](plugins/call-copilot) | any consultant or helping profession | pre-call brief from calendar, chat, email and public profiles · transcription (Zoom, audio, VTT) · client recap + internal CRM note · follow-up draft with pre-send checks · progress report and next agenda · presets for 6 niches |
| [**advisor-copilot**](plugins/advisor-copilot) | financial advisors, planners, wealth managers | discovery brief · meeting recap with money facts · financial plan draft (goals, cashflow, three buckets, asset location) · 13-meeting service year · annual review |

Niche presets in call-copilot: coach, psychologist / therapist, realtor, lawyer / accountant, financial advisor, general consultant.

## Why it is different

It was extracted from a pipeline that runs every working day in a real advisory practice. The rules come from mistakes that actually happened:

- **Wrong-person guard.** A recap once went to the wrong client. Now every outgoing message is checked: recipient's name must be in the source, no other client's name may appear. `guard_check.py` handles Russian and English name forms.
- **Platform notes go to the client, not an AI rewrite.** The client watched Zoom Notes being written and agreed with them. A fresh AI summary adds new wording and sometimes new facts.
- **Nothing is sent without your "yes".** The skill drafts; you approve.
- **No invented facts.** Gaps become "ask on the call", never guesses. Public profiles count only with two matching signals.
- **Whisper hallucinations filtered.** Silent chunks are skipped; "Thank you for watching!" never lands in a client recap.

## Install

### Claude Code (recommended)

```
/plugin marketplace add darautomation/consulting-skills
/plugin install call-copilot@darautomation
/plugin install advisor-copilot@darautomation
```

Then just ask: *"prep me for my 15:00 call"*, *"transcribe call.m4a and write the recap for Anna"*, *"progress report for Daniel before session 4"*.

### Claude.ai / Claude Desktop

Download `call-copilot.zip` or `advisor-copilot.zip` from [Releases](../../releases) → Settings → Capabilities → Skills → Upload.

### Other agents

The skills follow the open [Agent Skills](https://agentskills.io) format (a folder with `SKILL.md`), so they work in any agent that reads it. Copy `plugins/*/skills/*` into your agent's skills folder.

## Scripts

Python 3.9+, standard library only. Secrets via environment variables.

| Script | Does |
|---|---|
| `vtt_to_text.py` | Zoom / Teams / Meet VTT or SRT → clean speaker transcript |
| `transcribe.py` | audio → text via any OpenAI-compatible Whisper API (Groq, OpenAI, local). Splits long files, skips silence, removes hallucinations |
| `zoom_pull.py` | downloads cloud recordings, transcripts and AI Companion summaries (Zoom Server-to-Server OAuth) |
| `guard_check.py` | pre-send checks: right person, no other clients' names, no placeholders, no AI-tell phrases, length |

## Privacy

Recording and AI processing may need client consent. Therapy, medical and legal niches get stricter defaults: no sensitive content in messengers, local Whisper recommended. See [privacy-consent.md](plugins/call-copilot/skills/call-copilot/references/privacy-consent.md). Never commit recordings or transcripts to git: the included `.gitignore` blocks common audio, video and transcript folders.

## Pro and done-for-you

The open skills work on request, one call at a time. If you want it to run by itself:

| | Free (this repo) | Pro pack | Done-for-you |
|---|---|---|---|
| Brief, recap, follow-up, results on request | ✅ | ✅ | ✅ |
| Niche presets | 6 | 6 + extended scripts per niche | tuned to your practice |
| Calendar watcher: brief arrives 60 min before each call | | ✅ | ✅ |
| Recordings pulled and transcribed automatically | | ✅ | ✅ |
| Recaps queued for one-tap approval in Telegram or email | | ✅ | ✅ |
| Reminder with meeting link, held if the client asked to reschedule | | ✅ | ✅ |
| CRM logging (Google Docs, Notion) and session counters | | ✅ | ✅ |
| Setup on your accounts, your voice, your CRM | | | ✅ |
| Price | free, MIT | from $49 one-time | fixed price, [see site](https://finsave.online/en/ai/) |

**Get Pro or book a setup:** message [@deniscornerstone](https://t.me/deniscornerstone) on Telegram with the words *Call Copilot Pro* (or *Call Copilot setup*). You get payment options for your country; the Pro archive and setup guide arrive right after payment. More about DAR: [finsave.online/en/ai](https://finsave.online/en/ai/)

## About DAR

DAR (Dynamics, Automation, Results) builds AI assistants for small and medium businesses: sales follow-ups, client calls, reporting, content. Same team runs these skills in its own advisory practice every day.

- AI check-up of your business (7 minutes): [finsave.online/ai/check](https://finsave.online/ai/check/?src=github)
- YouTube: [@darautomation](https://www.youtube.com/@darautomation)

## Contributing

New niche presets are the most useful contribution: copy `references/niches/consultant.md`, adapt it to your profession, open a pull request. Bugs and ideas: [Issues](../../issues).

## License

MIT. Use it, change it, sell your services with it.
