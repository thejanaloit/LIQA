"""20-round honesty cycle. Eyes every round. Hands only if explicitly enabled."""
from __future__ import annotations

import time
from typing import Any

import honesty
import intent
import policy
from health import headed_health


def run_cycle(task: str, *, rounds: int = 20, eyes: bool = True, use_hands: bool = False, check_health: bool = True, ocr: bool = True) -> dict[str, Any]:
    pol = policy.check_task(task)
    plan = intent.predict(task)
    if not pol.get("ok") or plan.get("ask_user"):
        return {
            "ok": False,
            "status": "NEEDS_HUMAN",
            "reason": pol.get("reason") or "unclear — type a real task first",
            "plan": plan,
            "rounds": [],
        }
    h0 = {"ok": True}
    if check_health:
        h0 = headed_health()
        if not h0.get("ok"):
            return {"ok": False, "status": "FAILED", "reason": "worker not headed-ready", "health": h0, "rounds": []}
    job: dict[str, Any] = {"status": "STEPPED", "approaches": 0}
    log: list[dict[str, Any]] = []
    stopped = None
    import hands

    for i in range(1, max(1, rounds) + 1):
        honesty.bump_approach(job)
        ocr_text = ""
        png = None
        if eyes:
            shot = hands.screenshot(f"cycle20-{i:02d}", ocr=ocr)
            cap = shot.get("capture") or {}
            if isinstance(cap, dict):
                ocr_text = str(cap.get("ocr_preview") or "")[:800]
                png = cap.get("path")
        blocker = intent.classify_blocker(ocr_text)
        rec = {
            "round": i,
            "of": rounds,
            "headed": True,
            "next3": honesty.next_three(plan.get("predicted") or [], i - 1),
            "blocker": blocker,
            "status": job.get("status"),
            "approaches": job.get("approaches"),
            "png": png,
            "at": time.strftime("%H:%M:%S"),
        }
        if blocker and blocker != "checkbox_captcha":
            rec["status"] = "NEEDS_HUMAN"
            rec["gate"] = blocker
            log.append(rec)
            stopped = blocker
            break
        if blocker == "checkbox_captcha" and use_hands:
            rec["hands"] = hands.click_text("I'm not a robot")
        elif use_hands and i == 1:
            rec["note"] = "Hands enabled — still no guessed x/y; click_text only if OCR has a target."
        log.append(rec)
        if job.get("status") == "REAL_BUG":
            stopped = "20_approaches"
            break

    final = "DONE" if len(log) == rounds and not stopped else (stopped or job.get("status") or "STEPPED")
    if final == "DONE":
        fake = honesty.refuse_fake("done", {"proof_png": log[-1].get("png") if log else None})
        if not fake["ok"]:
            final = "STEPPED"
    return {
        "ok": final in ("DONE", "STEPPED"),
        "status": final,
        "task": task,
        "kind": plan.get("kind"),
        "restate": plan.get("restate"),
        "roundsCompleted": len(log),
        "roundsTarget": rounds,
        "approaches": job.get("approaches"),
        "handsUsed": use_hands,
        "honesty": "20 rounds. REAL_BUG if exhausted without proof. Hard CAPTCHA/SMS/Google = NEEDS_HUMAN.",
        "log": log,
        "plan": plan,
    }


def tick(task: str, round_no: int, *, rounds: int = 20, eyes: bool = True, use_hands: bool = False, ocr: bool | None = None) -> dict[str, Any]:
    """One visible round for the Control UI loop. Health check only on round 1. OCR defaults to round 1 only."""
    use_ocr = bool(ocr) if ocr is not None else False
    one = run_cycle(
        task,
        rounds=1,
        eyes=eyes,
        use_hands=use_hands and round_no == 1,
        check_health=round_no == 1,
        ocr=use_ocr and eyes,
    )
    rec = (one.get("log") or [{}])[0]
    rec["round"] = int(round_no)
    rec["of"] = rounds
    rec["batchStatus"] = one.get("status")
    rec["kind"] = one.get("kind")
    rec["ok"] = one.get("ok")
    rec["reason"] = one.get("reason")
    rec["restate"] = one.get("restate")
    return rec
