# Sigiri Gold — Complete Idea (PF-59194 owner export)

Source: `c:\Users\ThejanaD\Downloads\PF-59194 (2).csv`  
Canonical LIQA copy: `artifacts/xray-gold-pf59194/PF-59194-steps.csv`  
Story shell: [PF-55248](https://lolcgroupdev.atlassian.net/browse/PF-55248)  
Test: [PF-59194](https://lolcgroupdev.atlassian.net/browse/PF-59194)

## Format lock (not even a decimal difference)

| Column | Rule |
|--------|------|
| **Action** | Short imperative / navigate / observe / attempt / verify |
| **Data** | Always empty in this gold (120/120) |
| **Expected Result** | Short outcome; UI quotes allowed |

CSV header exactly:

```text
Action,Data,Expected Result
```

No Attachments column in the owner export. No FP bracket titles. No novels.

## Volume

- **120** Manual steps in one shell Test (summary = Story summary).
- Language: direct FusionX QA English (Sigiri / TestCrafters).

## Path themes inside the shell (for path-split when writing NEW packs)

1. Access / navigate / Create New / contract gate  
2. Active vs cancelled receipts  
3. Excess Pay toggles  
4. Update Transaction Type / latest-first allocation edit  
5. Credit notes  
6. Pending → Approve / Reject / Return + View Transaction Type  
7. Refund / Reversal after approve  
8. Account Inquiry → Receipt Details / TR Number / Allocation Status  
9. Outstanding / Installment reflection  
10. RBAC / no-permission / API block  
11. Session timeout  
12. Audit trail  
13. GL posting  
14. Mandatory / min-max / date format validation  
15. Grid columns / pagination / search  
16. Missing definitions / allocation order / delete dependencies  
17. Maker–Checker  
18. Final AI sync after reallocation / reverse / refund  

## Export quirk (LIQA repair)

Rows 86 and 107 put the Expected text into **Action** with empty Expected.  
LIQA `load_gold_steps` merges those into the previous/current Expected so guards stay clean.  
When **writing new** steps, never emit that quirk — always fill Expected Result.

## LIQA workflow forever

1. English doctrine first  
2. `liqa_xray_split_paths` on user story  
3. Draft steps **exactly** like this CSV  
4. `liqa_xray_validate_steps` (guard)  
5. `liqa_xray_build_manual_test` → CSV  
6. Create ADD NEW Xray Test (pipe title or story-equal shell)  
7. Link type **Test** → Story  
8. `liqa_xray_import_csv` / `liqa_xray_import_pack` (needs Xray API keys)  

## Anti-patterns (blocked)

- `[Lending][…][FP] - Validate that…` titles  
- please/kindly/ensure that in Action  
- Multi-paragraph steps  
- Missing Expected Result on authored steps  
