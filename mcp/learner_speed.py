"""Per-round learner — harvest what sped QA up and propose next-run shortcuts."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from paths import WORKSPACE, KNOWLEDGE_ROOT, REPO_ROOT


def _store() -> Path:
    d = WORKSPACE / "learner"
    d.mkdir(parents=True, exist_ok=True)
    return d / "speed-log.jsonl"


def _playbook() -> Path:
    d = KNOWLEDGE_ROOT
    d.mkdir(parents=True, exist_ok=True)
    return d / "SPEED-PLAYBOOK.md"


def record(
    task_key: str,
    notes: str,
    what_worked: str = "",
    what_slowed: str = "",
    seconds_saved_estimate: int = 0,
    techniques: list[str] | None = None,
) -> dict[str, Any]:
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "task_key": task_key,
        "notes": notes,
        "what_worked": what_worked,
        "what_slowed": what_slowed,
        "seconds_saved_estimate": int(seconds_saved_estimate or 0),
        "techniques": techniques or [],
    }
    with _store().open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # append playbook bullets
    pb = _playbook()
    bullets = []
    if what_worked.strip():
        bullets.append(f"- WORKED ({task_key}): {what_worked.strip()}")
    if what_slowed.strip():
        bullets.append(f"- AVOID ({task_key}): {what_slowed.strip()}")
    for t in techniques or []:
        if t.strip():
            bullets.append(f"- TECHNIQUE ({task_key}): {t.strip()}")
    if bullets:
        header = f"\n## Round {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
        if not pb.exists():
            pb.write_text(
                "# LIQA Speed Playbook\n\nLearned shortcuts from real headed QA rounds.\n",
                encoding="utf-8",
            )
        with pb.open("a", encoding="utf-8") as f:
            f.write(header)
            f.write("\n".join(bullets) + "\n")
    return {"ok": True, "recorded": row, "playbook": str(pb)}


def suggest(task_key: str = "", limit: int = 12) -> dict[str, Any]:
    store = _store()
    rows: list[dict[str, Any]] = []
    if store.exists():
        for line in store.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if task_key:
        preferred = [r for r in rows if r.get("task_key") == task_key]
        others = [r for r in rows if r.get("task_key") != task_key]
        rows = preferred + others
    tips = []
    for r in reversed(rows[-limit:]):
        if r.get("what_worked"):
            tips.append({"type": "reuse", "text": r["what_worked"], "from": r.get("task_key")})
        if r.get("what_slowed"):
            tips.append({"type": "avoid", "text": r["what_slowed"], "from": r.get("task_key")})
        for t in r.get("techniques") or []:
            tips.append({"type": "technique", "text": t, "from": r.get("task_key")})
    # built-in speed defaults from PF-55248 / PF-59194 success
    defaults = [
        {"type": "default", "text": "Prefer Playwright CDP on live Edge session over raw pyautogui for SPA forms."},
        {"type": "default", "text": "Minimize Excel before every capture — it steals focus and poisons proof."},
        {"type": "default", "text": "Human Gate only for Azure AD / OTP; do not pause for ordinary clicks."},
        {"type": "default", "text": "Build Book1 from headed proof folder only; never invent screenshots."},
        {"type": "default", "text": "Pull migrated account numbers from existing Jira/Xray evidence before blocking."},
    ]
    playbook_exists = _playbook().exists()
    return {
        "ok": True,
        "task_key": task_key,
        "tips": (tips + defaults)[: limit + len(defaults)],
        "rounds_logged": len(rows),
        "playbook": str(_playbook()) if playbook_exists else None,
        "message": "Apply tips at planning + first headed navigation to uplift speed.",
    }


def learn_cycle(notes: str = "", task_key: str = "") -> dict[str, Any]:
    """Called at ISTQB completion — always write a speed round."""
    # pull last trajectory hint if worker left one
    traj = REPO_ROOT / "trajectories"
    last_note = notes
    if traj.is_dir():
        files = sorted(traj.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if files:
            try:
                data = json.loads(files[0].read_text(encoding="utf-8"))
                last_note = notes or json.dumps(data)[:500]
            except Exception:  # noqa: BLE001
                pass
    rec = record(
        task_key=task_key or "general",
        notes=last_note or "learn_cycle",
        what_worked="Completed learn_cycle; refresh SPEED-PLAYBOOK before next task.",
        what_slowed="",
        techniques=["liqa_learn_speed before nav", "liqa_agency_dispatch for parallel intake"],
    )
    sug = suggest(task_key=task_key)
    return {"ok": True, "recorded": rec, "suggest": sug}
