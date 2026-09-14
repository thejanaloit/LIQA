# LIQA Product — Final Output

**Date:** 2026-09-14  
**Product name:** LIQA (Live Intelligent QA)  
**Home:** `E:\LIQA`  
**Cursor MCP key:** `liqa`  
**Entry:** `E:\LIQA\mcp\server.py`

## Feasibility answer

**Yes — possible.** LIQA is a real Cursor FastMCP that clones the Manual QA engineer flow proven on PF-55248 / PF-59194, absorbs ManualQA-Agent + QAFusionX learnings + agency-agents specialists, and keeps Worker/Control as the headed desktop engine.

## What shipped

1. **MCP surface (`liqa_*`)** — ISTQB 7-phase company flow, device Eyes→Brain→Hands, Book1 SHARE guards, honesty-20, Human Gate, orchestrator roles.
2. **Agency mesh** — indexes ~279 specialists from `E:\agency-agents\.cursor\rules` via `liqa_agency_list` / `liqa_agency_dispatch`.
3. **Learner** — every round records into `skills/SPEED-PLAYBOOK.md` via `liqa_learn_speed` / `liqa_learn_cycle`.
4. **Resource map** — ManualQA-Agent, QAFusionX, agency-agents, Worker, Control.
5. **Book1 gold** — PF-58374 SHARE + PF-55248 SHARE samples under `artifacts/book1-samples/`.
6. **Install script** — `scripts/install-liqa-mcp.ps1` writes Cursor `mcp.json`.

## How to use

```text
use LIQA
```

Agent must: `liqa_boot` → `liqa_fresh_task` → `liqa_self_assign` → ISTQB 1→7.  
Ask human only on real blockers (OTP/MFA/missing data). Otherwise finish full QA.

## Guards (same bar as PF-55248 SHARE)

- Columns: Area | Issue | Screenshot | What is testing | Why that failed your prediction | 2nd QA confirmation | Simple explanation
- Full English content method (not labels)
- 100% screenshot coverage
- Evaluator blocks share on gold parity fail
- Honesty-20 before REAL_BUG

## Non-goals / honest limits

- LIQA does **not** invent OTP codes.
- SSO splash-only login may require Human Gate.
- Jira write still uses Atlassian MCP with the user's account.
- Cursor cloud agents cannot click this Windows desktop — Worker/local MCP does.

## Deploy checklist

- [x] MCP server with liqa_* tools
- [x] Persona + laws + Book1 contract
- [x] Agency mesh + learner
- [x] Install script for Cursor
- [x] Smoke script
- [x] **Same-level handover for other developers**
  - `docs/QUALITY-CONTRACT.md`
  - `docs/DEVELOPER-HANDOVER.md`
  - `docs/SAME-LEVEL-ACCEPTANCE.md`
  - `tests/test_same_level_contract.py` (must be green)
  - `scripts/pack-developer-handover.ps1` → `packaging/out/LIQA-developer-handover-*.zip`
- [ ] Each new developer: reload MCP + sign acceptance checklist

## Industry productization (2 QA + Workers)

- [x] `docs/INDUSTRY-PRODUCT.md` — SKU + topology
- [x] `docs/OPS-MODEL-2QA.md` — human daily loop
- [x] `docs/DEPLOY-WORKER-VM.md` — Windows Worker VM blueprint
- [x] Control 2QA console APIs: `/v1/ops/summary`, gate resolve, job sign-off
- [x] `scripts/bootstrap-control.ps1` / `bootstrap-worker-vm.ps1`
- [x] `tests/test_industry_ops_model.py`

**Best method:** dedicated **Windows headed Worker VMs/VDI** + **Control** for the 2 humans — not headless Linux Docker, not Cursor Cloud alone.