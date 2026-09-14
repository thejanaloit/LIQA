"""Human gate — pause for SMS / Google 2FA / hard CAPTCHA. Never solve farms."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent / "gates"
ROOT.mkdir(parents=True, exist_ok=True)

CLICKABLE = {"checkbox_captcha"}
PAUSE = {"hard_captcha", "sms_otp", "google_2fa", "phone_call", "captcha"}


def create(kind: str, detail: str = "", job_id: str = "") -> dict[str, Any]:
    gid = uuid.uuid4().hex[:10]
    gate = {
        "id": gid,
        "kind": kind,
        "status": "waiting_human" if kind in PAUSE or kind not in CLICKABLE else "auto_click_allowed",
        "detail": detail,
        "jobId": job_id,
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "honesty": "Hard CAPTCHA / SMS / Google 2FA: human completes it. LIQA does not use captcha farms.",
    }
    (ROOT / f"{gid}.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")
    return gate


def list_gates() -> list[dict[str, Any]]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(ROOT.glob("*.json"))]


def ack(gid: str) -> dict[str, Any] | None:
    p = ROOT / f"{gid}.json"
    if not p.exists():
        return None
    g = json.loads(p.read_text(encoding="utf-8"))
    g["status"] = "acked"
    g["ackedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    p.write_text(json.dumps(g, indent=2), encoding="utf-8")
    return g


def policy_for(kind: str) -> dict[str, Any]:
    if kind == "checkbox_captcha":
        return {
            "action": "click_text",
            "text": "I'm not a robot",
            "note": "Only if the checkbox is on the latest screenshot.",
        }
    return {
        "action": "human_gate",
        "kind": kind,
        "note": "Pause and wait for the human on this PC.",
    }
