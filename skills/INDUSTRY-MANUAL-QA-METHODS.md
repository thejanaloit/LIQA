# Industry Manual QA methods (100% research pack)

Ground every ManualQA run in these methods.  
Updated: 2026-09-12 after owner YouTube-analogy re-explain + public research.

## Sources (study, do not invent)

- ISTQB Foundation Level syllabus v4.0 — fundamental test process + exploratory as experience-based technique  
- Session-Based Test Management (Jon & James Bach / Satisfice) — charter, session, TBS, debrief  
- Testing vs Checking (Bach / Bolton) — checking confirms expectations; testing investigates  
- SFDPOT product tour heuristic (Bach)  
- Explore It! / RST heuristics (Hendrickson, Bach)  
- Defect evidence practices used by professional manual QA teams  

## ISTQB fundamental process → ManualQA map

| ISTQB | ManualQA step |
|-------|----------------|
| Analysis & design from requirements | 3 stories + 6 map + 7 cases |
| Implementation | 7 NewTestCases + Jira NEW only |
| Execution | 9 headed Eyes→Brain→Hands |
| Reporting | 8 Book1 + Jira bugs |
| Closure | 10 honesty×3 + learn_cycle |

## What Manual QA is (owner + industry)

Owner: YouTube-style — write cases, execute yourself on real UI, decide if function works, **find bugs**.

Industry: Manual testing is human-led investigation of a product using scripted cases **and** exploratory sessions. Automation may assist setup; it does **not** replace headed judgment for ManualQA MCP.

## Scripted functional testing

- Trace to story / AC  
- Preconditions, numbered steps, expected result  
- Happy + negative + empty + RBAC  
- Match local Jira tone (SSP-42118 / SSP-38278 / PF-59194)  

## Exploratory + SBTM (Bach)

1. **Charter** — Explore [target] with [resources] to discover [information]  
2. **Session** — 60–120 minutes focused (use `manualqa_sbtm_charter`)  
3. **TBS** — time on Test design/execution, Bug investigation, Setup  
4. **Debrief** — what found, coverage, obstacles, next charter  
5. Step 6 map sessions are exploratory learning (no Pass/Fail)  
6. Step 9 hunts use SBTM when scripted cases leave risk  

## Design techniques (always)

| Technique | Use |
|-----------|-----|
| Equivalence partitioning | Input classes |
| Boundary value analysis | Limits, amounts, dates |
| Decision tables | Business rule combos |
| State transition | Pending → approve / reject |
| Use-case / story path | E2E journeys |

## Heuristic tours

- **SFDPOT** — Structure, Function, Data, Platform, Operations, Time  
- **CRUD** on every entity  
- Empty / invalid / unicode / concurrency  
- RBAC / maker-checker (banking)  
- Regression vs ExistingTestCases  

## Defect reporting (evidence-first)

- Clear issue + steps + expected + actual + environment  
- Cropped screenshot at exact failure  
- Match knowledgeBase tone (#TestCrafters / SSP)  
- Attach PNG to Jira — paths-only is not enough  

## Honesty (ManualQA-specific, mandatory)

- 20 approaches before REAL_BUG  
- 3 revalidation cycles before close  
- No Pass/Fail label in step 6  

## Anti-patterns

- Calling a pipeline “manual QA”  
- Pass without frame change  
- Bug after one flaky click  
- Editing others’ Xray tests  
- Inventing OTP  

## Skill growth

After every closed task: `manualqa_learn_cycle` → update this pack without regressing 100% doctrine.
