# LIQA — Complete Process Map (every micro-process)

**Locked to:** Full Stable V1 chat + Perfect-100 **PF-59486** + MCP `2026-09-16-liqa-perfect-100-v5`  
**Machine catalog:** [`MICROPROCESSES.json`](MICROPROCESSES.json) (107+ micro-processes) · [`LIQA-TOOLS.json`](LIQA-TOOLS.json) (98 tools)  
**Source chat:** [`../chat/FULL-CHAT.md`](../chat/FULL-CHAT.md)

> If someone asks how LIQA works end-to-end: give **this folder** + the Stable V1 chat.

---

## 0) Master flow (nothing skipped at macro level)

```mermaid
flowchart TB
  subgraph META["META — Company genesis from Stable V1 chat"]
    M0[MP-000 Connect agency-agents]
    M1[MP-001 Owner Manual QA doctrine / YouTube analogy]
    M2[MP-002 Absorb ManualQA + QAFusionX]
    M3[MP-003 Map to ISTQB CTFL 7 + SBTM + 29119]
    M4[MP-004 Scaffold LIQA MCP E:/LIQA]
    M5[MP-005 Train 279 agency Perfect-100 overlays]
    M6[MP-006 Lock PF-59486 Perfect-100 into laws/persona]
    M7[MP-007 Export Stable V1 chat + GitHub tags]
    M0-->M1-->M2-->M3-->M4-->M5-->M6-->M7
  end

  subgraph BOOT["BOOT — every run"]
    B0[MP-010 liqa_boot + laws + persona + todos]
    B1[MP-011 fresh_task + self_assign]
    B2[MP-012 learn_speed]
    B3[MP-013 flow_chart]
    B0-->B1-->B2-->B3
  end

  subgraph ISTQB["ISTQB CTFL 1→7 — every KEY"]
    P1[1 Planning + FULL Jira harvest]
    P2[2 Monitoring / stop-the-line]
    P3[3 Analysis + headed experience map]
    P4[4 Design Sigiri NEW cases]
    P5[5 Implement Xray UI RPA + Book1 scaffold]
    P6[6 Execute Eyes→Brain→Hands + honesty]
    P7[7 Complete Book1 SHARE + learn + closeout]
    P1-->P2-->P3-->P4-->P5-->P6-->P7
  end

  META --> BOOT --> ISTQB
  P7 --> M7
```

---

## 1) Agents that move on every process

### 1.1 In-process LIQA roles (always)

| Role | Mission | Primary micro-processes |
|------|---------|-------------------------|
| **orchestrator** | Phase gates, handoffs, stop-the-line | MP-010…013, MP-112, MP-200…202, phase completes |
| **intake** | Jira assign + **full harvest** + creds + stories | MP-100…113, MP-300…301 |
| **mapper** | Headed experience map (NO Pass/Fail) | MP-304…313 |
| **designer** | Sigiri NEW tests EP/BVA/state | MP-400…407 |
| **executor** | Headed run + Xray UI RPA + bugs | MP-500…507, MP-600…614 |
| **honesty_referee** | 20 approaches / obvious-3 | MP-604…607, MP-701 |
| **book1_reporter** | SHARE Book1 rows + validate | MP-508…509, MP-611, MP-700 |
| **learner** | learn_cycle / SPEED-PLAYBOOK | MP-012, MP-703, MP-707 |

### 1.2 Agency mesh (279 Perfect-100 overlays)

Every `liqa_agency_dispatch` loads `packaging/industry/agency-qa-trained/<id>.md`.

**Core specialists on Perfect-100 runs (always dispatch):**

| Specialist | When |
|------------|------|
| `agents-orchestrator` | Phase start / Perfect-100 lock |
| `evidence-collector` | Map + execute + Book1 proof |
| `reality-checker` | Harvest gates, honesty, Book1 validate, bug dedupe |
| `senior-project-manager` | Living plan / monitoring |
| `workflow-architect` | Map structure / micro-flow |
| `test-results-analyzer` | Sufficiency / evaluate_all |
| `product-manager` | Story AC / scope |
| `technical-writer` | Plain-English assignedTasks + closeout |
| `multi-agent-systems-architect` | Mesh topology |
| `code-reviewer` | MCP/law diffs when Perfect-100 uplift |

**Tracks (all 279):** domain 158 · data 44 · security 15 · gtm 13 · frontend 10 · execution 10 · platform 9 · docs 6 · orchestrator 5 · design 5 · backend 4 — see MANIFEST.

```mermaid
flowchart LR
  ORCH[liqa_agency_dispatch]
  ORCH --> OV[Load Perfect-100 overlay]
  OV --> WS[Workstream brief]
  WS --> EV[Return evidence paths + verdict only]
  EV --> GATE[Orchestrator phase gate]
```

---

