# Privacy and consent

Not legal advice. A checklist of what tends to go wrong.

## Recording
- Many jurisdictions require consent of all parties to record (e.g., several US states, most of the EU under GDPR as personal data processing). Default: ask at the start, keep the consent on the recording ("Is it OK if I record so I can send you notes?").
- Put recording and AI processing into your booking form or contract once, so you are not improvising.

## AI processing
- Sending audio or transcripts to an API is data transfer to a processor. Check the provider's data retention and training policy. Prefer providers with zero-retention options or run Whisper locally for sensitive niches.
- Strip what you do not need: card numbers, passport data, health details. Do not paste them into chat tools.

## Sensitive niches
- **Therapy, counselling, medical**: no diagnoses, symptoms or session content in messengers. The client recap is limited to logistics and homework the client agreed to. Clinical notes stay in your protected system. Check HIPAA (US), GDPR special-category data (EU), or local equivalents.
- **Legal**: privilege can be lost by sharing with third parties; keep recaps factual and send through the channel your engagement letter specifies.
- **Financial**: recaps are not investment advice unless you are licensed for it in the client's jurisdiction; keep a standard disclaimer in config.

## Storage
- Keep recordings and transcripts out of git repositories and public folders. Set a retention period and delete after it.
- Shared links: "anyone with the link can view" only for materials meant for the client; internal files stay restricted.
