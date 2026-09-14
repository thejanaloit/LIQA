# Support runbook

- Collect `scripts/support-bundle.ps1` (no .env, no vault).
- Check `/health` reasons: LogonUI, Session 0, tiny display.
- RDP: use tscon to console. Disconnect ≠ headed.
- NTP clock skew: enable Windows time service.
- OCR missing: install Tesseract.
- Chrome missing: add to PATH.
