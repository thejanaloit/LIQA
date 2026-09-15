"""Build Sigiri path packs from PF-59194 gold and emit create payload."""
from __future__ import annotations

import json
from pathlib import Path

import sigiri_xray_contract as s

STORY_KEY = "PF-58380"
STORY_SUMMARY = (
    "Lending Module | Receipt behaviors for migrated contracts  | Testcase writing and execution"
)
GOLD_STORY = "PF-55248"

# Path slices into gold step index ranges (1-based inclusive) — same CSV order as PF-59194
PATHS = [
    {
        "id": "P00",
        "name": "Shell — full Manual (Sigiri twin)",
        "summary": STORY_SUMMARY,
        "slice": None,  # all gold steps
    },
    {
        "id": "P01",
        "name": "Access and open Receipt Reallocation",
        "summary": "Lending Module | Receipt Reallocation | Access / Navigate | Testcase writing and execution",
        "slice": (1, 5),
    },
    {
        "id": "P02",
        "name": "Create New and contract selection",
        "summary": "Lending Module | Receipt Reallocation | Create New | Testcase writing and execution",
        "slice": None,
        "rebuild": "create",
    },
    {
        "id": "P03",
        "name": "Excess Pay toggles",
        "summary": "Lending Module | Receipt Reallocation | Excess Pay toggles | Testcase writing and execution",
        "slice": (14, 17),
        "nav_prefix": True,
    },
    {
        "id": "P04",
        "name": "Pending Approve Reject Return",
        "summary": "Lending Module | Receipt Reallocation | Pending Auth | Testcase writing and execution",
        "slice": (30, 37),
        "nav_prefix": True,
    },
    {
        "id": "P05",
        "name": "Validation — contract required",
        "summary": "Lending Module | Receipt Reallocation | Validation | Testcase writing and execution",
        "slice": (1, 6),
    },
]


def nav_prefix() -> list[dict[str, str]]:
    return [
        {
            "Action": "Log in as a user with Receipt Reallocation access",
            "Data": "",
            "Expected Result": "User is logged in successfully",
        },
        {
            "Action": "Navigate to 'Loan Origination and Management'",
            "Data": "",
            "Expected Result": "The main module screen is displayed",
        },
        {
            "Action": "Navigate to 'Transaction Management' > 'Receipt Reallocation'",
            "Data": "",
            "Expected Result": "The Receipt Reallocation screen is displayed with available options",
        },
    ]


def create_block() -> list[dict[str, str]]:
    return nav_prefix() + [
        {
            "Action": "Observe the validation message",
            "Data": "",
            "Expected Result": 'Validation message: "Please select a contract before proceeding" is displayed',
        },
        {
            "Action": "Verify that the 'Create New' button is visible",
            "Data": "",
            "Expected Result": "'Create New' button is visible and enabled",
        },
        {
            "Action": "On the Receipt Reallocation screen, click 'Create New' without selecting a contract",
            "Data": "",
            "Expected Result": "System prompts for contract selection",
        },
        {
            "Action": "Select a valid contract from the list",
            "Data": "",
            "Expected Result": "Contract details are displayed automatically",
        },
        {
            "Action": "Click 'Create New' again",
            "Data": "",
            "Expected Result": "New reallocation form is displayed for the selected contract",
        },
    ]


def main() -> None:
    gold = s.load_gold_steps()
    assert gold["ok"], gold
    all_steps: list[dict[str, str]] = gold["steps"]

    split = s.split_story_paths(
        STORY_KEY,
        "Receipt reallocation pending approve account inquiry receipt details excess toggle validation create new",
        paths_json=json.dumps(
            [{"id": p["id"], "name": p["name"], "hint": p["summary"]} for p in PATHS]
        ),
    )
    print("split", split["ok"], len(split["paths"]))

    results = []
    for p in PATHS:
        if p.get("rebuild") == "create":
            steps = create_block()
        elif p["slice"] is None:
            steps = all_steps
        else:
            a, b = p["slice"]
            steps = all_steps[a - 1 : b]
            if p.get("nav_prefix") and a > 3:
                # avoid duplicate login if slice already starts at 1
                prefix = nav_prefix()
                # dedupe if first actions overlap
                if not steps or steps[0]["Action"] != prefix[0]["Action"]:
                    steps = prefix + steps

        # Drop gold steps that use filler "Verify that the system" if any — gold is clean
        v = s.validate_steps(steps)
        if not v["ok"]:
            print("FAIL", p["id"], v["reasons"])
            continue
        pack = s.build_manual_pack(
            STORY_KEY,
            p["id"],
            p["name"],
            json.dumps(v["steps"]),
            summary=p["summary"],
        )
        print(p["id"], pack["ok"], pack.get("step_count"), pack.get("csv"))
        results.append(
            {
                "id": p["id"],
                "summary": p["summary"],
                "path_name": p["name"],
                "step_count": pack.get("step_count"),
                "csv": pack.get("csv"),
                "md": pack.get("md"),
                "steps": v["steps"],
            }
        )

    out = Path(s.WORKSPACE) / "NewTestCases" / STORY_KEY / "sigiri-manual" / "jira-create-payload.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "link_story": STORY_KEY,
        "also_relate_gold_story": GOLD_STORY,
        "link_type": "Test",
        "create_link": {"inwardIssue": "<NEW_TEST>", "outwardIssue": STORY_KEY, "type": "Test"},
        "packs": [
            {
                "id": r["id"],
                "summary": r["summary"],
                "path_name": r["path_name"],
                "step_count": r["step_count"],
                "csv": r["csv"],
                "md": r["md"],
            }
            for r in results
        ],
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("payload", out)
    # write steps json per pack for description
    for r in results:
        steps_path = Path(r["csv"]).with_name(f"{r['id']}-steps.json")
        steps_path.write_text(json.dumps(r["steps"], indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
