# Cursor API — dispatcher only (T080–T087)

Cursor Cloud Agents can **queue work**. They do **not** click this Windows desktop.

- `CURSOR_API_KEY` lives in local `.env` only. Never commit. Keys pasted in chat are leaked — rotate.
- Worker `POST /v1/cursor/dispatch` forwards a prompt. Timeouts apply.
- Bank SKU: do not attach UAT screenshots to Cursor.
- Cursor computer-use in the cloud is macOS/Linux. LIQA Hands are **this Windows Worker**.
- Map Cursor run status to a LIQA job later (`docs/TODO.md` T083). Until then, treat dispatch as fire-and-forget with a note on the job.
- Prefer a service-account / Enterprise API key over a personal user key in production.
