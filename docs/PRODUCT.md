# LIQA product

## One sentence

LIQA lets another company run **manual QA like a human** — visible desktop, real clicks, proof screenshots, Jira bugs — without hiring that human for every story.

## Why this is possible

Internal ManualQA already:

- Pulls assigned Jira work
- Maps the live UI
- Writes new test cases
- Executes headed (mouse + keyboard)
- Emits Book1 Excel + bugs with PNGs
- Stops honestly on MFA instead of inventing OTPs

External companies need the **same loop**, with **their** Jira, URL, credentials, and report format. That is LIQA.

## Customer flow

1. They put LIQA Worker on a Windows QA PC or VM **they own** (or a dedicated desktop we host for them).
2. They log into LIQA Control (our SaaS).
3. They connect Jira + UAT URL. Passwords stay on the worker, not in our multi-tenant DB.
4. They start a pack. They can watch the live screen (same as watching an employee).
5. They download Excel, proof, bugs in their format pack.

## Architecture

```
Customer browser → LIQA Control (jobs, live view, reports)
                         │
                         ▼
              LIQA Worker (Windows, headed)
                         │
                         ▼
              Their Chrome → their UAT
```

Brain can run on the worker. Hands never leave that desktop. Control is only orchestration + artifacts.

## Honest limits (put in the contract)

- First project: mapping + format harvest, not instant full coverage
- SMS / Google 2FA / hard CAPTCHA: their human must tap
- Worker must stay logged in with a real display (locked VM = product is down)
- We do not claim headless speed for UAT sign-off

## Build order

| Phase | Ship |
|---|---|
| P0 | Worker health + job HTTP (started under ManualQA headed-worker) |
| P1 | LIQA-branded Worker installer + live view |
| P2 | LIQA Control login, Jira OAuth, artifact download |
| P3 | Format packs + optional visible replay of already-proved cases |

## Names

| Name | Role |
|---|---|
| **LIQA** | What we sell |
| ManualQA | Engine (internal) |
| QAFusionX | LOLC internal pipeline — not the SKU |
| Cursor | How we build LIQA — not a customer dependency |
