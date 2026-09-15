# SIGIRI Manual Steps Guard — LIQA (locked 2026-09-15)

Owner doctrine (English):

1. Convert Sinhala instructions to English first.
2. When generating test cases, **split into path parts**.
3. Identify parts by reading the user story and mapping distinct UI paths.
4. Write steps **exactly** like SIGIRI JAYASEKARA on PF-59194:
   - Columns: **Action | Data | Expected Result**
   - Extremely simple, direct English
   - Not even a decimal of difference from that structure
5. LIQA MCP enforces this with guard tools — nothing ships to Jira without a pass.

## Tools

| Tool | Purpose |
|------|---------|
| `liqa_sigiri_laws` | Print locked laws |
| `liqa_xray_gold_steps` | Load PF-59194 gold CSV |
| `liqa_xray_split_paths` | Story → path parts |
| `liqa_xray_validate_steps` | Guard before upload |
| `liqa_xray_build_manual_test` | CSV+MD pack after pass |
| `liqa_xray_validate_title` | Pipe taxonomy guard |
| `liqa_save_new_testcase` | Blocks bad Manual tables |
| `liqa_xray_credentials_status` | Check Xray API keys |
| `liqa_xray_set_credentials` | Save Client Id/Secret to `secrets/xray.env` |
| `liqa_xray_ui_import_csv` | **RPA** headed Chrome Import (no API keys); `force_reset` replaces steps |
| `liqa_xray_ui_import_pack` | RPA import one pack |
| `liqa_xray_ui_import_registry` | RPA import all packs |
| `liqa_xray_ui_method` | Print locked wizard contract (`xray_csv_wizard_action_star`) |
| `liqa_xray_ui_ensure_login` | One-time Jira login in persistent Chrome |
| `liqa_xray_end_of_run_upload` | **Auto** on phase 7 / learn_cycle — upload all packs |
| `liqa_xray_upload_after_run` | API if keys exist, else RPA |

## Import (inbuilt)

**Preferred without admin API keys:** headed UI RPA — **no Xray API Keys page**. Full method: `scripts/README-xray-ui-rpa.md` + `liqa_xray_ui_method`.

Proven wizard (never Attachments):

1. Import → leaf **From csv...** → `#xray-csv-file`
2. Optional **Reset Current Test Steps** (`force_reset=True`)
3. Map **Action\*** / **Data** / **Expected Result**
4. Validate → **Import Steps** → wait dialog gone → verify aio

Agent steps:

1. Reload LIQA MCP  
2. One-time: `liqa_xray_ui_ensure_login` or  
   `py -3 E:\LIQA\scripts\xray_ui_upload_end_of_run.py login`  
3. Upload all: `liqa_xray_end_of_run_upload` or  
   `py -3 E:\LIQA\scripts\xray_ui_upload_end_of_run.py upload`  
4. **Every run end:** `liqa_complete_phase(7)` and `liqa_learn_cycle` auto-call the RPA uploader  

Optional API path (only if Client Id/Secret ever exist): `liqa_xray_set_credentials` then `liqa_xray_import_csv`.

## Gold

- Story: PF-55248
- Test: PF-59194
- CSV: `artifacts/xray-gold-pf59194/PF-59194-steps.csv`
