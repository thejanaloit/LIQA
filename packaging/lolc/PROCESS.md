# How LOLC FusionX QA actually works (observed on Jira)

Companies differ. LOLC FusionX QA is **not** generic ISTQB paperwork and **not** iPay `[FP]` titles.  
**Training source = project PF tickets**, not Teams chat.

## Happy path (from live PF tickets)

```
Theeksha / Sandun / Charuni
  └─ QA Story: "Module | Feature | … | Testcase writing and execution"
       labels: TestCrafters|AutoBots|PulseCheckers|DefectHunters + V69_Testing|V71_Testing
       assignee: Sigiri / Udari / Chamoda / Janani / Sashika / Thanula …
            ├─ Xray Test(s) — same pipes, or path-split (PF-50325 → PF-58668, PF-59085, PF-59089)
            │     link: Test / tests  (empty Jira description; steps in Xray)
            ├─ Headed UAT Kenya/Zambia (cNwNb, GBAF, Live tags)
            ├─ Book1 SHARE (LIQA Perfect-100 overlay)
            └─ Bugs: #TestCrafters|#Autobots|#Shielders|#GlobalSupport|#DefectHunters|#PulseCheckers
                 + failure sentence
                 body: Issue / Steps / Actual / Expected (Sigiri) or screenshot + symptom (Janani)
                 assignee: developer  (e.g. Tishan Dhanuja, Miyuru)
                 Relates: FXN HotFix
                 close: QA comments "Verified in UAT" → DONE
```

Nilmie’s `QA AGENT - …` Stories are **clones** of the Human QA Story. Harvest the **source** (attachments live there).

## Branch conditions

| If | Then |
|----|------|
| Ticket is a **clone** / QA AGENT | Harvest the **source** feature. Clone attachments are often empty. |
| Existing Xray Test already exists (PF-59194) | ADD NEW sibling Tests. Never edit/delete. |
| One Story has several path Tests | Copy Sigiri: extra pipe at the end (`… \| Loan Cancellation Workflow`). |
| Pending Approve/Reject | Switch to **checker**. Maker only observes. |
| Azure AD / splash / MFA | Human Gate. Do not invent OTP. |
| Same 500 / blank shell already open | Relates oldest bug + comment proof. Do not mint a twin. |
| Book1 written but headed paths still open | Comments stay **NOT Done** (PF-55248). |
| Story is **Sanity Testing \| Version 69** | Smoke the module on live/UAT (PF-59304). Not a full Testcase-writing pack. |

## Failure / recovery

- Blank SPA after URL jump → recover via **menu tile** or one address-bar deep URL in the **same** session.
- AuNEXO splash-only HTML → enter via FusionX ReturnUrl, or Human Gate Azure AD.

## Handoffs

- QA → Dev: Bug with Issue / Steps / Actual / Expected + screenshot. Assignee is a developer, not yourself (Janani sometimes self-assigns until verify).
- Dev → QA: comment + screenshot; QA **Verified in UAT**.
- QA → Checker: Pending queue row; do not approve as maker.
- LIQA → Jira: Story comment with keys, Book1 path, honesty verdict.

## Observable states (PF)

- Story/Test: `To Do` (10057) while work is in flight; gold Sigiri Test `DONE` (10009).
- Labels: `TestCrafters`, `AutoBots`, `Shielders`, `PulseCheckers`, `V69_Testing`, `V71_Testing`, `CyberDrift`, `LendingModule`, `SEPT13`.
