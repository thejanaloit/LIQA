"""Eyes → Brain → Hands until done | human_gate | BLOCKED. Proof required."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

import capture_ops
import gates
import hands
import honesty
import intent
import metrics
import policy
import session
import trajectory
from health import headed_health
from vault import honest_enough

PROOF = Path(__file__).resolve().parents[2] / "captures" / "jobs"
PROOF.mkdir(parents=True, exist_ok=True)


def run_job(task: str, *, url: str = "", creds: list[str] | None = None, max_steps: int = 12) -> dict[str, Any]:
    metrics.note_job()
    h = headed_health()
    if not h["ok"]:
        return {"ok": False, "status": "FAILED", "reason": "worker not headed-ready", "health": h}
    pol = policy.check_task(task)
    plan = intent.predict(task)
    if not pol.get("ok") or plan.get("ask_user"):
        return {"ok": False, "status": "NEEDS_HUMAN", "reason": pol.get("reason") or "unclear", "plan": plan}

    jid = uuid.uuid4().hex[:12]
    session.begin(jid, url)
    capture_ops.rotate()
    disk = capture_ops.disk_ok()
    if not disk.get("ok"):
        return {"ok": False, "status": "BLOCKED", "reason": "disk_low", "disk": disk}

    hands.presence("LIQA Worker")
    hands.calibrate()
    log: list[dict[str, Any]] = []
    job: dict[str, Any] = {"id": jid, "status": "STEPPED", "approaches": 0, "revalidate": 0}

    if creds:
        v = honest_enough(creds)
        log.append({"step": "vault", **v})
        if not v["ok"]:
            g = gates.create("credentials", f"Need: {v['missing']}", jid)
            metrics.note_gate()
            return {"ok": False, "status": "human_gate", "jobId": jid, "gate": g, "plan": plan, "log": log}

    from brain import decide

    last_png = None
    for i in range(max(1, max_steps)):
        honesty.bump_approach(job)
        eyes = hands.screenshot(f"job-{jid}-{i}")
        cap = eyes.get("capture") or {}
        last_png = cap.get("path") if isinstance(cap, dict) else None
        ocr = str((cap or {}).get("ocr_preview") or "")[:2000] if isinstance(cap, dict) else ""
        n3 = honesty.next_three(plan.get("predicted") or [], i)
        log.append({"step": "eyes", "i": i, "ok": eyes.get("ok"), "next3": n3, "png": last_png})
        trajectory.record(jid, {"i": i, "ocr": ocr[:200], "next3": n3})

        blocker = intent.classify_blocker(ocr)
        if blocker == "checkbox_captcha":
            log.append({"step": "checkbox", **hands.click_text("I'm not a robot")})
            hands.wait_analyzable(1.0)
            hands.wait_frame(8)
            continue
        if blocker:
            g = gates.create(blocker, ocr[:200], jid)
            metrics.note_gate()
            job["status"] = "human_gate"
            out = {"ok": False, "status": "human_gate", "jobId": jid, "gate": g, "plan": plan, "log": log, "next3": n3}
            _save(jid, out)
            _debrief(jid, task, log, last_png)
            return out

        action = decide(task, ocr, n3)
        log.append({"step": "brain", "action": action})
        act = action.get("action")
        if act == "done":
            fake = honesty.refuse_fake("done", {"proof_png": last_png})
            if not fake["ok"]:
                continue
            job["status"] = "DONE"
            honesty.revalidate_cycle(job)
            break
        if act == "click_text" and action.get("text"):
            log.append({"step": "hands", **hands.click_text(str(action["text"]))})
            hands.wait_analyzable(1.0)
            hands.wait_frame(10)
        elif act == "type" and action.get("text"):
            log.append({"step": "hands", **hands.type_text(str(action["text"]), is_secret=bool(action.get("secret")))})
        elif act == "wait":
            hands.wait_analyzable(1.2)
        elif act == "human_gate":
            g = gates.create(action.get("kind") or "unclear", action.get("reason") or "", jid)
            metrics.note_gate()
            out = {"ok": False, "status": "human_gate", "jobId": jid, "gate": g, "plan": plan, "log": log}
            _save(jid, out)
            return out
        else:
            hands.wait_analyzable(0.5)

    out = {
        "ok": job.get("status") in ("DONE", "STEPPED"),
        "status": job.get("status"),
        "jobId": jid,
        "plan": plan,
        "log": log,
        "approaches": job.get("approaches"),
        "revalidate": job.get("revalidate"),
        "proof": last_png,
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _save(jid, out)
    _debrief(jid, task, log, last_png)
    return out


def _save(jid: str, body: dict[str, Any]) -> None:
    (PROOF / f"{jid}.json").write_text(json.dumps(body, indent=2), encoding="utf-8")


def _debrief(jid: str, task: str, log: list, png: str | None) -> None:
    md = [
        f"# PROOF debrief {jid}",
        "",
        f"Task: {task}",
        f"Proof PNG: {png or 'none'}",
        "",
        "In simple words: LIQA looked at the screen, predicted next steps, and either clicked, typed, or paused for a human.",
        "",
        "```json",
        json.dumps(log[-8:], indent=2)[:4000],
        "```",
        "",
        "Learn-cycle: harvest misses into knowledgeBase (no passwords).",
    ]
    (PROOF / f"{jid}-PROOF.md").write_text("\n".join(md), encoding="utf-8")
