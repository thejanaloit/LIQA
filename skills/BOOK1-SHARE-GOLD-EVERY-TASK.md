# Book1 SHARE gold law (v117)

## Locked perfect sample

`artifacts/book1-samples/gold-share-pf58374/PF-58374-Book1-SHARE.xlsx`

Owner verdict: this output is **really perfect**. Every future task Book1 must match
this quality **every time**.

## Required every task

| Rule | Value |
|------|--------|
| Sheet | Sheet1 only |
| Columns | Area \| Issue \| Screenshot \| What is testing \| Why \| 2nd QA \| Simple |
| Data rows | ≥110 |
| Screenshots | embedded_images == data_rows (100%) |
| Area | ≥250 chars full English |
| Issue | ≥500 chars (never empty) |
| What is testing | ≥240 chars |
| Why prediction | ≥250 chars |
| 2nd QA | ≥280 chars |
| Simple explanation | ≥320 chars, starts with `In simple words:` |

## Enforcement

- `manualqa_validate_book1` → `gold_parity_ok` / `GOLD_SHARE_PARITY_FAIL`
- Evaluator step 8: `require_book1_gold_share_parity`
- `evaluate_all_steps` when through≥8 re-checks Book1 gold every time
- n8n `book1_validate` requires `book1GoldParityOk`

## Operator

Before share: validate must return `ok:true` and `gold_parity_ok:true`.
If not, expand with `ensure_full_book1_row` / embed-all — do not ship thinner Book1.
