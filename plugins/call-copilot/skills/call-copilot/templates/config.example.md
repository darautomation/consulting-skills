# call-copilot.config.md
# Copy to your project root or ~/.claude/call-copilot.config.md and fill in.
# The skill reads this before every stage. Never put passwords or API keys here.

name: Anna Smith
profession: coach            # financial-advisor | psychologist | coach | realtor | lawyer | consultant
language: en                 # language for briefs and recaps
client_address: informal     # informal | formal
timezone: Europe/Berlin

offer:
  main: 3-month coaching program, 12 sessions
  price: 1800 EUR
  next_step_default: book the kickoff session

links:
  booking: https://cal.com/your-link
  materials_folder: https://drive.google.com/...   # shared "anyone with the link"

channels:                    # where recaps go, in order of preference
  - telegram
  - email

signature: |
  Anna

disclaimer: ""               # e.g. "This is not investment advice."

style:
  banned_phrases: ["hope you're well", "feel free to reach out", "just checking in"]
  max_message_chars: 3500

lists:
  clients_file: ./clients.txt        # one client name per line, used by the wrong-person guard
  do_not_contact: ./do_not_contact.txt
