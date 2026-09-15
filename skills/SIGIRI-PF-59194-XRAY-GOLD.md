# GOLDEN REFERENCE — PF-59194 / Sigiri Jayasekara (TestCrafters)

Source site: https://lolcgroupdev.atlassian.net  
Primary keys harvested 2026-09-10:

| Key | Type | Role |
|-----|------|------|
| **PF-59194** | Xray **Test** | Golden Test shell (this ticket) |
| **PF-55248** | Story | Parent QA task Sigiri owns |
| **PF-51556** | Epic | Product epic for Receipt (migrated contracts) |
| **PF-58380** | Story | `QA AGENT - …` clone of PF-55248 (agent lane) |
| **PF-57736** | Xray Test | Same Test-shell pattern (multi-story link) |
| **PF-57509 / PF-57624 / PF-59174 / PF-58713** | Bug | TestCrafters bug-writing brain |

Author / party to **become**: **SIGIRI JAYASEKARA** + **TestCrafters** squad thinking.

---

## 1. What PF-59194 actually is (tiny truth)

PF-59194 is **not** a long prose test script in the Jira Description field.

It is an **Xray Test work item** that:

1. Uses the **exact Story title** as the Test summary  
2. Links with issue-link type **Test** → outward **`tests`** → Story **PF-55248**  
   (Story side shows **is tested by** PF-59194)
3. Sets **Country** = Sri Lanka (field `customfield_10177`)
4. Leaves Description / Attachments / Comments **empty** in Jira REST
5. Is created by Sigiri, assigned to Sigiri, moved **To Do → DONE** almost immediately (coverage/execution tracker shell)
6. Sets release checkboxes often to Yes: Jasper_reports_NEW, Workflows_NEW, Rules_NEW, Environment_properties_NEW
7. URS Status may remain **URS Pending** even when Test is DONE

**Changelog order (how they work):**
1. Create Test  
2. Link: *This work item tests PF-55248*  
3. Status To Do → DONE (+ resolution Done)  
4. Assignee = SIGIRI JAYASEKARA  

**Thinking pattern:**  
> First create the Xray Test that *binds* to the Story with the official pipe title.  
> Detailed steps live in Xray Manual Steps / execution / BA scenarios — not a novel in Description.  
> Close the Test when writing+execution for that Story lane is complete.

ManualQA must **create the same shell** for every assigned Story:  
`issuetype=Test` + summary=Story.summary + link `tests` → Story + Country + DONE only after real work.

---

## 2. Title taxonomy (LOCKED — copy Sigiri)

### Stories / Xray Tests (same shape)

```
{Module} | {Feature / Sub-feature} | {Change type} | Testcase writing and execution
```

Examples from gold:

- `Lending Module | Receipt behaviors for migrated contracts  | Testcase writing and execution`  ← PF-59194 / PF-55248
- `Lending Module | Receipt Reallocation | Modification to Existing Functionality | Testcase Writing and Execution - Task 01`
- `Lending Module | Account Maintenance | Loan Account Cancellation | Modification for an existing function | …`
- `Lending Module | Analytics Report |BI Collection Report | New report | Testcase writing and execution`

Rules:

- Pipe `|` separators (2–6 segments)
- Start with **Module** (`Lending Module`, `Account Module`, …)
- End QA Stories/Tests with **Testcase writing and execution** (or Task 01/02)
- Do **not** invent `[Module][Submodule][FP] - Validate that…` for FusionX PF project — that was ipaydev SSP style and is **secondary**. For lolcgroupdev **PF**, Sigiri pipe titles win.

### QA AGENT clone Stories

```
QA AGENT  - {exact human Story title}
```

Example: `QA AGENT  - Lending Module | Receipt behaviors for migrated contracts  | Testcase writing and execution` (PF-58380)  
Labels: `QA_AGENT`

---

## 3. Link graph (LOCKED)

```
Epic (product)
  ↑  (Story often "tests" / linked to Epic)
Story  (TestCrafters / V{n}_Testing)   ← human QA assignee
  ↑ is tested by
Xray Test  (summary == Story summary)  ← PF-59194 pattern
  +
Bugs  linked with Test / Relates to Story + often FXN-* code ticket
```

Always:

