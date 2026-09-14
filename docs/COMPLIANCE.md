# Compliance

- PII retention: 14 days default. Wipe command provided.
- GDPR DPA template: bank mode = processor does not receive special category screenshots.
- SOC2 mapping (later audit): CC6 access, CC7 monitoring (/metrics), CC8 change (git), P8 privacy (wipe).
- Tenant isolation: hashed API keys, jobs keyed by tenant, signed downloads.
- TLS: terminate at reverse proxy (Caddy/nginx) in front of :8788. mTLS optional Worker↔Control.
- Network policy: Worker egress allowlist = Control URL + UAT + optional Ollama localhost.
- Pentest checklist: docs/PENTEST.md
- Session lock = security event (LogonUI → /health 503 + metrics).
