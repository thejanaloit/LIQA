# Ops model — 2 QA humans + LIQA execution

## Roles

### QA Gate Lead (Human 1) — primary on-call
- Owns Human Gate inbox (OTP / MFA / unclear UI)
- Unblocks vault / SSO / checker accounts
- First-line sign-off on Book1 for normal stories

### QA Sign-off Lead (Human 2) — quality owner
- Spot-checks agent proofs (sample %)
- Approves REAL_BUG vs BLOCKED calls on disputes
- Release / Done transition in Jira after validators pass
- Escalates product defects to engineering

Both may rotate weekly. Never leave gates with nobody watching.

---

## Daily loop

```
08:30  Open Control UI → Workers headed? Gates empty?
09:00  Queue / confirm Jira-assigned KEYs as LIQA jobs
       (agents/Workers execute — humans do not click stories)
…      Slack/Teams: gate alerts only
Anytime Resolve gate (enter OTP / complete SSO / supply account #)
16:00  Review Book1 validate + honesty for finished jobs
16:30  Sign-off → Jira Done / bug push
17:00  Learner notes (what slowed workers today)
```

Humans **do not** re-run the full Manual QA walk unless spot-check fails.

---

## When a human must act (only these)

| Event | Action |
|-------|--------|
| Gate: OTP / MFA | Enter code in Control / on Worker live view |
| Gate: SSO splash | Complete login once; leave session for worker |
| Gate: missing data | Fetch account/receipt from Jira/ops; resume job |
| Worker health red | Unlock VM / fix autologon / restart headed session |
| Validator fail | Reject sign-off; send job back to worker |
| Suspected fantasy PASS | Re-run honesty / headed sample |

Everything else = LIQA execution.

---

## Control UI focus (2-human console)

Must show at all times:

1. **Workers** — headed ready / locked / Session 0  
2. **Gates** — waiting human (age, story, worker)  
3. **Jobs** — queued / running / needs_signoff / done  
4. **Sign-off** — Book1 path + validate result  
5. **Audit** — who resolved which gate  

API surface:

- `GET /v1/ops/summary` — single pane for the 2  
- `POST /v1/gates/{id}/resolve` — human completed gate  
- `POST /v1/jobs/{id}/signoff` — human accepts Done  

---

## SLAs (suggested)

| Item | Target |
|------|--------|
| Gate acknowledgment | &lt; 15 min business hours |
| Gate resolve (OTP) | &lt; 5 min after SMS received |
| Sign-off after Book1 green | &lt; 1 business day |
| Worker red health | &lt; 30 min restore |

---

## Anti-patterns (breaks the 2-person model)

- Humans still clicking every FusionX path “just to be sure”  
- Sharing one RDP desktop across parallel jobs  
- Ignoring gates overnight with jobs stuck  
- Signing off without `book1_validate`  
- Storing passwords in chat / tickets  

---

## Success metric

After 30 days:

- ≥ 80% of story execution hours on Workers  
- ≤ 2 FTE on QA gates/sign-off  
- Gate volume trending down (SSO sessions sticky, data packs ready)  
- Book1 SHARE pass rate ≥ 95% on first sign-off attempt  