## 2) Phase 1 — Planning (micro)

```mermaid
flowchart TD
  A[MP-100 Pull assigned Jira] --> B[MP-101 Harvest checklist]
  B --> C[MP-102 KEY body]
  C --> D[MP-103 Cloners]
  D --> E[MP-104 Relates/Tests]
  E --> F[MP-105 Epic/feature/parent]
  F --> G[MP-106 ALL attachments PDF/PNG/msg]
  G --> H[MP-107 Extract PDF text]
  H --> I[MP-108 harvest_status.complete=true]
  I -->|false| G
  I -->|true| J[MP-109 Request 2-3 credentials]
  J --> K[MP-110 Credentials honesty]
  K --> L[MP-111 Agency intake dispatch]
  L --> M[MP-112 Announce planning done]
  M --> N[MP-113 Heartbeat]
```

**Folders:** `assignedTasks/<KEY>/` · `knowledgeBase/<KEY>/jira-attachments/`  
**Hard gate:** no headed map until `liqa_jira_harvest_status.complete=true`.

---

## 3) Phase 2 — Monitoring (micro)

```mermaid
flowchart TD
  H[MP-200 heartbeat + status + todos + mesh_status] --> S{Control visible?}
  S -->|no| ASK[ASK human — never guess x/y]
  S -->|yes| E[MP-202 evaluate_all]
  E --> M{Missing evidence?}
  M -->|yes| STL[MP-201 stop_the_line]
  M -->|no| CONT[Continue current phase]
```

---

## 4) Phase 3 — Analysis + experience map (micro)

```mermaid
flowchart TD
  U[MP-300 UserStories] --> X[MP-301 ExistingTestCases read-only]
  X --> T[MP-302 Harvest Jira tone / gold refs]
  T --> G{MP-303 harvest complete?}
  G -->|no| BLOCK[BLOCK map]
  G -->|yes| B[MP-304 browser_open entry URL ONCE]
  B --> OTP{OTP/MFA?}
  OTP -->|yes| HG[MP-305 Human Gate / await_otp / ack]
  OTP -->|no| SBTM[MP-306 SBTM charter]
  HG --> SBTM
  SBTM --> LOOP[MP-307 Device loop]
  LOOP --> MAP[MP-308 save_map_node every control]
  MAP --> PLAN[MP-309 living plan update]
  PLAN --> MORE{Unvisited control?}
  MORE -->|yes| LOOP
  MORE -->|no| R2[MP-310 Round-2 miss hunt]
  R2 --> NAV[MP-311 FusionX recovery: blue-pixel / one address-bar]
  NAV --> XL[MP-312 Minimize Excel before capture]
  XL --> DONE[MP-313 complete_phase 3]
```

**Device atomic loop (every click — MP-800…811):**

```mermaid
flowchart LR
  EYES[capture full desktop] --> BRAIN[vision + ttp/laws decide]
  BRAIN --> HANDS[move → click/type/hotkey]
  HANDS --> WAIT[wait_frame]
  WAIT --> EYES
```

**Rules:** one headed session · mouse+keyboard after entry URL · no Pass/Fail in map · Round 2 folder must exist even if empty.

---

## 5) Phase 4 — Design (micro)

```mermaid
flowchart TD
  L[MP-400 Sigiri laws + gold steps + template] --> S[MP-401 split_paths P00…]
  S --> D[MP-402 draft Action|Data|Expected Result CSV]
  D --> V[MP-403 validate_steps + validate_title]
  V -->|fail| D
  V -->|pass| EP[MP-404 EP/BVA/state/RBAC/maker-checker]
  EP --> SUF[MP-405 sufficiency loop]
  SUF -->|not enough| D
  SUF -->|enough| AG[MP-406 agency designer dispatch]
  AG --> DONE[MP-407 complete_phase 4]
```

---

## 6) Phase 5 — Implementation / Xray UI RPA / Book1 scaffold (micro)

```mermaid
flowchart TD
  C[MP-500 createJiraIssue Test + link tests→Story] --> M[MP-501 xray_ui_method]
  M --> LOGIN[MP-502 xray_ui_ensure_login / Human Gate]
  LOGIN --> CSV[MP-503 ui_import_csv]
  CSV --> PACK[MP-504 ui_import_pack]
  PACK --> REG[MP-505 ui_import_registry / end_of_run_upload]
  REG --> API[MP-506 API fallback ONLY if Client Id/Secret]
  CSV --> RST[MP-507 force_reset wrong steps — never Esc]
  REG --> B1[MP-508 book1_sample scaffold]
  B1 --> DISK[MP-509 disk free ≥50MB]
  DISK --> DONE[MP-510 complete_phase 5]
```

**Xray dialog micro-sequence (never skip):**

