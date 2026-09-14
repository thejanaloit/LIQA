"""Honesty referee, labels, 20 approaches, 3-cycle, never fake CAPTCHA/order."""
from __future__ import annotations

from typing import Any

LABELS = ("REAL_BUG", "BLOCKED", "NEEDS_HUMAN", "STEPPED", "DONE", "FAILED")


def next_three(predicted: list[str], done: int = 0) -> list[str]:
    rest = [p for p in predicted[done : done + 3]]
    while len(rest) < 3:
        rest.append("Eyes first — screenshot then decide. Do not guess.")
    return rest[:3]


def bump_approach(job: dict[str, Any]) -> dict[str, Any]:
    n = int(job.get("approaches") or 0) + 1
    job["approaches"] = n
    if n >= 20 and job.get("status") not in ("DONE", "NEEDS_HUMAN"):
        job["status"] = "REAL_BUG"
        job["honesty"] = "20 approaches exhausted — label REAL_BUG, do not pretend pass."
    return job


def revalidate_cycle(job: dict[str, Any]) -> dict[str, Any]:
    c = int(job.get("revalidate") or 0) + 1
    job["revalidate"] = c
    job["revalidateMax"] = 3
    if c < 3 and job.get("status") == "DONE":
        job["status"] = "STEPPED"
        job["note"] = f"Honesty cycle {c}/3 — do not close yet."
    return job


def refuse_fake(kind: str, evidence: dict[str, Any]) -> dict[str, Any]:
    if kind == "captcha_solved" and evidence.get("gate_used"):
        return {"ok": False, "label": "NEEDS_HUMAN", "reason": "Never claim captcha solved if a gate was used."}
    if kind == "order_placed" and not evidence.get("confirmation_png"):
        return {"ok": False, "label": "BLOCKED", "reason": "Never claim order placed without confirmation PNG."}
    if kind == "done" and not evidence.get("proof_png"):
        return {"ok": False, "label": "STEPPED", "reason": "Never mark done without proof PNG."}
    return {"ok": True}


def timeout_blocked(job: dict[str, Any], sla_sec: int = 600) -> dict[str, Any]:
    if job.get("status") == "human_gate" and int(job.get("gate_age_sec") or 0) > sla_sec:
        job["status"] = "BLOCKED"
        job["ok"] = False
        job["reason"] = "Human gate exceeded SLA — BLOCKED not FAIL."
    return job
