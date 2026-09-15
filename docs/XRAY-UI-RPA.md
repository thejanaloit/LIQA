# Xray UI RPA — Sigiri Manual steps (locked)

**No Xray API Keys required.** LIQA uploads `Action,Data,Expected Result` CSVs into Jira Xray Tests with headed Chrome.

Contract id: `xray_csv_wizard_action_star`  
MCP: `liqa_xray_ui_method` · `liqa_xray_ui_import_csv` · `liqa_xray_end_of_run_upload`  
CLI: `scripts/xray_ui_upload_end_of_run.py` · `scripts/start-xray-chrome-cdp.ps1`  
Full ops notes: [scripts/README-xray-ui-rpa.md](../scripts/README-xray-ui-rpa.md)  
Gold: [artifacts/xray-gold-pf59194/](../artifacts/xray-gold-pf59194/) · skill [SIGIRI-MANUAL-STEPS-GUARD.md](../skills/SIGIRI-MANUAL-STEPS-GUARD.md)

## Proven wizard (never Attachments)

1. Prefer CDP: `LIQA_CHROME_CDP=http://127.0.0.1:9333`
2. Open `/browse/{KEY}` → Xray all-in-one iframe
3. **Import** → leaf **From csv...**
4. Dialog `manual-steps-import` → `#xray-csv-file` only
5. Optional replace: **Reset Current Test Steps** (`force_reset=True`)
6. Map **Action\*** / **Data** / **Expected Result**
7. **Validate** → **Import Steps** → wait dialog gone → verify Expected Result in aio
8. Do not press Escape while the dialog is open

## Quick start

```powershell
powershell -File scripts\start-xray-chrome-cdp.ps1
$env:LIQA_CHROME_CDP = "http://127.0.0.1:9333"
py -3 scripts\xray_ui_upload_end_of_run.py method
py -3 scripts\xray_ui_upload_end_of_run.py upload
# replace wrong steps:
py -3 scripts\xray_ui_upload_end_of_run.py pack P01 PF-59477 --force-reset
```

After MCP reload: `liqa_xray_ui_method` then `liqa_xray_end_of_run_upload`.  
Auto-runs on `liqa_complete_phase(7)` and `liqa_learn_cycle`.

## Secrets

- Optional Jira UI login: `secrets/jira-ui-login.json` `{email,password}` (gitignored)
- Optional Xray API: `secrets/xray.env` from `secrets/xray.env.example` (only if Client Id/Secret exist)
- Never invent OTP/MFA — Human Gate
