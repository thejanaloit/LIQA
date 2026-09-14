# YouTube analogy — Manual QA mission

## One sentence

Manual QA = create cases → execute them yourself on the real product UI → judge if each function works → **find and prove bugs**.

## YouTube example (owner)

Imagine QA of YouTube:

- Search, play, pause, comments, upload, settings, notifications…  
- You do **not** claim “search works” from an API log alone  
- You open the app, move the mouse, type, wait for the frame to change, watch the result  
- If something fails after many honest tries → bug with cropped proof  

ManualQA MCP must behave the same way on FusionX / banking UAT / any assigned system.

## Mapping to 10 steps

| YouTube-like action | ManualQA step |
|---------------------|---------------|
| Read what to test | 1–4 assigned + stories + existing |
| Confirm ready | 5 announce |
| Learn the app UI | 6 map (experience, no verdict) |
| Write what you will check | 7 NEW cases |
| Keep a results notebook | 8 Book1 |
| Actually click through | 9 headed + honesty-20 |
| Double-check honesty | 10 ×3 + learn |

## Main job

**Finding bugs** — not producing green pipeline dashboards.
