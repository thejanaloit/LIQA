# SLA

- Headed Worker uptime measured on `/health` ok=true (interactive session).
- Human gate SLA default 10 minutes then BLOCKED not FAIL.
- Worker silent > 60s → alert.
- Lock screen / Session 0 → unhealthy (not a breach of click SLA).
