"""Format packs: ISTQB default + optional Sigiri. Never invent URS."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2] / "packs"
ROOT.mkdir(parents=True, exist_ok=True)

ISTQB = {
    "id": "istqb-functional",
    "storyTitle": "[Module] [Feature] — Validate that <behaviour>.",
    "testType": "Functional",
    "bugTitle": "Module | When user tries to … then …",
    "neverEditExistingXray": True,
}

SIGIRI = {
    "id": "pf-59194-sigiri",
    "scope": "LOLC lolcgroupdev only — optional pack",
    "storyTitle": "Module | Feature | … | Testcase writing and execution",
    "labels": ["TestCrafters"],
    "bugTitle": "#TestCrafters #Kenya #UAT#cNwNb# Module | When User Try To…",
    "neverEditExistingXray": True,
}


def load(name: str = "istqb-functional") -> dict[str, Any]:
    p = ROOT / f"{name}.json"
    if not p.exists():
        data = ISTQB if "sigiri" not in name else SIGIRI
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data
    return json.loads(p.read_text(encoding="utf-8"))


def list_packs() -> list[str]:
    for n, d in (("istqb-functional", ISTQB), ("pf-59194-sigiri", SIGIRI)):
        p = ROOT / f"{n}.json"
        if not p.exists():
            p.write_text(json.dumps(d, indent=2), encoding="utf-8")
    return [p.stem for p in ROOT.glob("*.json")]
