# LIQA FINAL PACKAGE

**Product:** LIQA — Live Intelligent QA  
**Version:** 2026-09-14-qa-trained-v1  
**Model:** 2 QA humans + LIQA Workers + **279 QA-trained agency specialists**

## What’s in the package

| Item | Location |
|------|----------|
| Cursor MCP (`liqa`, 74+ tools) | `mcp/server.py` |
| Control (2QA console) | `apps/control/` :8788 |
| Worker (headed Hands) | `apps/worker/` :8787 |
| Agency catalog | `packaging/industry/agency-catalog.json` |
| **QA-trained overlays (279)** | `packaging/industry/agency-qa-trained/*.md` |
| Training manifest | `packaging/industry/agency-qa-trained/MANIFEST.json` |
| Book1 SHARE gold | `artifacts/book1-samples/` |
| Industry / ops docs | `docs/INDUSTRY-PRODUCT.md`, `OPS-MODEL-2QA.md`, `DEPLOY-WORKER-VM.md` |
| Quality contract | `docs/QUALITY-CONTRACT.md` |
| Complete status | `docs/COMPLETE.md` |

## Agency QA training

Every specialist received an additional LIQA Manual-QA overlay:

- ISTQB 7 phases  
- Eyes→Brain→Hands  
- Book1 SHARE content method  
- Honesty-20 + Human Gate  
- Track-specific mission (execution / security / platform / docs / …)

Dispatch always injects the trained overlay via `liqa_agency_dispatch`.  
Check: `liqa_agency_train_status` → `count: 279`, `trained: true`.

## Install (any machine)

```powershell
# 1) Unzip this package
cd <LIQA_ROOT>
copy .env.example .env
copy secrets\tmp-creds.example.json secrets\tmp-creds.json
# fill vault locally — never commit

# 2) Cursor MCP
py -3 scripts\install_liqa_mcp.py
# Reload MCP in Cursor → liqa green

# 3) Prove
powershell -File scripts\smoke-liqa-mcp.ps1
py -3 -m pytest tests\test_same_level_contract.py tests\test_industry_ops_model.py -q

# 4) Industry runtime
# Terminal A: powershell -File scripts\bootstrap-control.ps1
# Terminal B: powershell -File scripts\bootstrap-worker-vm.ps1
```

## Use

```text
use LIQA
```

Then: `liqa_boot` → `liqa_agency_train_status` → `liqa_agency_dispatch` → ISTQB 1→7.

## Honest ops model

- **Workers + trained specialists:** almost all QA execution  
- **2 humans:** OTP/MFA gates + Book1 sign-off  
- Not zero humans
