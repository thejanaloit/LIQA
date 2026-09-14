# LIQA — Developer Handover Pack

Give **this folder product** to other developers so they get the **same performance and smoothness** as the owner run (PF-55248 SHARE level).

## What to give them

| Item | Path | Why |
|------|------|-----|
| Product root | `E:\LIQA` (or zip of repo) | Full MCP + Worker + gold + skills |
| Quality contract | `docs/QUALITY-CONTRACT.md` | Non-negotiable same-level bar |
| This handover | `docs/DEVELOPER-HANDOVER.md` | Install + first run |
| Acceptance | `docs/SAME-LEVEL-ACCEPTANCE.md` | Sign-off checklist |
| Gold Book1 | `artifacts/book1-samples/gold-share-pf55248/` | Content + layout reference |
| Skills | `skills/` especially `SPEED-PLAYBOOK.md` | Speed techniques that made the run smooth |
| Agency source | `agency-agents` clone (or set `LIQA_AGENCY_HOME`) | 250+ specialists |
| ManualQA twin | Optional `ManualQA-Agent` | Reference implementation |

Do **not** hand over: `.env`, `secrets/tmp-creds.json`, real UAT passwords, customer PNGs outside proof folders.

## 30-minute install (other developer PC)

### 0) Machine

- Windows 10/11 with a **real interactive desktop** (not Session 0 / locked)
- Python 3.11+ (`py -3`)
- Edge or Chrome
- Cursor Desktop with MCP enabled

### 1) Get code

```powershell
# Option A: clone your company LIQA remote
git clone <YOUR_LIQA_REMOTE> LIQA
cd LIQA

# Option B: unzip the handover zip onto D:\ or E:\
```

### 2) Env

```powershell
copy .env.example .env
# Edit paths for THIS machine:
#   LIQA_HOME=<this repo>
#   LIQA_AGENCY_HOME=<path to agency-agents>
#   MANUAL_QA_HOME=<optional ManualQA-Agent or QAFusionX manualQA>
```

```powershell
copy secrets\tmp-creds.example.json secrets\tmp-creds.json
# Fill maker/checker for THEIR tenant — never commit
```

### 3) Install Cursor MCP

```powershell
py -3 scripts\install_liqa_mcp.py
```

Reload MCP servers in Cursor. Confirm server key **`liqa`** is listed.

### 4) Prove same level

```powershell
powershell -File scripts\smoke-liqa-mcp.ps1
py -3 -m pytest tests\test_same_level_contract.py -q
```

Both must be green. Then open Cursor chat and say:

```text
use LIQA
```

Agent must call `liqa_boot`. If it summarises instead of booting — MCP not loaded; fix install.

### 5) First real task (smoothness check)

Assign a small Jira KEY and require:

- `liqa_fresh_task` + `liqa_self_assign`
- `liqa_learn_speed` before nav
- Headed proof captures
- Book1 validate before Done

If they skip headed UI or invent screenshots → **fail quality contract**.

## What “same level” means in one sentence

**Same Book1 SHARE content method + same headed Eyes→Brain→Hands smoothness + same honesty/evaluator gates — on every developer machine.**

## Support contacts / owners

- Product: LIQA (`mcp/server.py`)
- Process law: ISTQB CTFL in `mcp/laws.py`
- Book1 floors: `mcp/book1_contract.py`
- Speed tips: `skills/SPEED-PLAYBOOK.md`

## Zip recipe (for email / Teams)

```powershell
powershell -File scripts\pack-developer-handover.ps1
# → packaging/out/LIQA-developer-handover-<date>.zip
```

Zip excludes secrets, `.env`, huge capture dumps, and `__pycache__`.
