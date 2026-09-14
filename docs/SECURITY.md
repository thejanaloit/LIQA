# SECURITY

- Never commit `.env`, vault JSON, captures with PII, or API keys.
- Keys pasted in chat are **compromised**: rotate in Cursor Dashboard → API Keys, then update local `.env` only.
- Worker binds `127.0.0.1` by default. LAN bind requires `LIQA_WORKER_TOKEN`.
- Bank SKU: screenshots stay on the Worker. Do not send UAT pixels to Cursor Cloud Agents or public LLMs.
- Cursor API is a **dispatcher**. It does not receive passwords.
- Captcha farms, OTP invention, and mass account creation are **out of product**.
- Visible “I’m not a robot” may be clicked if it is on the latest screenshot. Hard puzzles / SMS / Google 2FA wait for a human ACK.
- Rotate procedure: Dashboard → revoke leaked key → new key only in `.env` → restart Worker. Never paste the new key into chat or git.
