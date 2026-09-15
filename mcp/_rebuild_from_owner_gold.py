"""Rebuild packs from owner PF-59194 (2).csv gold — exact 3 columns."""
from __future__ import annotations

import json
from pathlib import Path

import sigiri_xray_contract as s

STORY_KEY = "PF-58380"
STORY_SUMMARY = (
    "Lending Module | Receipt behaviors for migrated contracts  | Testcase writing and execution"
)

# Inclusive 1-based ranges on REPAIRED gold steps (after quirk merge)
PATHS = [
    {"id": "P00", "name": "Shell — full Manual (Sigiri twin)", "summary": STORY_SUMMARY, "slice": None},
    {"id": "P01", "name": "Access / Create / contract gate", "summary": "Lending Module | Receipt Reallocation | Access / Navigate | Testcase writing and execution", "slice": (1, 8)},
    {"id": "P02", "name": "Receipts filter + Excess toggles", "summary": "Lending Module | Receipt Reallocation | Excess Pay toggles | Testcase writing and execution", "slice": (9, 17)},
    {"id": "P03", "name": "Allocation edit + credit notes", "summary": "Lending Module | Receipt Reallocation | Allocation Edit | Testcase writing and execution", "slice": (18, 29)},
    {"id": "P04", "name": "Pending Auth + refund/reversal", "summary": "Lending Module | Receipt Reallocation | Pending Auth | Testcase writing and execution", "slice": (30, 41)},
    {"id": "P05", "name": "Account Inquiry / Receipt Details", "summary": "Lending Module | Account Inquiry | Receipt Details | Testcase writing and execution", "slice": (42, 57)},
    {"id": "P06", "name": "RBAC / session / audit / GL", "summary": "Lending Module | Receipt Reallocation | Security Audit GL | Testcase writing and execution", "slice": (58, 73)},
    {"id": "P07", "name": "Validation / grid / maker-checker / deps", "summary": "Lending Module | Receipt Reallocation | Validation | Testcase writing and execution", "slice": (74, 120)},
]


def main() -> None:
    gold = s.load_gold_steps()
    assert gold["ok"], gold
    all_steps = gold["steps"]
    print("gold_repaired", gold["count"], "contract", s.CONTRACT_VERSION)

    s.split_story_paths(
        STORY_KEY,
        "Receipt reallocation full gold themes",
        paths_json=json.dumps([{"id": p["id"], "name": p["name"], "hint": p["summary"]} for p in PATHS]),
    )

    packs = []
    for p in PATHS:
        if p["slice"] is None:
            steps = all_steps
        else:
            a, b = p["slice"]
            steps = all_steps[a - 1 : min(b, len(all_steps))]
        v = s.validate_steps(steps)
        if not v["ok"]:
            print("FAIL", p["id"], v["reasons"][:5])
            continue
        pack = s.build_manual_pack(STORY_KEY, p["id"], p["name"], json.dumps(v["steps"]), summary=p["summary"])
        print(p["id"], pack["ok"], pack.get("step_count"), pack.get("csv"))
        packs.append({"id": p["id"], "summary": p["summary"], "steps": pack.get("step_count"), "csv": pack.get("csv")})

    out = Path(s.WORKSPACE) / "NewTestCases" / STORY_KEY / "sigiri-manual" / "gold-rebuild.json"
    out.write_text(
        json.dumps(
            {
                "gold_source": "PF-59194 (2).csv",
                "contract": s.CONTRACT_VERSION,
                "gold_count": gold["count"],
                "packs": packs,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("wrote", out)


if __name__ == "__main__":
    main()
