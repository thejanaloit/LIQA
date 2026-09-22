# PERFECT-100 GOLD — PF-59486 (owner-locked LIQA bar)

**Version:** `2026-09-22-liqa-perfect-100-v6`  
**Reference run:** [PF-59486](https://lolcgroupdev.atlassian.net/browse/PF-59486) (clone of [PF-55248](https://lolcgroupdev.atlassian.net/browse/PF-55248))  
**Format gold:** [PF-59194](https://lolcgroupdev.atlassian.net/browse/PF-59194) Sigiri Manual steps  
**Book1 SHARE:** `workspace/default-run/outputs/PF-59486/PF-59486-Book1-SHARE.xlsx` (110 rows · 100% images · gold_parity_ok)
**Attach RPA:** `mcp/jira_attach_proofs.py` — bug proofs must appear under Jira Attachments (PF-59783 lesson)

Owner lock: **this end-to-end Manual QA level is the Perfect-100 bar for LIQA MCP + every agency specialist.**  
“Almost” is a fail. Next KEY must match or beat this kit.

---

## What Perfect-100 means (checklist)

| Gate | Perfect-100 requirement |
|------|-------------------------|
| ISTQB | Phases **1→7** all `done` in `liqa_status` |
| Harvest | `liqa_jira_harvest_status.complete=true` before headed map |
| Clone | Fresh KEY; Cloners + Relates to epic + Sigiri gold |
| Map | Headed experience map (no Pass/Fail) under `map/<KEY>/` |
| Design | Path-split P00… + Action\|Data\|Expected Result only |
| Xray | NEW Tests linked `tests` → Story; UI RPA CSV import (not Attachments) |
| Book1 | ≥110 rows, image_coverage=100%, SHARE min-chars, `liqa_book1_validate` ok |
| Execute | Eyes→Brain→Hands; honesty 20 / obvious-3 with proof PNGs |
| Bugs | REAL_BUG only after honesty; **dedupe** existing open bugs first |
| Attach | Cropped PNGs in Jira **Attachments** panel via `liqa_attach_bug_proofs` / auto `liqa_attach_end_of_run` (pack `outputs/<KEY>/jira-attach-pack-<BUG>/`) — description filenames alone fail |
| Close | learn_cycle + Xray EOR + Attach EOR + comment on Story + proofs under `reports/proof/<KEY>/` |

---

## Agency-agents study lock (every specialist)

All 279+ agency overlays MUST carry this Perfect-100 doctrine:

1. YouTube Manual QA analogy — find bugs with cropped proof, not pipelines.
2. ISTQB CTFL 7 activities — never skip.
3. Book1 SHARE method — full English + PNG every row.
4. Honesty-20 / obvious-3 (`http_5xx`, `blank_shell`, …).
5. Sigiri Xray lock — UI RPA Import→From csv→Action\*|Data|Expected Result.
6. Fresh KEY memory; Human Gate only for OTP/MFA/CAPTCHA/unclear UI.
7. Orchestrator owns phase gates; engineer owns headed truth.

---

## Device / FusionX lessons locked from PF-59486

- AM hub tile clicks often miss → recover with **one** address-bar deep URL (same session).
- Locate **Create New** by blue-pixel cluster (right content edge), not guessed mid-toolbar.
- Prefer Playwright CDP when available; Sync Playwright **must run in subprocess** inside MCP asyncio.
- Check free disk on workspace drive before Book1 SHARE embed (110 thumbs).
- Before filing Bug: JQL for same symptom; if open duplicate exists → Relates + comment, do not mint a twin.

---

## Artifacts to copy as kit

```
workspace/default-run/outputs/PF-59486/PF-59486-Book1-SHARE.xlsx
workspace/default-run/reports/proof/PF-59486/
workspace/default-run/NewTestCases/PF-59486/
skills/PERFECT-100-PF-59486-GOLD.md
artifacts/perfect-100-pf59486/
```

---

## Version bump

MCP `PERSONA_VERSION` / `laws.VERSION` = `2026-09-22-liqa-perfect-100-v6`  
Agency training = `2026-09-16-qa-trained-perfect-100-v2`  
v6 adds **BUG PROOF ATTACH LOCK** — end-of-run Attachments RPA (`liqa_attach_end_of_run`).
