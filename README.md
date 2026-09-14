# LIQA — Live Intelligent QA

**Product:** one Cursor MCP that clones a human Manual QA engineer end-to-end.

## Give to other developers (same level)

Other developers must hit the **same smoothness and Book1 quality** as PF-55248 SHARE — not a weaker fork.

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
- Product: `liqa_product_status`, `liqa_resource_map`

## Guards (locked)

- Book1 7 columns + SHARE full-English content method + 100% screenshots
- Honesty-20 before `REAL_BUG`
- Human Gate for OTP/MFA — never invent codes
- Evaluators block share on gold parity fail
- Secrets only under `secrets/` (gitignored)

## Worker (optional desktop SKU)

See original Worker/Control docs under `docs/`. MCP is the primary Cursor surface.
