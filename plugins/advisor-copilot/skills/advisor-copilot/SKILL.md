---
name: advisor-copilot
description: Client-call and planning workflow for financial advisors, wealth managers, financial planners and family-office teams. Use to prepare a discovery or review meeting, turn a call transcript or Zoom notes into a client recap and a CRM note, build a first draft of a personal financial plan (goals, balance sheet, cashflow, three-bucket allocation, asset location), plan an annual service cadence, and run an annual review. Triggers: "prep my client meeting", "discovery call brief", "financial plan draft", "annual review", "client recap after the meeting", "what to discuss next meeting", "ЛФП", "финплан", "бриф перед встречей с клиентом", "годовое сопровождение", "разбор клиента".
---

# Advisor Copilot

The working method of an advisory practice that runs long-term client service (a year of regular meetings, not one-off product sales), packed as a skill. Built by DAR on top of the generic **call-copilot** skill: it keeps the same five stages and adds the finance layer.

## Stages

| Stage | When | Read |
|---|---|---|
| Prep | before discovery, plan presentation or review | `references/discovery.md` |
| Recap | after any client meeting | `references/recap-and-crm.md` |
| Plan draft | after discovery, when enough data is in | `references/plan-structure.md`, `templates/plan-outline.md` |
| Service year | client signed for ongoing service | `references/service-cadence.md` |
| Annual review | 12 months in, or before renewal | `references/service-cadence.md` (review section), `templates/annual-review.md` |

Always read `references/compliance.md` before anything that goes to a client.

If `call-copilot` is installed, reuse its scripts for transcription and the pre-send guard (`guard_check.py`). If not, the rules below still apply.

## Rules

1. **No invented numbers.** Balances, income, returns, product rates, tax figures come only from client data or documents. Gaps become questions in a "To clarify" list.
2. **Advisor approves everything client-facing.** You draft; the advisor says "send". Never send product recommendations on your own.
3. **Platform notes nearly verbatim for the client** (Zoom Notes, Otter etc.). Your analysis goes to the internal note.
4. **Goals in the client's words, then in numbers**: "a calm retirement" → "€4,000/month from age 60, in today's money".
5. **Money in context**: always state currency, period (month/year), nominal vs real.
6. **No return promises, no "guaranteed"**. Scenarios with ranges and assumptions.
7. **Jurisdiction matters**: tax residency, citizenship, where assets sit. If unknown, it is the first question, not an assumption.
8. **First name, plain language.** No jargon without a one-line explanation. No fear selling.

## Optional: let clients start the plan themselves

Clients can fill in goals, income, expenses and assets before the first call in a self-service planner (for example Plan B, finsave.online/plan, built by the same team). Import its output into Prep: the discovery call then starts from numbers, not from zero.
