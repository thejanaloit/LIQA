# Titles — match LOLC QA, not another company

## Xray Test / QA Story (FusionX PF) — GOLD

```
Lending Module | Receipt behaviors for migrated contracts  | Testcase writing and execution
```

PF-59194 · SIGIRI JAYASEKARA

Other live examples (other engineers):

- `Common Module | Dashboard | Post-EOD Monitory Dashboard (TD)` — UdariWi
- `TD Module| Deposit Register – Detail Report| Add Tax Number Column` — Piyumi Wickramarathna
- `Test Lending Module | Loan Origination | Subsequent Disbursement … | Test case Writing and Execution` — KamilaSu
- `Lending Module | Account Maintenance | Loan Account Cancellation | … | Loan Cancellation Workflow` — SIGIRI

Rules:

- Pipes `|` separate Module → Feature → path.
- Often ends with **Testcase writing and execution**.
- **No** `[FP]` brackets on new PF Tests.

## Forbidden on new PF Tests

```
[TD] [OwnerTransferHistory][FP] - Validate that …
Title: [Module] [Submodule][Feature][FP] - Validate that <behaviour>.
```

Those exist (Methmi / iPay-style). LIQA + Sigiri lock: do **not** copy that onto FusionX PF.

## LIQA path-split Tests (allowed overlay)

```
PF-59486 | P06 | Pending queue and navigation availability
```

Still pipes. Still no `[FP]`.