1. Create/find Story  
2. Create Xray **Test** with **same summary**  
3. Link Test → Story with link type **Test** / outward **tests**  
4. Never edit/delete existing Tests — **ADD NEW only** (still law)

---

## 4. Bug writing brain (THIS is how they think)

### Title pattern (LOCKED)

```
#TestCrafters #Kenya #UAT#cNwNb# {Module} | {What the user did / what broke — present tense, concrete}
```

Variants observed:

- `#TestCrafters#Lending Module#UAT#cNwNb | When User Try To …`
- `#TestCrafters #Kenya #UAT#cNwNb# Lending Module | When Creating … Got 500.`
- `#TestCrafters#Lending#cNwNb#UAT| When User Try To Select …`

Rules:

- Hashtags first: **TestCrafters**, country/tenant (**Kenya**, **cNwNb**), **UAT**
- Then Module
- Then **observable user-facing failure** (not “TC-03 failed”)
- Prefer **When User Try To…** / **When Creating…** / **Unable to…**

### Description pattern (LOCKED)

```markdown
**Issue:** <1–3 sentences: what is wrong in business language>

**Steps to Reproduce:**
1. Navigate to …
2. Select …
3. Initiate …
4. Observe …

**(Expected):** <what should happen>
**(Actual):** <what happened>
```

Optional:

- Environment field: `cNwNb-UAT-Kenya` (or exact tenant)
- Severity: Medium / High (`customfield_10167`)
- Labels: `TestCrafters`, `LendingModule`, sprint tag (`SEPT13`, `AUG16`), squad (`CyberDrift`, `NovaNest`)
- Attach proof screenshots (they attach when critical — e.g. PF-58713 had 5)
- Link Bug to Story via **Test** link; Relates to FXN-* when code ticket exists

### How they choose scenarios (thinking)

From BA comment on PF-49561 to Sigiri:

> check scenarios from **BA verification**, including **Receipt Details with Account Inquiry** and **other payment methods**.

So the brain is:

1. Read BA / URS / verification notes — not only AC bullets  
2. Trace **real money paths**: cash, cheque, internal transfer, credit note, excess, refundable  
3. Break at **boundaries** (latest receipt, reverse disbursement, toggles)  
4. File **one bug per concrete bad behaviour** with hashtag title  
5. Keep Story/Test titles hierarchical; keep Bug titles behavioural

---

## 5. Labels & fields cheat sheet

| Artefact | Labels / fields |
|----------|-----------------|
| Story | `TestCrafters`, `V69_Testing` / `V67_Testing`, module labels |
| Epic | `LendingModule`, `QA_Planned`, `Version_69`, country client labels |
| Xray Test | often no labels; Country=Sri Lanka or tenant country |
| Bug | `TestCrafters`, `LendingModule`, sprint, squad; Env=`cNwNb-UAT-Kenya` |
| Agent Story | `QA_AGENT` + `QA AGENT  -` title prefix |

---

## 6. ManualQA agent must BE Sigiri

When working lolcgroupdev **PF** assigned QA:

1. Mirror Story title exactly on new Xray Tests  
2. Link `tests` → Story  
3. Explore like BA verification + payment-method matrix  
4. File bugs in **#TestCrafters #Kenya #UAT#cNwNb#** title format  
5. Bug body = Issue + Steps + Expected/Actual  
6. Book1 Excel remains deliverable, but **Jira shape** follows this gold — not inventing SSP-only titles for PF  
7. Mark Xray Test DONE only after writing + headed execution honesty for that Story  

---

## 7. Anti-patterns (do not do)

- Filling Test Description with fake fluff while leaving link missing  
- Editing Sigiri’s existing Tests  
- Bug titles like `PF-58376 FAIL row 12`  
- Using only ipaydev SSP-38278 bracket titles on FusionX PF without pipe taxonomy  
- Closing Story/Test DONE with no bugs **and** no headed proof when AC is broken  

---

## 8. Quick clone checklist (agent)

- [ ] Story key + exact summary  
- [ ] Epic key  
- [ ] Create Xray Test = same summary + Country + `tests` link  
- [ ] Map BA scenarios / payment methods / negatives  
- [ ] Execute headed; proof PNGs  
- [ ] File TestCrafters-format bugs  
- [ ] Book1 gold columns + simple English G  
- [ ] Transition Test → DONE when lane complete  
