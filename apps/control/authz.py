"""RBAC, CSRF cookie, OIDC stub, license seats."""
from __future__ import annotations

import hashlib
import hmac
import os
import time
from typing import Any

ROLES = ("owner", "qa-lead", "viewer")
CSRF_SECRET = os.environ.get("LIQA_CSRF_SECRET", "liqa-csrf-dev")
SEATS = int(os.environ.get("LIQA_WORKER_SEATS", "1"))
OIDC = {
    "issuer": os.environ.get("LIQA_OIDC_ISSUER", ""),
    "clientId": os.environ.get("LIQA_OIDC_CLIENT", ""),
    "note": "Stub — wire customer IdP. Local host uses cookie session.",
}


def role_of(header: str) -> str:
    h = (header or "").lower()
    for r in ROLES:
        if r in h:
            return r
    return "owner" if not os.environ.get("LIQA_CONTROL_TOKEN") else "viewer"


def can(role: str, action: str) -> bool:
    if role == "owner":
        return True
    if role == "qa-lead":
        return action in {"job_create", "job_cancel", "gate_ack", "view"}
    return action == "view"


def csrf_token() -> str:
    ts = str(int(time.time()) // 3600)
    return hmac.new(CSRF_SECRET.encode(), ts.encode(), hashlib.sha256).hexdigest()[:24]


def csrf_ok(token: str) -> bool:
    return hmac.compare_digest(csrf_token(), token or "")


def seats_ok(worker_count: int) -> dict[str, Any]:
    return {"ok": worker_count <= SEATS, "seats": SEATS, "used": worker_count}


def license_activate(key: str) -> dict[str, Any]:
    digest = hashlib.sha256(key.encode()).hexdigest()
    ok = len(key) >= 16
    return {"ok": ok, "keyHash": digest[:16], "seats": SEATS}
