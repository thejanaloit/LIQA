# LIQA — COMPLETE on this device

**Status:** COMPLETE (industry product pack ready on-device)  
**Date:** 2026-09-14  
**Model:** 2 QA humans + LIQA Workers execute almost all Manual QA  

## Orchestration

- Agency specialists indexed: **279**
- Mass-dispatched into mesh workstreams: **279**
- Core delivery cell: orchestrator, SPM, multi-agent architect, workflow, PM, evidence, reality-checker, test-results, tech-writer, devops, backend, frontend, security, SRE, code-reviewer

Catalog: `packaging/industry/agency-catalog.json`  
Assignments: `workspace/default-run/agents/mesh/assignments.jsonl`

## Product surfaces (all present)

| Surface | Path | Role |
|---------|------|------|
| Cursor MCP | `mcp/server.py` (`liqa_*`, ≥70 tools) | Studio / authoring |
| Control | `apps/control/server.py` :8788 | 2QA gates + sign-off |
| Worker | `apps/worker/api.py` :8787 | Headed Eyes→Brain→Hands |
| Book1 gold | `artifacts/book1-samples/` | SHARE parity |
| Quality bar | `docs/QUALITY-CONTRACT.md` | Same-level |
| Industry | `docs/INDUSTRY-PRODUCT.md` | Deploy topology |
| Ops 2QA | `docs/OPS-MODEL-2QA.md` | Human daily loop |
| Worker VM | `docs/DEPLOY-WORKER-VM.md` | VM blueprint |

## Verify on this device

```powershell
cd E:\LIQA
pip install -r requirements.txt
powershell -File scripts\smoke-liqa-mcp.ps1
powershell -File scripts\verify-install.ps1
py -3 -m pytest tests\test_same_level_contract.py tests\test_industry_ops_model.py -q
# Terminal A:
powershell -File scripts\bootstrap-control.ps1
# Terminal B:
powershell -File scripts\bootstrap-worker-vm.ps1
# Browser: http://127.0.0.1:8788/
```

## What “complete” means here

1. Full MCP engineer clone with Book1 + honesty + learner  
2. Industry Control/Worker topology for 2QA ops  
3. All 279 agency specialists catalogued + assigned  
4. CI gates for same-level + industry  
5. Portable Hands path (LIQA\mcp device_core)  
6. Bootstrap + verify scripts for Worker VMs  

## Honest remaining ops (not product holes)

- Reload Cursor MCP once so `liqa` server is live in the IDE  
- Fill vault / OTP Human Gate per tenant when running real UAT  
- Clone Worker VM image for scale-out beyond this machine  

**Orchestrator verdict:** Product COMPLETE for on-device industry SKU handoff.

## Agency QA training (added)

- **279 / 279** specialists have LIQA Manual-QA overlays  
- Path: `packaging/industry/agency-qa-trained/`  
- Tools: `liqa_agency_train_status`, `liqa_agency_trained_prompt`  
- Dispatch auto-injects trained overlay  

## Final package

`packaging/out/LIQA-FINAL-PACKAGE-*.zip` — see `docs/FINAL-PACKAGE.md`

