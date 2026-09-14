"""Local vault paths. Never log secrets. Gitignored JSON only."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("LIQA_VAULT", Path(__file__).resolve().parents[2] / "secrets"))
ROOT.mkdir(parents=True, exist_ok=True)


def path_for(name: str) -> Path:
    safe = "".join(c for c in name if c.isalnum() or c in "-_")[:40]
    return ROOT / f"{safe}.json"


def load(name: str) -> dict[str, Any]:
    p = path_for(name)
    if not p.exists():
        return {"ok": False, "reason": "vault_missing", "path": str(p), "honesty": "Ask the user for credentials. Do not invent."}
    data = json.loads(p.read_text(encoding="utf-8"))
    return {"ok": True, "keys": sorted(k for k in data if k.lower() not in ("password", "otp", "secret", "token"))}


def honest_enough(names: list[str]) -> dict[str, Any]:
    missing = [n for n in names if not path_for(n).exists()]
    return {
        "ok": not missing,
        "needed": names,
        "missing": missing,
        "honesty": "Not enough credentials" if missing else "Vault files present (values not printed)",
    }
