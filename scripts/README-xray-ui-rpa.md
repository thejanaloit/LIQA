# Xray UI RPA — end-of-run Manual step upload

**No Xray API Keys required.** Headed Chrome uploads `Action,Data,Expected Result` CSVs into Jira Tests via the Xray all-in-one **Import → From csv...** wizard.

Contract id: `xray_csv_wizard_action_star` (see `liqa_xray_ui_method` / `mcp/xray_ui_import.py` `PROVEN_UI_METHOD`).

## Proven method (locked 2026-09-15)

Never use Jira **Attachments**. Never treat pre-existing aio steps as success before clicking **Import Steps**.

1. Prefer CDP Chrome: `LIQA_CHROME_CDP=http://127.0.0.1:9333` (`scripts/start-xray-chrome-cdp.ps1`)
2. Login: `secrets/jira-ui-login.json` `{email,password}` (gitignored) — never invent OTP/MFA
3. Open `/browse/{KEY}` → scroll → Xray all-in-one iframe → Test details
4. Empty: button **Import**. Filled: icon menu right of **Add Step**
5. Leaf menuitem text exactly **`From csv...`**
6. Dialog iframe `src` contains `manual-steps-import`
7. Set files on **`#xray-csv-file`** only (`name=csvFile`, `accept=.csv`)
8. Optional replace: click visible label **`Reset Current Test Steps`** (`force_reset=True`)
9. **Next** → Map Fields react-select → **Action\*** / **Data** / **Expected Result** (never Call Test)
10. **Validate** → click **Import Steps** → wait until `manual-steps-import` iframe is **gone** → verify Expected Result in aio
11. Do **not** press Escape while the import dialog is open

CSV columns: `Action,Data,Expected Result` (Sigiri PF-59194 gold).

## Preferred (stable session): CDP Chrome

```powershell
powershell -File E:\LIQA\scripts\start-xray-chrome-cdp.ps1
# Log into Jira in that Chrome window (OTP yourself)
$env:LIQA_CHROME_CDP = "http://127.0.0.1:9333"
py -3 E:\LIQA\scripts\xray_ui_upload_end_of_run.py upload
```

Leave that Chrome open for the whole LIQA run. End-of-run hooks reuse `LIQA_CHROME_CDP` when set.

## Alternate: Playwright persistent profile

```powershell
py -3 E:\LIQA\scripts\xray_ui_upload_end_of_run.py login
py -3 E:\LIQA\scripts\xray_ui_upload_end_of_run.py upload
```

Profile: `E:\LIQA\workspace\default-run\.chrome-xray-ui-import` (gitignored)

## Auto hooks (LIQA MCP)

After MCP reload:

- `liqa_xray_ui_method` → print locked contract
- `liqa_complete_phase(7)` → `end_of_run_upload_registry`
- `liqa_learn_cycle` → same
- Manual: `liqa_xray_end_of_run_upload` / `liqa_xray_ui_ensure_login`
- Replace wrong steps: `liqa_xray_ui_import_csv(..., force_reset=True)`

## Single pack

```powershell
$env:LIQA_CHROME_CDP = "http://127.0.0.1:9333"
py -3 E:\LIQA\scripts\xray_ui_upload_end_of_run.py pack P01 PF-59477
```

## Force reset (wrong steps already in Test)

```text
liqa_xray_ui_import_csv(issue_key="PF-59477", csv_path=".../P01-steps.csv", force_reset=True)
```

Clicks **Reset Current Test Steps** then re-imports.