1. Open Test issue headed  
2. Manual steps → **Import** → **From csv...**  
3. File chooser `#xray-csv-file` (not Attachments)  
4. Map columns **Action\*** | **Data** | **Expected Result**  
5. Validate → **Import Steps**  
6. If wrong steps: **Reset Current Test Steps** (`force_reset`) then re-import  
7. Playwright **Sync must be subprocess** under MCP asyncio (Perfect-100 lock)

---

## 7) Phase 6 — Execution + honesty + bugs (micro)

```mermaid
flowchart TD
  R[MP-600 role_start executor] --> STEP[MP-601 Eyes→Brain→Hands case step]
  STEP --> CDP[MP-602 CDP Playwright SPA fill]
  STEP --> MC[MP-603 maker→checker same window]
  STEP --> HS[MP-604 honesty_start]
  HS --> HA[MP-605 honesty_attempt ×≤20]
  HA --> OB[MP-606 obvious-class 3 repros]
  HA --> HV[MP-607 honesty_verdict]
  HV -->|PASS| B1[MP-611 Book1 append row + PNG]
  HV -->|REAL_BUG| BD[MP-608 bug draft + proof_crop]
  BD --> DD[MP-609 JQL dedupe]
  DD -->|twin open| REL[Relates + comment — no new Bug]
  DD -->|new| JB[MP-610 createJiraIssue Bug + attach PNG]
  JB --> B1
  B1 --> RV[MP-612 revalidate optional]
  RV --> AG[MP-613 agency evidence/reality]
  AG --> MORE{More cases?}
  MORE -->|yes| STEP
  MORE -->|no| DONE[MP-614 complete_phase 6]
```

---

## 8) Phase 7 — Completion (micro)

```mermaid
flowchart TD
  V[MP-700 book1_validate SHARE ≥110 / 100% images / gold_parity_ok] -->|fail| FIX[Fix Book1 — BLOCK share]
  V -->|pass| H3[MP-701 honesty triple cycle]
  H3 --> XU[MP-702 end_of_run Xray upload all packs]
  XU --> LR[MP-703 learn_cycle + learn_record]
  LR --> CM[MP-704 Story Perfect-100 closeout comment]
  CM --> DU[MP-705 dedupe Relates finalize]
  DU --> EV[MP-706 evaluate_all + complete_phase 7]
  EV --> TR[MP-707 optional agency retrain]
```

---

## 9) Perfect-100 lock + Stable V1 export (micro)

```mermaid
flowchart TD
  RUN[PF-59486 ISTQB 1→7 kit] --> DOC[skills/PERFECT-100-PF-59486-GOLD.md]
  DOC --> LAW[engineer_persona + laws v5 Absolute laws]
  LAW --> TRAIN[train_agency_qa.py → 279 overlays v2]
  TRAIN --> LEARN[liqa_learn_record]
  LEARN --> EXP[MP-A00 export entire chat]
  EXP --> RED[MP-A01 redact secrets]
  RED --> GH[MP-A02 push tags stable-v1 / v1.0.0-stable]
  GH --> MAP[MP-A03 publish this process-map]
```

---

## 10) Folders contract (every KEY)

```
assignedTasks/<KEY>/
UserStories/<KEY>/
ExistingTestCases/<KEY>/
map/<KEY>/          (+ round-2/)
knowledgeBase/<KEY>/jira-attachments/
NewTestCases/<KEY>/sigiri-manual/Pxx/
outputs/<KEY>/      Book1 SHARE xlsx
reports/proof/<KEY>/
bugs/<KEY>/
agents/mesh/<specialist>/
secrets/            (gitignored)
```

---

## 11) External MCP / systems in the flow

| System | Used for |
|--------|----------|
| **user-liqa** | All LIQA tools (98) |
| **user-atlassian** | Jira issues, links, comments, search |
| **user-theja-humanize / device** | Full-desktop Eyes→Hands when LIQA hands wrap it |
| **Playwright + CDP :9333** | FusionX SPA + Xray UI RPA subprocess |
| **agency-agents** | 279 specialist source roles |
| **GitHub thejanaloit/LIQA** | Stable V1 + process-map publish |

---

## 12) How to use this map

1. Open [`MICROPROCESSES.json`](MICROPROCESSES.json) for the full ID list (MP-xxx).  
2. Walk mermaid sections 0→9 in order — **do not skip micro gates**.  
3. Cross-check tools in [`LIQA-TOOLS.json`](LIQA-TOOLS.json).  
4. For narrative of what actually happened: [`../chat/FULL-CHAT.md`](../chat/FULL-CHAT.md).

**Completeness claim:** every ISTQB phase micro-step, device atomic, Xray UI RPA dialog step, honesty/Book1/bug-dedupe gate, agency mesh dispatch pattern, Perfect-100 lock, and Stable V1 export path from the entire process is mapped above and enumerated in `MICROPROCESSES.json`.
