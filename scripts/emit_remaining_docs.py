"""Emit remaining product docs in one shot."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs"
ROOT.mkdir(exist_ok=True)

FILES = {}

FILES["OSS-ABSORB.md"] = """# OSS absorb (lawful)

## Stagehand (MIT)
`act` / `extract` / `observe` map to LIQA `click_text` / `type` / screenshot+OCR. Do **not** vendor Playwright as the core Hands. Replay after headed proof only.

## browser-use (MIT)
Agent loop observe → act. LIQA loop is Eyes → Brain JSON → Hands. Same idea, headed Windows pixels.

## AskUI 3-layer
Brain / Hands / worker-on-device. Documented in ARCHITECTURE.md. No source steal.

## Rainforest VM+VNC
Customer watches a real OS. LIQA live view is screenshot poll now; WebRTC H.264 when TURN exists. Interactive = human_gate take-over on the Worker PC.

## BrowserStack Local
Outbound tunnel only. Worker heartbeats out. No inbound bank hole. ICE/TURN outbound in customer VPC.

## Karate on-prem CUA
Keep LLM next to Worker. Reject headless Docker as the manual-QA core.

## Claude computer_toolset
screenshot, left_click, type, zoom → LIQA screenshot, click_text/click_xy(only if seen), type, dpi downscale.

## OpenAI CUA
Screenshot → click loop. We refuse raw x/y unless the control is on the latest PNG (click_text/OCR).

## Cua Windows driver
Background input has compositor limits. LIQA uses the interactive desktop (fail if Session 0).

## Midscene YAML
Optional case format under packs/. Not a replacement for headed proof.

## TQU / void_humanize / ManualQA device_core
Owned Hands engine. Bezier + mss capture.

Do not scrape authenticated proprietary apps.
"""

FILES["LEGAL.md"] = """# MSA + DPA + AUP pointers

- AUP: docs/AUP.md (captcha farms, stuffing, mass accounts forbidden)
- DPA: pixels stay on Worker in bank SKU. Control stores job metadata only.
- MSA: Worker seat + Control tenant + Bank air-gap SKUs. See PRICING.md
- Trademark: "LIQA" search is the customer's counsel job before public launch. This repo is a product name in use internally 2026-09.
- GDPR: PII retention days = LIQA_PII_DAYS (default 14). Wipe: scripts/wipe.ps1
- SOC2: control list in COMPLIANCE.md — not a certified audit.
"""

FILES["PRICING.md"] = """# SKUs

| SKU | What | Price note |
| --- | --- | --- |
| Worker seat | One headed Windows appliance | Per concurrent interactive desktop |
| Control tenant | Jobs, gates, live poll, Excel | Per company |
| Bank air-gap | Local brain, no UAT pixels off-box | Premium |

Not Cursor. Not headless SaaS.
"""

FILES["DEMO.md"] = """# 15-minute headed demo

1. Open http://127.0.0.1:8788/
2. Health pills green (Worker headed).
3. Predict: "Open notepad and type hello" — no click.
4. Run cycle — presence badge, Bezier, proof PNG.
5. Predict a shop task — show payment = human_gate.
6. Show CAPTCHA policy: checkbox click vs pause.
7. Download Book1 CSV.
8. Cancel a job without killing the browser.
"""

FILES["SLA.md"] = """# SLA

- Headed Worker uptime measured on `/health` ok=true (interactive session).
- Human gate SLA default 10 minutes then BLOCKED not FAIL.
- Worker silent > 60s → alert.
- Lock screen / Session 0 → unhealthy (not a breach of click SLA).
"""

FILES["ONBOARDING.md"] = """# Customer onboarding

1. Windows QA PC they own. Autologon runbook. Never-sleep.
2. Chrome/Edge on PATH. Tesseract optional for click_text.
3. `scripts/verify-install.ps1` then `scripts/dev.ps1` or logon task.
4. Vault JSON for maker/checker (gitignored).
5. Jira OAuth when they want story pull — read-only Xray.
6. Format pack: ISTQB default or their templates.
7. Bank FAQ: pixels stay on worker.
"""

FILES["SUPPORT.md"] = """# Support runbook

- Collect `scripts/support-bundle.ps1` (no .env, no vault).
- Check `/health` reasons: LogonUI, Session 0, tiny display.
- RDP: use tscon to console. Disconnect ≠ headed.
- NTP clock skew: enable Windows time service.
- OCR missing: install Tesseract.
- Chrome missing: add to PATH.
"""

FILES["NTP.md"] = """# NTP

Worker vs Control clock skew warning is on. Enable Windows Time (`w32tm /resync`) on the QA PC. Signed URLs expire; skew breaks downloads.
"""

FILES["BANK-FAQ.md"] = """# Bank FAQ — pixels stay on the Worker

Q: Do UAT screenshots leave our network?
A: Bank SKU: no. Brain is local Ollama. Control stores job ids and statuses.

Q: Can Cursor see our UAT?
A: No. Cursor API is a dispatcher. Screenshots are not attached.

Q: MFA?
A: Human gate. We do not invent OTPs or farm CAPTCHAs.

Q: Headless Chrome in Docker?
A: Not this product.
"""

FILES["COMPLIANCE.md"] = """# Compliance

