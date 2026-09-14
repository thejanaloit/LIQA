"""Book1 + iPay-lite matrices. ≥110 rows optional per tenant."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

OUT = Path(__file__).resolve().parents[2] / "reports"
OUT.mkdir(parents=True, exist_ok=True)

BOOK1_COLS = [
    "Area",
    "Issue",
    "Screenshot",
    "What is testing",
    "Why that failed your prediction",
    "2nd QA confirmation",
    "Simple explanation (plain English)",
]
IPAY_COLS = ["Area", "Concern", "User story", "Status", "Change made?", "Change / verification notes (English)", "Commit / cycle"]


def _rows(n: int, cols: list[str], story: str) -> list[dict[str, str]]:
    rows = []
    for i in range(1, n + 1):
        row = {c: "" for c in cols}
        row[cols[0]] = "LIQA"
        row[cols[1]] = f"Case {i:03d} for {story[:80]}"
        if "Simple explanation" in cols:
            row["Simple explanation (plain English)"] = f"In simple words: check case {i}. Result: not executed yet."
        if "Concern" in cols:
            row["Concern"] = f"Failure risk #{i}: behaviour must hold for {story[:60]}"
            row["User story"] = story[:120]
            row["Status"] = "Not executed"
            row["Change / verification notes (English)"] = "Execute headed. Attach PNG."
        rows.append(row)
    return rows


def generate_book1(story: str, n: int = 110) -> dict[str, Any]:
    rows = _rows(max(110, n), BOOK1_COLS, story)
    p = OUT / "book1-latest.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=BOOK1_COLS)
        w.writeheader()
        w.writerows(rows)
    meta = {"ok": True, "path": str(p), "rows": len(rows), "xlsx_note": "CSV first; embed PNG in Excel on Worker with openpyxl when licensed."}
    (OUT / "book1-latest.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def generate_ipay(story: str, n: int = 110) -> dict[str, Any]:
    rows = _rows(max(110, n), IPAY_COLS, story)
    p = OUT / "ipay-lite-latest.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=IPAY_COLS)
        w.writeheader()
        w.writerows(rows)
    return {"ok": True, "path": str(p), "rows": len(rows)}


def validate_book1(min_rows: int = 110) -> dict[str, Any]:
    p = OUT / "book1-latest.csv"
    if not p.exists():
        return {"ok": False, "reason": "no book1 yet"}
    with p.open(encoding="utf-8") as f:
        n = sum(1 for _ in f) - 1
    return {"ok": n >= min_rows, "rows": n, "min": min_rows}
