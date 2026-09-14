"""Learn-cycle after job close — no passwords in harvest."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

KB = Path(__file__).resolve().parents[2] / "knowledgeBase"
KB.mkdir(parents=True, exist_ok=True)


def harvest(job: dict[str, Any]) -> dict[str, Any]:
    safe = {k: v for k, v in job.items() if k.lower() not in {"password", "otp", "token", "secret"}}
    p = KB / f"{job.get('jobId') or job.get('id') or 'job'}.json"
    p.write_text(json.dumps(safe, indent=2)[:8000], encoding="utf-8")
    return {"ok": True, "path": str(p), "telemetry": "opt-in only — LIQA_TELEMETRY=1 to ship metadata without pixels"}
