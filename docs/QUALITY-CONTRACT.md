# LIQA Quality Contract — SAME LEVEL for every developer

**Locked reference run:** PF-55248 Book1 SHARE (`PF-55248-Book1-SHARE.xlsx`)  
**Also gold:** PF-58374-Book1-SHARE · PF-59194 headed process  

Any developer / machine that ships LIQA work MUST match this bar.  
“Almost the same” is a fail.

---

## 1. Smoothness (how QA feels)

| Rule | Same-level requirement |
|------|------------------------|
| Headed only | Visible browser/desktop. No headless Pass/Fail as the method. |
| One session | Entry URL once; mouse+keyboard after; never close mid maker→checker. |
| Eyes→Brain→Hands | Capture → decide → visible move/click/type → wait frame → capture. |
| SPA forms | Prefer Playwright CDP on live Edge/Chrome — not raw pyautogui-only. |
| Focus hygiene | Minimize Excel / chat stealers before every proof capture. |
| Human Gate | ONLY OTP / MFA / CAPTCHA / unclear UI — never invent codes. |
| No fantasy | Missing data = BLOCKED/PARTIAL, not REAL_BUG. |

## 2. Performance (time & reliability)

| Metric | Target (same level) |
|--------|---------------------|
| Tool surface | ≥ 70 `liqa_*` tools load; `liqa_boot` < 3s local |
| Agency mesh | ≥ 200 specialists indexed from agency-agents (or bundled catalog) |
| Learner | SPEED-PLAYBOOK present; `liqa_learn_speed` returns tips at planning |
| Capture loop | Frame wait after every action; no rush-click on splash |
| Book1 build | From headed proofs only; ≥110 rows when story pack requires it |
| Share gate | `liqa_book1_validate` must pass before “Done” / share |

## 3. Book1 content (not only columns)

Columns (locked):

`Area | Issue | Screenshot | What is testing | Why that failed your prediction | 2nd QA confirmation | Simple explanation`

Content method (locked to SHARE gold):

- Every text cell = full English explanation (not button labels)
- Every data row embeds a real PNG
- `image_coverage = 100%`
- Min char floors from `mcp/book1_contract.py` / GOLD-PROFILE
- Evaluator blocks share on gold parity fail

Reference file to copy into every kit:

`artifacts/book1-samples/gold-share-pf55248/PF-55248-Book1-SHARE.xlsx`

## 4. Honesty

- Up to **20** distinct failed approaches with proof before `REAL_BUG`
- Found-a-way ⇒ **PASS** (not a bug)
- Triple honesty cycle at completion

## 5. Orchestration

Every assigned Jira KEY:

1. `liqa_boot`
2. `liqa_fresh_task` + `liqa_self_assign` (ignore prior memory)
3. `liqa_learn_speed`
4. `liqa_agency_dispatch` for intake / evidence / reality-checker / Book1
5. ISTQB phases 1→7
6. `liqa_learn_cycle` on close

## 6. Secrets

- Only `secrets/tmp-creds.json` (gitignored)
- Never commit passwords
- Never paste vault into chat/PRs

## 7. Pass / Fail for “same level”

A developer handover is **PASS** only if:

- [ ] `scripts/smoke-liqa-mcp.ps1` green
- [ ] `pytest tests/test_same_level_contract.py` green
- [ ] One sample Book1 validates against SHARE guards
- [ ] Dev can run `use LIQA` → `liqa_boot` in Cursor
- [ ] They read `docs/DEVELOPER-HANDOVER.md` and sign the checklist

Anything less = **NOT same level** — fix before giving to the next person.
