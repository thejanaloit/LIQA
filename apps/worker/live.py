"""Live view: screenshot poll + MJPEG. WebRTC H.264 documented; poll is the working fallback."""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import hands

FPS_CAP = 25
LAST = Path(__file__).resolve().parents[2] / "captures" / "live"
LAST.mkdir(parents=True, exist_ok=True)
DEBUG = os.environ.get("LIQA_DEBUG_URL", "http://127.0.0.1:8787/v1/live/frame")


def frame(label: str = "live") -> dict[str, Any]:
    cap = hands.screenshot(label, ocr=False, wait=False)
    path = None
    c = cap.get("capture") or {}
    if isinstance(c, dict):
        path = c.get("path")
    return {
        "ok": bool(cap.get("ok")),
        "debugUrl": DEBUG,
        "interactive": False,
        "fpsCap": FPS_CAP,
        "webrtc": "optional — needs TURN outbound in customer VPC; poll is default",
        "blurPii": False,
        "presence": "LIQA Worker",
        "path": path,
        "capture": cap,
    }


def webrtc_notes() -> dict[str, Any]:
    return {
        "publisher": "Worker desktop H.264 when a TURN is configured",
        "sfu": "Control relays to same-tenant viewers only",
        "ice": "outbound-only ICE/TURN — no inbound bank hole",
        "fallback": "/v1/live/frame screenshot poll",
        "interactive": "human_gate ACK then viewer may take mouse on the Worker PC",
    }
