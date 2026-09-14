"""Chrome profile isolation per tenant. One process; no second Chromium for maker-checker."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("LIQA_PROFILES", Path(__file__).resolve().parents[2] / "captures" / "profiles"))
ROOT.mkdir(parents=True, exist_ok=True)


def dir_for(tenant: str) -> Path:
    safe = "".join(c for c in tenant if c.isalnum() or c in "-_")[:32] or "default"
    p = ROOT / safe
    p.mkdir(parents=True, exist_ok=True)
    return p


def law() -> dict[str, Any]:
    return {
        "one_process": True,
        "maker_checker": "logout/login in SAME Chrome — never spawn a second process",
        "new_tab": "UI click only, not chrome.tabs API",
        "address_bar": "forbidden after entry URL",
        "entry_once": True,
    }
