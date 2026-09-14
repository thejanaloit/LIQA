"""Refuse stuffing, mass accounts, destructive OS, Win+R bypass, OTP invention."""
from __future__ import annotations

import re
from typing import Any

DESTRUCTIVE = ("format c:", "del /s", "rm -rf", "shutdown", "stop-computer", "diskpart", "cipher /w")
STUFFING = ("password list", "combo list", "credential stuffing", "50 emails", "100 accounts", "create accounts for")
WINR = ("win+r", "windows+r", "run dialog")


def check_task(task: str) -> dict[str, Any]:
    t = (task or "").lower()
    if any(x in t for x in STUFFING) or re.search(r"\b(\d{2,}|hundreds?)\s+accounts?\b", t):
        return {"ok": False, "gate": "policy", "reason": "Refuse mass account creation / stuffing."}
    if any(x in t for x in DESTRUCTIVE):
        return {"ok": False, "gate": "confirm_destructive", "reason": "Destructive OS action needs explicit human confirm."}
    if any(x in t for x in WINR) and "bypass" in t:
        return {"ok": False, "gate": "policy", "reason": "Refuse Win+R as a silent Hands bypass."}
    if "invent otp" in t or "bypass 2fa" in t or "solve captcha farm" in t:
        return {"ok": False, "gate": "policy", "reason": "Refuse OTP invention and captcha farms."}
    if len((task or "").strip()) < 4:
        return {"ok": False, "gate": "unclear", "reason": "Target unclear — ask the user, do not start Hands."}
    return {"ok": True}


def never_invent_otp() -> dict[str, str]:
    return {"otp": "never_invent", "source": "visible_field_or_human_gate"}