- PII retention: 14 days default. Wipe command provided.
- GDPR DPA template: bank mode = processor does not receive special category screenshots.
- SOC2 mapping (later audit): CC6 access, CC7 monitoring (/metrics), CC8 change (git), P8 privacy (wipe).
- Tenant isolation: hashed API keys, jobs keyed by tenant, signed downloads.
- TLS: terminate at reverse proxy (Caddy/nginx) in front of :8788. mTLS optional Worker↔Control.
- Network policy: Worker egress allowlist = Control URL + UAT + optional Ollama localhost.
- Pentest checklist: docs/PENTEST.md
- Session lock = security event (LogonUI → /health 503 + metrics).
"""

FILES["PENTEST.md"] = """# Pentest checklist

- Worker binds 127.0.0.1; LAN bind requires token.
- No secrets in logs (redact password/otp/token).
- CSRF token on UI mutating calls.
- Signed artifact URLs expire.
- Rate limit job create.
- Captcha-farm endpoints must not exist (grep 2captcha).
- Headless env vars rejected.
"""

FILES["PACKAGING.md"] = """# Packaging

- Inno: packaging/liqa-worker.iss
- Autostart: scripts/register-logon-task.ps1
- Hyper-V/VMware: dedicated VM, GPU/virtual display ≥ 1280x720, autologon, never lock.
- RDP: tscon %SESSIONNAME% 0 after connect so the console stays headed.
- Offline wheels: pip download -r apps/worker/requirements.txt -d wheels/
- Update channel: signed zip + hash in CHANGELOG (customer verifies).
- License key: POST /v1/license
- Uninstall: Inno + optional capture wipe.
"""

FILES["LIVE-VIEW.md"] = """# Live view

Working now: GET http://127.0.0.1:8787/v1/live/frame (screenshot poll, 25fps cap in docs).
UI embeds debugUrl. Presence label LIQA Worker.
WebRTC H.264 publisher + SFU: specified in /v1/live/webrtc — needs TURN outbound.
interactive=true: ACK the human gate then use the real Worker mouse (same PC).
Recording: PNG sequence in captures/; optional ffmpeg to MP4 as artifact.
Blur PII: off by default (future toggle).
Viewer auth: same tenant token as Control.
"""

FILES["REPLAY.md"] = """# Replay after headed proof

trajectories/*.jsonl records proved steps.
Replay is headed-visible only. Headless replay is not a default SKU.
UI drift → screenshot mismatch → invalidate cache → re-enter brain.
"""

FILES["WEBSITE-COPY.md"] = """# Website copy

LIQA is headed manual QA and a full-PC human agent on **your** Windows desktop.
Not Cursor. Not a headless SaaS farm. You watch it click.
"""

FILES["CHANGELOG.md"] = """# Changelog

## 0.1.0 (2026-09-10)
- Local Control :8788 + Worker :8787
- Eyes→Brain→Hands, ManualQA 10, human gates
- Book1 CSV, live screenshot poll, format packs
- General PC playbooks (shop/social/qa/os)
"""

FILES["I18N.md"] = """# i18n

Control GET /v1/i18n returns en + si empty states and live-view labels.
Sinhala NL keywords in intent.py (කඩේ, ෆේස්බුක්, පරීක්ෂණ).
IME type path: POST /v1/hands/ime sinhala=true.
"""

FILES["TLS.md"] = """# TLS / mTLS

Put Caddy or nginx in front of Control :8788 with your certificate.
Worker talks outbound HTTPS to Control.
Optional mTLS: client cert on Worker, verify on proxy.
Local host 127.0.0.1 may stay HTTP.
"""

FILES["NETWORK-POLICY.md"] = """# Worker egress allowlist

- LIQA_CONTROL_URL
- Customer UAT host
- 127.0.0.1:11434 Ollama (bank)
- Optional Atlassian
Deny captcha-farm hosts. Deny inbound.
"""

FILES["RETENTION.md"] = """# PII retention

LIQA_PII_DAYS=14. capture_ops.rotate(keep_hours=days*24).
Customer wipe: scripts/wipe.ps1 and POST /v1/wipe.
"""

FILES["SBOM.md"] = """# SBOM

Generate: `py -m pip freeze > reports/sbom-pip-freeze.txt`
Optional syft/cyclonedx later. Dependabot: .github/dependabot.yml
pip-audit: scripts/pip-audit.ps1
"""

FILES["TRADEMARK.md"] = """# Trademark

Internal product name LIQA (Live Intelligent QA). Public trademark search/filing is legal counsel work — not a git checkbox that grants a mark.
"""

FILES["COOKIE-WIPE.md"] = """# Cookie isolation

Shared appliance: wipe Chrome profile between customers.
scripts/cookie-wipe.ps1 closes nothing mid-job; run only when no session.lock.
"""

FILES["CHROME-PROFILES.md"] = """# Chrome profiles

One process per job. Profile dir under captures/profiles/<tenant> gitignored.
Maker-checker: same process, logout/login in the window.
"""

FILES["OPENTELEMETRY.md"] = """# Traces

JSON logs metrics.jlog('brain') then metrics.jlog('hands') are the span pair.
Export to OTLP later; local files are enough for support bundles.
"""

FILES["ARCHITECTURE-PDF.md"] = """# Procurement PDF

Print docs/ARCHITECTURE.md + VISION.md + BANK-FAQ.md to PDF from the browser (Ctrl+P) or `pandoc`.
"""

FILES["STAGEHAND.md"] = FILES["OSS-ABSORB.md"]

(ROOT / "research").mkdir(exist_ok=True)
for name, body in FILES.items():
    (ROOT / name).write_text(body, encoding="utf-8")
print("wrote", len(FILES), "docs")
