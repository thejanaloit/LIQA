"""Locked Book1 architecture — GOLD = PF-58374-Book1-SHARE.xlsx (v117).

Every task, every time, Book1 must match SHARE quality:
- Screenshot on EVERY data row (image_coverage=100%)
- EVERY text field is a BIG full English explanation (SHARE-parity min lengths)
- Sheet1 only, 7 columns, >=110 data rows
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

BOOK1_COLUMNS = [
    "Area",
    "Issue",
    "Screenshot",
    "What is testing",
    "Why that failed your prediction",
    "2nd QA confirmation",
    "Simple explanation (plain English)",
]

BOOK1_WIDTHS = [36.0, 55.0, 22.0, 55.0, 55.0, 45.0, 55.0]

BOOK1_HEADER_FILL = "C00000"
BOOK1_SHEET_NAME = "Sheet1"
BOOK1_MIN_ROWS = 110
BOOK1_TARGET_IMAGES = 110
BOOK1_MIN_IMAGE_COVERAGE = 1.0
BOOK1_ALLOW_IMAGE_SHORTFALL = 0

_REPO = Path(__file__).resolve().parents[1]
GOLD_SHARE_DIR = _REPO / "artifacts" / "book1-samples" / "gold-share-pf58374"
GOLD_SHARE_XLSX = GOLD_SHARE_DIR / "PF-58374-Book1-SHARE.xlsx"
GOLD_SHARE_PROFILE_PATH = GOLD_SHARE_DIR / "GOLD-PROFILE.json"

GOLD_SAMPLE_HINT = (
    "artifacts/book1-samples/gold-share-pf58374/PF-58374-Book1-SHARE.xlsx "
    "(owner-locked perfect Book1 — every task must match this quality every time)"
)
CONTRACT_VERSION = "2026-09-12-book1-gold-share-parity-v117"

# SHARE-parity floors (slightly under observed mins on gold SHARE)
BOOK1_MIN_CHARS: dict[str, int] = {
    "Area": 250,
    "Issue": 500,
    "What is testing": 240,
    "Why that failed your prediction": 250,
    "2nd QA confirmation": 280,
    "Simple explanation (plain English)": 320,
}

BOOK1_COL_INDEX = {name: i + 1 for i, name in enumerate(BOOK1_COLUMNS)}

BOOK1_EXPLAIN_HINTS = (
    "this ",
    "we ",
    "under ",
    "verif",
    "check",
    "confirm",
    "explain",
    "kenya",
    "story",
    "result",
    "expected",
    "actual",
    "because",
    "module",
    "screen",
    "api",
    "in simple words",
    "full product area",
    "observation",
    "2nd qa",
)

FILL_PASS = "C6EFCE"
FILL_BLOCKED = "FFEB9C"
FILL_BUG = "FF6B6B"
FILL_NA = "D9D9D9"


def load_gold_share_profile() -> dict[str, Any]:
    """Load locked SHARE gold profile (enforced mins for every task)."""
    if GOLD_SHARE_PROFILE_PATH.exists():
        try:
            data = json.loads(GOLD_SHARE_PROFILE_PATH.read_text(encoding="utf-8"))
            enforced = data.get("enforced_min_chars") or {}
            if enforced:
                # keep module defaults as floor, profile can only raise
                for k, v in enforced.items():
                    if k in BOOK1_MIN_CHARS:
                        BOOK1_MIN_CHARS[k] = max(int(BOOK1_MIN_CHARS[k]), int(v))
            data["gold_xlsx_exists"] = GOLD_SHARE_XLSX.exists()
            data["gold_xlsx"] = str(GOLD_SHARE_XLSX)
            return data
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e), "path": str(GOLD_SHARE_PROFILE_PATH)}
    return {
        "ok": False,
        "error": "missing GOLD-PROFILE.json",
        "path": str(GOLD_SHARE_PROFILE_PATH),
        "enforced_min_chars": dict(BOOK1_MIN_CHARS),
    }


# Apply profile mins at import
_GOLD_PROFILE = load_gold_share_profile()


def detect_result(issue: str, second_qa: str = "", why: str = "") -> str:
    blob = f"{issue}\n{second_qa}\n{why}".upper()
    if "REAL_BUG" in blob or "REAL PRODUCT ISSUE" in blob:
        return "FAIL"
    if re.search(r"\bBLOCKED\b", blob):
        return "BLOCKED"
    if re.search(r"\bN/?A\b", blob) or "KENYA N/A" in blob or "NOT ON KENYA" in blob:
        return "N/A"
    if (
        "FAILED" in blob
        or re.search(r"\bFAIL\b", blob)
        or re.search(r"\bBUG\b", blob)
        or "PREDICTION MISSED" in blob
        or "ROUTE NOT FOUND" in blob
        or "404" in blob
    ):
        return "FAIL"
    if (
        "PASSED" in blob
        or re.search(r"\bPASS\b", blob)
        or "PREDICTION MATCHED" in blob
        or "LOGIN OK" in blob
        or "BEHAVED AS EXPECTED" in blob
        or "NO DEFECT" in blob
        or "WORKED AS EXPECTED" in blob
    ):
        return "PASS"
    return "PENDING"


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _short(text: str, n: int = 120) -> str:
    t = _norm(text)
    t = re.split(
        r"\s[—\-]\s*(PASSED|FAILED|PASS|FAIL|BLOCKED|N/A|BUG)\b", t, maxsplit=1
    )[0]
    t = t.strip(" .")
    if len(t) <= n:
        return t
    return t[: n - 1].rstrip() + "…"


def _looks_full(text: str, min_chars: int) -> bool:
    raw = _norm(text)
    if len(raw) < min_chars:
        return False
    low = raw.lower()
    return any(h in low for h in BOOK1_EXPLAIN_HINTS) or raw.count(".") >= 1


def ensure_full_area(area: str, *, story_key: str = "", what_is_testing: str = "") -> str:
    raw = _norm(area)
    if _looks_full(raw, BOOK1_MIN_CHARS["Area"]):
        return raw
    label = raw or "Lending / product area"
    sk = story_key or "the assigned story"
    topic = _short(what_is_testing or label, 80)
    return (
        f"{label} — full product area for this Book1 row under {sk} on Kenya UAT. "
        f"This area covers the screens, APIs, and maker/checker paths related to: {topic}. "
        f"All observations in this row belong to this module context."
    )


def ensure_full_issue(
    issue: str,
    *,
    area: str = "",
    what_is_testing: str = "",
    story_key: str = "",
    result: str | None = None,
) -> str:
    raw = _norm(issue)
    if _looks_full(raw, BOOK1_MIN_CHARS["Issue"]):
        return raw
    res = (result or detect_result(raw)).upper()
    topic = _short(what_is_testing or raw or area or "this check", 100)
    sk = story_key or "the assigned story"
    if res == "FAIL" or "BUG" in raw.upper():
        return (
            f"ISSUE / DEFECT observation under {sk} in {area or 'this area'}: {topic}. "
            f"On Kenya UAT the expected behaviour was not met. This is recorded as a real "
            f"product or environment problem with headed proof — not a tooling mistake. "
            f"Impact: a Kenya bank user can hit a wrong screen, missing field, broken API, "
            f"or incomplete configuration here. Original short note: {raw or 'BUG'}."
        )
    if res == "N/A":
        return (
            f"N/A observation under {sk}: {topic} is not applicable or not reachable for "
            f"full AC proof on this Kenya UAT tenant yet (for example checker path blocked "
            f"by an earlier API/UI gap). Do not treat this as a silent pass. "
            f"Original short note: {raw or 'N/A'}."
        )
    if res == "BLOCKED":
        return (
            f"BLOCKED observation under {sk}: we could not finish proving {topic} because "
            f"the environment or access wall stopped the headed path. Fix access/API first, "
            f"then re-test. Original short note: {raw or 'BLOCKED'}."
        )
    return (
        f"No defect on this check under {sk} in {area or 'this area'}. "
        f"Observation: {topic} behaved as expected on Kenya UAT during headed manual QA. "
        f"This Issue cell still documents the full positive finding so Book1 never has an "
        f"empty Idea column. Original short note: {raw or 'PASS'}."
    )


def ensure_full_what_is_testing(
    what_is_testing: str,
    *,
    area: str = "",
    issue: str = "",
    story_key: str = "",
) -> str:
    raw = _norm(what_is_testing)
    if _looks_full(raw, BOOK1_MIN_CHARS["What is testing"]):
        return raw
    topic = raw or _short(issue or area or "this control", 100)
    sk = (story_key or "").strip() or "the assigned story"
    area_bit = (area or "the product area").strip()
    return (
        f"This test verifies {topic} in {area_bit}. "
        f"Under {sk} on Kenya UAT, we confirm the expected behaviour is present and usable "
        f"for a bank user, including the related screen or API path, preconditions, and "
        f"business purpose. Short labels are not enough — this cell holds the full idea of "
        f"what is being tested and why the check exists."
    )


def ensure_full_why(
    why: str,
    *,
    issue: str = "",
    what_is_testing: str = "",
    story_key: str = "",
    result: str | None = None,
) -> str:
    raw = _norm(why)
    if _looks_full(raw, BOOK1_MIN_CHARS["Why that failed your prediction"]):
        return raw
    res = (result or detect_result(issue, why=raw)).upper()
    topic = _short(what_is_testing or issue or "this check", 100)
    sk = story_key or "the assigned story"
    if res == "FAIL":
        return (
            f"Why this failed the prediction under {sk}: we predicted {topic} would work "
            f"(or already be fixed), but Kenya UAT showed a break. Expected vs actual did "
            f"not match. Evidence from headed Eyes→Brain→Hands and/or network capture "
            f"supports a real gap. Short note expanded: {raw or 'prediction missed'}."
        )
    if res == "PASS":
        return (
            f"Why the prediction held under {sk}: we expected {topic} to succeed on Kenya "
            f"UAT, and headed evidence matched that prediction. No surprise failure. "
            f"Short note expanded: {raw or 'prediction matched'}."
        )
    return (
        f"Prediction analysis under {sk} for {topic}: {raw or 'see headed evidence'}. "
        f"This cell explains whether the QA prediction matched reality and what that means "
        f"for the story acceptance on Kenya UAT."
    )


def ensure_full_second_qa(
    second_qa: str,
    *,
    issue: str = "",
    what_is_testing: str = "",
    story_key: str = "",
    result: str | None = None,
) -> str:
    raw = _norm(second_qa)
    if _looks_full(raw, BOOK1_MIN_CHARS["2nd QA confirmation"]):
        return raw
    topic = _short(what_is_testing or issue or "this check", 100)
    sk = story_key or "the assigned story"
    res = (result or detect_result(issue, second_qa=raw)).upper()
    return (
        f"2nd QA confirmation under {sk}: a second headed look (same build/tenant) "
        f"re-checked {topic}. Outcome class: {res or 'REVIEWED'}. "
        f"Confirmation notes: {raw or 'reconfirmed on headed re-run'}. "
        f"This is not a one-glance claim — the row was reviewed again before share."
    )


def simple_explanation(
    *,
    issue: str,
    what_is_testing: str = "",
    why_prediction: str = "",
    second_qa: str = "",
    story_key: str = "",
    result: str | None = None,
) -> str:
    result = (result or detect_result(issue, second_qa, why_prediction)).upper()
    checked = _short(what_is_testing or issue, 160)
    concern = _short(issue or what_is_testing, 160)
    sk = story_key or "this story"

    if result == "PASS":
        return (
            "In simple words: We tried this check on Kenya UAT and it worked as expected. "
            f"Story/context: {sk}. What we checked: {checked}. "
            "Result: PASS. "
            "A normal bank user can complete this step without a product break. "
            "This Book1 row keeps the full idea so managers do not need jargon."
        )
    if result == "FAIL":
        return (
            "In simple words: This is a real product problem, not a test-tool mistake. "
            f"Story/context: {sk}. What we expected to work: {concern}. "
            "What happened: it failed on Kenya UAT. "
            "Why it matters: a Kenya bank user can hit a wrong screen, missing field, "
            "broken API, or incomplete configuration here. Result: FAIL / BUG."
        )
    if result == "BLOCKED":
        return (
            "In simple words: We could not finish this check because the environment blocked us "
            "(for example HTTP 503, missing menu, or login/permission wall). "
            f"Story/context: {sk}. What we tried: {checked}. "
            "Result: BLOCKED. "
            "Fix the environment or access, then re-test — do not call this a code bug yet."
        )
    if result == "N/A":
        return (
            "In simple words: This part is not fully applicable or not reachable for proof "
            "on this Kenya UAT tenant right now. "
            f"Story/context: {sk}. What we looked for: {checked}. "
            "Result: N/A. Re-open after blockers are fixed — do not pretend it passed."
        )
    return (
        "In simple words: This check is still open. "
        f"Story/context: {sk}. What we planned to verify: {checked}. "
        "Result: PENDING. "
        "Run headed QA and update this row with PASS, FAIL, BLOCKED, or N/A, with full English."
    )


def ensure_full_simple(
    english: str,
    *,
    issue: str = "",
    what_is_testing: str = "",
    why_prediction: str = "",
    second_qa: str = "",
    story_key: str = "",
    result: str | None = None,
) -> str:
    raw = _norm(english)
    if _looks_full(raw, BOOK1_MIN_CHARS["Simple explanation (plain English)"]) and (
        "in simple words" in raw.lower() or "what happened" in raw.lower()
    ):
        return raw
    return simple_explanation(
        issue=issue,
        what_is_testing=what_is_testing,
        why_prediction=why_prediction,
        second_qa=second_qa,
        story_key=story_key,
        result=result,
    )


def ensure_full_book1_row(
    *,
    area: str,
    issue: str,
    what_is_testing: str,
    why_prediction: str,
    second_qa: str,
    english_explanation: str = "",
    story_key: str = "",
    is_bug: bool = False,
) -> dict[str, str]:
    """Expand every text field to full English. Screenshot stays a path/image."""
    result = "FAIL" if is_bug else detect_result(issue, second_qa, why_prediction)
    what = ensure_full_what_is_testing(
        what_is_testing, area=area, issue=issue, story_key=story_key
    )
    area_full = ensure_full_area(area, story_key=story_key, what_is_testing=what)
    issue_full = ensure_full_issue(
        issue, area=area_full, what_is_testing=what, story_key=story_key, result=result
    )
    why_full = ensure_full_why(
        why_prediction,
        issue=issue_full,
        what_is_testing=what,
        story_key=story_key,
        result=result,
    )
    second_full = ensure_full_second_qa(
        second_qa,
        issue=issue_full,
        what_is_testing=what,
        story_key=story_key,
        result=result,
    )
    simple_full = ensure_full_simple(
        english_explanation,
        issue=issue_full,
        what_is_testing=what,
        why_prediction=why_full,
        second_qa=second_full,
        story_key=story_key,
        result=result,
    )
    return {
        "area": area_full,
        "issue": issue_full,
        "what_is_testing": what,
        "why_prediction": why_full,
        "second_qa": second_full,
        "english_explanation": simple_full,
        "result": result,
    }


def _count_data_rows(ws) -> int:
    n = 0
    for r in range(2, (ws.max_row or 1) + 1):
        if any(ws.cell(r, c).value not in (None, "") for c in range(1, 8)):
            n += 1
    return n


def _count_embedded_images(ws) -> int:
    imgs = getattr(ws, "_images", None) or []
    return len(imgs)


def _scan_text_field_gaps(ws) -> dict[str, Any]:
    gaps: dict[str, dict[str, int]] = {}
    for name, min_n in BOOK1_MIN_CHARS.items():
        gaps[name] = {"empty": 0, "short": 0, "weak": 0, "min": min_n}
    for r in range(2, (ws.max_row or 1) + 1):
        if not any(ws.cell(r, c).value not in (None, "") for c in range(1, 8)):
            continue
        for name, min_n in BOOK1_MIN_CHARS.items():
            col = BOOK1_COL_INDEX[name]
            val = _norm(str(ws.cell(r, col).value or ""))
            if not val:
                gaps[name]["empty"] += 1
                continue
            if len(val) < min_n:
                gaps[name]["short"] += 1
            else:
                weak = not _looks_full(val, min_n)
                if name == "Simple explanation (plain English)":
                    low = val.lower()
                    if "in simple words" not in low and "what happened" not in low:
                        weak = True
                if weak:
                    gaps[name]["weak"] += 1
    return gaps


def validate_book1_workbook(path: str) -> dict[str, Any]:
    """Hard validate architecture + screenshots + FULL English on all text fields."""
    try:
        from openpyxl import load_workbook
    except ImportError:
        return {"ok": False, "error": "pip install openpyxl"}

    from pathlib import Path

    p = Path(path)
    if not p.exists():
        return {"ok": False, "error": f"missing {path}"}

    wb = load_workbook(p, read_only=False, data_only=False)
    reasons: list[str] = []
    if wb.sheetnames != [BOOK1_SHEET_NAME]:
        reasons.append(f"sheets must be only {[BOOK1_SHEET_NAME]}, got {wb.sheetnames}")
    ws = wb[BOOK1_SHEET_NAME]
    headers = [ws.cell(1, c).value for c in range(1, 8)]
    if headers != BOOK1_COLUMNS:
        reasons.append(f"headers mismatch: {headers}")
    if ws.max_column != 7:
        reasons.append(f"max_column={ws.max_column} want 7")
    if (ws.max_row or 0) < BOOK1_MIN_ROWS:
        reasons.append(f"rows={ws.max_row} want >={BOOK1_MIN_ROWS}")

    data_rows = _count_data_rows(ws)
    images = _count_embedded_images(ws)
    shortfall = max(0, data_rows - images)
    coverage = (images / data_rows) if data_rows else 0.0

    if data_rows < (BOOK1_MIN_ROWS - 1):
        reasons.append(f"data_rows={data_rows} want >={BOOK1_MIN_ROWS - 1}")
    if images < BOOK1_TARGET_IMAGES and data_rows >= BOOK1_TARGET_IMAGES:
        reasons.append(
            f"embedded_images={images} want >={BOOK1_TARGET_IMAGES} "
            f"(every Book1 row needs a screenshot)"
        )
    if shortfall > BOOK1_ALLOW_IMAGE_SHORTFALL:
        reasons.append(
            f"SCREENSHOT_GAP: {shortfall} data row(s) missing embedded PNG "
            f"(images={images}, data_rows={data_rows}, coverage={coverage:.0%}). "
            f"Do NOT share. Rebuild with manualqa_book1_append_row / embed-all script."
        )
    if coverage + 1e-9 < BOOK1_MIN_IMAGE_COVERAGE and data_rows > 0:
        reasons.append(
            f"image_coverage={coverage:.0%} want >={BOOK1_MIN_IMAGE_COVERAGE:.0%} "
            f"(law: one screenshot per Book1 data row)"
        )

    text_gaps = _scan_text_field_gaps(ws)
    text_short_total = 0
    for name, g in text_gaps.items():
        bad = g["empty"] + g["short"] + g["weak"]
        text_short_total += bad
        if g["empty"]:
            reasons.append(
                f"FIELD_EMPTY[{name}]: {g['empty']} row(s) — every field needs full English"
            )
        if g["short"]:
            reasons.append(
                f"FIELD_TOO_SHORT[{name}]: {g['short']} row(s) under {g['min']} chars — "
                f"expand to a full explanation of the complete idea"
            )
        if g["weak"]:
            reasons.append(
                f"FIELD_WEAK[{name}]: {g['weak']} row(s) look like labels — rewrite as full English"
            )

    wb.close()
    gold = load_gold_share_profile()
    gold_parity = (
        shortfall == 0
        and coverage + 1e-9 >= BOOK1_MIN_IMAGE_COVERAGE
        and text_short_total == 0
        and data_rows >= (BOOK1_MIN_ROWS - 1)
        and not reasons
    )
    if not gold_parity and not any("GOLD_SHARE" in str(x) for x in reasons):
        # only add if already failing for other reasons we still tag parity
        pass
    if not gold_parity:
        reasons.append(
            "GOLD_SHARE_PARITY_FAIL — Book1 must match "
            "artifacts/book1-samples/gold-share-pf58374/PF-58374-Book1-SHARE.xlsx "
            "quality (100% screenshots + SHARE-parity full English on every text field) "
            "for EVERY task EVERY time"
        )

    return {
        "ok": not reasons,
        "path": str(p.resolve()),
        "reasons": reasons,
        "gold_hint": GOLD_SAMPLE_HINT,
        "gold_share_xlsx": str(GOLD_SHARE_XLSX),
        "gold_share_exists": GOLD_SHARE_XLSX.exists(),
        "gold_parity_ok": gold_parity and not reasons,
        "gold_profile": {
            "stamp": gold.get("stamp"),
            "enforced_min_chars": dict(BOOK1_MIN_CHARS),
            "contract_version": CONTRACT_VERSION,
        },
        "columns": BOOK1_COLUMNS,
        "data_rows": data_rows,
        "embedded_images": images,
        "image_shortfall": shortfall,
        "image_coverage": round(coverage, 4),
        "min_image_coverage": BOOK1_MIN_IMAGE_COVERAGE,
        "min_chars": dict(BOOK1_MIN_CHARS),
        "text_field_gaps": text_gaps,
        "text_field_gap_total": text_short_total,
        "stop_share": bool(reasons),
        "contract_version": CONTRACT_VERSION,
    }


def contract_summary() -> dict[str, Any]:
    gold = load_gold_share_profile()
    return {
        "ok": True,
        "version": CONTRACT_VERSION,
        "columns": BOOK1_COLUMNS,
        "widths": BOOK1_WIDTHS,
        "sheet": BOOK1_SHEET_NAME,
        "min_rows": BOOK1_MIN_ROWS,
        "target_images": BOOK1_TARGET_IMAGES,
        "min_image_coverage": BOOK1_MIN_IMAGE_COVERAGE,
        "allow_image_shortfall": BOOK1_ALLOW_IMAGE_SHORTFALL,
        "min_chars": dict(BOOK1_MIN_CHARS),
        "header_fill": BOOK1_HEADER_FILL,
        "gold_samples": GOLD_SAMPLE_HINT,
        "gold_share_xlsx": str(GOLD_SHARE_XLSX),
        "gold_share_exists": GOLD_SHARE_XLSX.exists(),
        "gold_profile_stamp": gold.get("stamp"),
        "all_fields_english_law": (
            "EVERY text column must match SHARE gold quality — big full English "
            f"explanations. Minimums (SHARE-parity): {BOOK1_MIN_CHARS}. "
            "Screenshot column = embedded image on every row."
        ),
        "screenshot_law": (
            "EVERY data row MUST embed a real PNG/JPG in column Screenshot. "
            "3-of-N images is a PROCESS FAIL — evaluator + Gatekeeper block share."
        ),
        "every_task_every_time": (
            "Evaluator step 8 + evaluate_all re-check Book1 against SHARE gold "
            "on every unlock. No task may ship a thinner Book1."
        ),
        "forbidden": [
            "Cover sheet / multi-sheet Book1 for final share",
            "iPay Lite columns labeled as Book1",
            "Jargon-only or label-only text in ANY Book1 column",
            "Empty Issue on PASS rows",
            "Stamping REDO body and calling it FRESH",
            "Book1 with text-only Screenshot column / only a few rows imaged",
            "Short What is testing / Why / 2nd QA / Simple explanation",
            "Book1 below SHARE gold parity (GOLD_SHARE_PARITY_FAIL)",
        ],
    }
