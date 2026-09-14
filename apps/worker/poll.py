"""Outbound poll: pull Control jobs onto this headed Worker."""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

CONTROL = os.environ.get("LIQA_CONTROL_URL", "http://127.0.0.1:8788")
TOKEN = os.environ.get("LIQA_CONTROL_TOKEN", "")


def _req(method: str, path: str, body: dict | None = None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(f"{CONTROL}{path}", data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def heartbeat() -> dict[str, Any]:
    from health import headed_health

    h = headed_health()
    return _req("POST", "/v1/workers/heartbeat", {"id": "local-worker", "headed": h["ok"], "health": h})


def pull_jobs() -> dict[str, Any]:
    return _req("GET", "/v1/jobs")
