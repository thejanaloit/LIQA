# LIQA — Live Intelligent QA

**Product:** one Cursor MCP that clones a human Manual QA engineer end-to-end.

## Full Stable V1 (final)

If somebody asks for the **LIQA full stable v1 version chat**, give:

**→ [`artifacts/stable-v1/`](artifacts/stable-v1/)** — entire chat + Perfect-100 lock  
**→ [`artifacts/stable-v1/chat/FULL-CHAT.md`](artifacts/stable-v1/chat/FULL-CHAT.md)** — full readable chat  
**→ [`artifacts/stable-v1/chat/FULL-CHAT.raw.jsonl`](artifacts/stable-v1/chat/FULL-CHAT.raw.jsonl)** — raw transcript  
**→ Tag:** `stable-v1` on this repo

See **[docs/STABLE-V1.md](docs/STABLE-V1.md)**.

**Sigiri Manual steps (locked):** upload Xray steps with headed UI RPA — **no Xray API keys**. See **[docs/XRAY-UI-RPA.md](docs/XRAY-UI-RPA.md)** · MCP `liqa_xray_ui_method` · gold PF-59194.

## Give to other developers (same level)

Other developers must hit the **same smoothness and Book1 quality** as **Perfect-100 PF-59486** (and PF-55248 SHARE) — not a weaker fork.

Doctrine: **[skills/PERFECT-100-PF-59486-GOLD.md](skills/PERFECT-100-PF-59486-GOLD.md)** · MCP `2026-09-16-liqa-perfect-100-v5` · Agency train `2026-09-16-qa-trained-perfect-100-v2`

1. Read **[docs/QUALITY-CONTRACT.md](docs/QUALITY-CONTRACT.md)** (non-negotiable bar)
2. Follow **[docs/DEVELOPER-HANDOVER.md](docs/DEVELOPER-HANDOVER.md)**
3. Sign **[docs/SAME-LEVEL-ACCEPTANCE.md](docs/SAME-LEVEL-ACCEPTANCE.md)**
4. Pack zip: `powershell -File scripts\pack-developer-handover.ps1`
5. Gate: `py -3 -m pytest tests\test_same_level_contract.py -q`

## Industry product (2 QA humans + Workers)

**Status on this device:** see **[docs/COMPLETE.md](docs/COMPLETE.md)** (agency **279** dispatched).

**Do not** run production Manual QA only as Cursor-on-a-laptop.

| Layer | Where | Who |
|-------|--------|-----|
| **Control** | Private VPC / on-prem | 2 QA humans — gates + sign-off UI |
| **Worker VMs** | Windows headed VDI/VM | LIQA execution (Eyes→Brain→Hands) |
| **Studio MCP** | Platform team Cursor | Authoring / gold packs |

Start here: **[docs/INDUSTRY-PRODUCT.md](docs/INDUSTRY-PRODUCT.md)** · **[docs/OPS-MODEL-2QA.md](docs/OPS-MODEL-2QA.md)** · **[docs/DEPLOY-WORKER-VM.md](docs/DEPLOY-WORKER-VM.md)**

```powershell
powershell -File scripts\bootstrap-control.ps1      # Control host
powershell -File scripts\bootstrap-worker-vm.ps1    # each Worker VM
```

```powershell
py -3 scripts\install_liqa_mcp.py   # portable paths per machine
powershell -File scripts\smoke-liqa-mcp.ps1
py -3 -m pytest tests\test_same_level_contract.py tests\test_industry_ops_model.py -q
```

## Feasibility — confirmed

Yes. LIQA is buildable and shipped as:

| Layer | Role |
|-------|------|
| `mcp/server.py` | FastMCP `liqa_*` tools (ISTQB flow, device, Book1, honesty, agency, learner) |
| `apps/worker` | Headed Eyes/Brain/Hands worker (existing LIQA desktop engine) |
| `apps/control` | Local control plane |
| `artifacts/book1-samples` | SHARE gold guards (PF-58374 / PF-55248) |
| `agency-agents` mesh | 250+ specialists via `liqa_agency_*` |

## Start (Cursor)

1. Run: `powershell -File E:\LIQA\scripts\install-liqa-mcp.ps1`
2. Reload MCP in Cursor
3. Say **use LIQA** → agent calls `liqa_boot`

```powershell
cd E:\LIQA
.\scripts\install-liqa-mcp.ps1
.\scripts\smoke-liqa-mcp.ps1
```

## Trigger words

`use LIQA` · `liqa agent` · `liqa mcp`

## Core tools

- Boot: `liqa_boot`, `liqa_laws`, `liqa_todo_list`, `liqa_company_status`
- Task: `liqa_fresh_task`, `liqa_self_assign`, `liqa_orchestrator_assign`
- Agency: `liqa_agency_list`, `liqa_agency_dispatch`, `liqa_mesh_status`
- Learner: `liqa_learn_speed`, `liqa_learn_record`, `liqa_learn_cycle`
- Device: `liqa_capture`, `liqa_click`, `liqa_type`, `liqa_hotkey`, `liqa_browser_open`
- Book1: `liqa_book1_sample`, `liqa_book1_append_row`, `liqa_book1_validate`
- Honesty: `liqa_honesty_start` / `_attempt` / `_verdict`
- Xray Manual steps (UI RPA): `liqa_xray_ui_method`, `liqa_xray_ui_import_csv`, `liqa_xray_ui_import_pack`, `liqa_xray_ui_import_registry`, `liqa_xray_end_of_run_upload`
- Product: `liqa_product_status`, `liqa_resource_map`

## Guards (locked)

- Book1 7 columns + SHARE full-English content method + 100% screenshots
- Honesty-20 before `REAL_BUG`
- Human Gate for OTP/MFA — never invent codes
- Evaluators block share on gold parity fail
- Secrets only under `secrets/` (gitignored)
- Sigiri Manual steps: UI RPA (`liqa_xray_ui_method` / `scripts/README-xray-ui-rpa.md`) — prefer over Xray API keys; never Attachments

## Xray Manual-step upload (no API keys)

Full guide: **[docs/XRAY-UI-RPA.md](docs/XRAY-UI-RPA.md)** · [scripts/README-xray-ui-rpa.md](scripts/README-xray-ui-rpa.md)

```powershell
powershell -File scripts\start-xray-chrome-cdp.ps1
$env:LIQA_CHROME_CDP = "http://127.0.0.1:9333"
# MCP: liqa_xray_end_of_run_upload  |  CLI: py -3 scripts\xray_ui_upload_end_of_run.py upload
```

Wizard: Import → **From csv...** → `#xray-csv-file` → Action\* / Data / Expected Result → Validate → Import Steps. Never Attachments. `force_reset` replaces wrong steps.

## Worker (optional desktop SKU)

See original Worker/Control docs under `docs/`. MCP is the primary Cursor surface.
