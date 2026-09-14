# LIQA Worker (headed)

Windows interactive session only. Session 0 / locked screen → `/health` 503.

## Autologon + never-sleep (customer checklist)

1. Dedicated QA PC or VM **you own**.
2. User auto-logon (or stay logged in). Disable lock screen for that account if policy allows.
3. Power plan: never sleep, never turn off display while a job runs.
4. Chrome or Edge installed and on PATH.
5. Start Worker at logon (Task Scheduler: `py E:\LIQA\apps\worker\api.py`).
6. If you RDP: disconnect with `tscon` to console, or Worker reports unhealthy.

## Laws

- One browser. Entry URL once. Then mouse + keyboard only.
- Bezier move before click.
- Hard CAPTCHA / SMS / Google 2FA → human gate.
- Visible “I’m not a robot” checkbox may be clicked if it is on the latest screenshot.

## Endpoints

- `GET /health` `GET /v1/status` `GET /v1/jobs` `GET /v1/version`
- `POST /v1/hands/*` screenshot, click_text, click, type, wait, wait_frame, presence, calibrate, focus, hotkey
- `POST /v1/predict` natural language → ManualQA 10-step plan
- `POST /v1/run` one Eyes→Brain→Hands cycle
- `POST /v1/gates` + `/v1/gates/{id}/ack`
- `POST /v1/heartbeat` outbound to Control
- `POST /v1/cursor/dispatch` dispatcher only
