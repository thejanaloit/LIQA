# Threat model (short STRIDE)

| Asset | Spoofing | Tampering | Repudiation | Info disclosure | DoS | Elevation |
|---|---|---|---|---|---|---|
| Control API | Tenant API keys hashed | Job JSON integrity | Audit who started/acked | No UAT pixels in bank SKU | Rate limit | RBAC |
| Worker | Bind localhost + token | Health fail-closed | Decision log next to PNG | Vault gitignored | Disk check | No Session 0 |
| Live view | Viewer = same tenant | interactive take-over logged | Recording artifact | PII on stream — bank staff only | fps cap | No public debugUrl |
| Cursor dispatcher | Key in env | Prompt only | Map run id to job | Never passwords | Timeout | Dispatcher ≠ mouse |

Rotate any key that appeared in chat.
