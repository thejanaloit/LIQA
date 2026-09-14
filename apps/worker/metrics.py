"""Prometheus-ish metrics + JSON logs + alerts."""
from __future__ import annotations

import json
import time
from collections import Counter
from typing import Any

from health import headed_health

_REASONS: Counter[str] = Counter()
_JOBS = 0
_GATES = 0
_SILENT = 0.0
_LAST_HB = time.time()


def note_health() -> None:
    global _LAST_HB
    _LAST_HB = time.time()
    h = headed_health()
    for r in h.get("reasons") or []:
        _REASONS[str(r)] += 1


def note_job() -> None:
    global _JOBS
    _JOBS += 1


def note_gate() -> None:
    global _GATES
    _GATES += 1


def prometheus() -> str:
    h = headed_health()
    silent = time.time() - _LAST_HB
    lines = [
        f"liqa_worker_headed {1 if h.get('ok') else 0}",
        f"liqa_jobs_total {_JOBS}",
        f"liqa_gates_total {_GATES}",
        f"liqa_worker_silent_seconds {silent:.0f}",
    ]
    for k, v in _REASONS.items():
        safe = k.replace('"', "'")[:80]
        lines.append(f'liqa_headed_fail_reason{{reason="{safe}"}} {v}')
    return "\n".join(lines) + "\n"


def alerts(gate_age: float = 0) -> list[dict[str, Any]]:
    out = []
    silent = time.time() - _LAST_HB
    if silent > 60:
        out.append({"alert": "worker_silent", "seconds": silent})
    if gate_age > 600:
        out.append({"alert": "human_gate_sla", "seconds": gate_age})
    h = headed_health()
    if not h.get("ok"):
        out.append({"alert": "headed_unhealthy", "reasons": h.get("reasons")})
    return out


def jlog(event: str, **kw: Any) -> str:
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event, **kw}
    for s in ("password", "otp", "token", "secret", "apiKey"):
        if s in rec:
            rec[s] = "<redacted>"
    line = json.dumps(rec, ensure_ascii=False)
    return line
