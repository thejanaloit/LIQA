# Book1 ALL-FIELDS full English law (v115 / PF-58374 miss)

## Law

Every Book1 **text** cell must be a **big full English explanation** that contains
the complete idea. Short labels are a **process FAIL**.

| Column | Must contain |
|--------|----------------|
| Area | Full module/context paragraph (not just `PERC`) |
| Issue | Full observation — even PASS rows (never empty) |
| Screenshot | Embedded PNG/JPG (image, not text) |
| What is testing | Full verification design explanation |
| Why that failed your prediction | Full expected-vs-actual / prediction analysis |
| 2nd QA confirmation | Full second-look confirmation narrative |
| Simple explanation | Manager plain English (`In simple words: …`) long enough |

## Minimums (enforced)

See `BOOK1_MIN_CHARS` in `mcp/book1_contract.py` (v115+).

## Fail codes

- `FIELD_EMPTY[…]`
- `FIELD_TOO_SHORT[…]`
- `FIELD_WEAK[…]`
- plus existing `SCREENSHOT_GAP`

## Evaluator

Step 8: `require_book1_full_english` + `require_book1_screenshots`.
Share blocked until `manualqa_validate_book1` → `ok: true`.

## Tools

- `ensure_full_book1_row(...)` on append
- `scripts/pf58374_book1_expand_all_fields.py` rebuild pattern
- `manualqa_validate_book1(path)`
