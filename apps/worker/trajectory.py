"""Record headed trajectory; replay only on headed Worker. Never default headless."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2] / "trajectories"
ROOT.mkdir(parents=True, exist_ok=True)


def record(job_id: str, step: dict[str, Any]) -> dict[str, Any]:
    p = ROOT / f"{job_id}.jsonl"
    rec = {**step, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "headed": True}
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return {"ok": True, "path": str(p)}


def load(job_id: str) -> list[dict[str, Any]]:
    p = ROOT / f"{job_id}.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def replay_plan(job_id: str) -> dict[str, Any]:
    steps = load(job_id)
    return {
        "ok": True,
        "jobId": job_id,
        "steps": steps,
        "mode": "headed_visible",
        "headless_default": False,
        "self_heal": "On screenshot mismatch, invalidate cache and re-enter brain.",
    }
