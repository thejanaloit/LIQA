# Honesty — 20 approaches + 3 cycles (100%)

## Owner law (step 9)

You have to try every honest way.  
After **20 rounds with various approaches** you still cannot succeed → **REAL BUG**.  
Without that process you **cannot** label a bug.  
Without that process you **cannot** label good / PASS.

## Tools

- `manualqa_honesty_start(case_id, task_key, concern)`  
- `manualqa_honesty_attempt(...)` — record each approach + proof  
- `manualqa_honesty_verdict(...)` — PASS | REAL_BUG | BLOCKED | N/A  

REAL_BUG requires **20** recorded approaches (enforced in agents_backbone).

## Step 10 — triple revalidate

1. `manualqa_revalidate_cycle` cycle=1  
2. cycle=2  
3. cycle=3  
4. `manualqa_learn_cycle`  

## Gatekeeper

Optional: `honesty_20_gate` / `manualqa_gate_call` before labeling.

## Anti-patterns

- One flaky fail → bug  
- Pass without frame-change proof  
- Skipping honesty because “obvious”
