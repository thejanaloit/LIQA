# Same-Level Acceptance Checklist

Developer name: _______________  
Machine: _______________  
Date: _______________  
LIQA commit / zip: _______________

## A. Install

- [ ] Repo / zip extracted; Python 3.11+ works (`py -3 --version`)
- [ ] `.env` created from `.env.example` with **this machine’s** paths
- [ ] `secrets/tmp-creds.json` present locally (not in git)
- [ ] `py -3 scripts/install_liqa_mcp.py` succeeded
- [ ] Cursor shows MCP server **`liqa`**

## B. Automated same-level gates

- [ ] `scripts/smoke-liqa-mcp.ps1` → OK
- [ ] `pytest tests/test_same_level_contract.py` → all pass
- [ ] Agency count ≥ 200 **or** bundled catalog fallback documented
- [ ] `liqa_*` tool defs ≥ 70 in `mcp/server.py`

## C. Smoothness (manual 15 min)

- [ ] Chat: `use LIQA` → agent runs `liqa_boot` (not a prose summary only)
- [ ] `liqa_learn_speed` returns tips including SPEED-PLAYBOOK ideas
- [ ] `liqa_agency_dispatch` can assign `agents-orchestrator`
- [ ] One headed `liqa_capture` (or device capture) produces a PNG
- [ ] Developer confirms Excel is minimized before proof captures (process understood)

## D. Book1 bar (must match SHARE method)

- [ ] Read `artifacts/book1-samples/gold-share-pf55248/PF-55248-Book1-SHARE.xlsx` (or PF-58374 gold)
- [ ] Understand: full English cells + embedded PNG every row
- [ ] `book1_contract` min chars known; validate blocks weak rows

## E. Honesty / Human Gate

- [ ] Knows: never invent OTP; Human Gate only
- [ ] Knows: 20 approaches before REAL_BUG; found-a-way = PASS

## F. Sign-off

I confirm this machine can deliver **the same LIQA level** as the PF-55248 reference run.

Signature: _______________  

**Result:** PASS / FAIL (circle one)  
If FAIL — list gaps: _______________
