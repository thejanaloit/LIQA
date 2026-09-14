"""One headed session lock: one browser, entry URL once, never close mid-job."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

STATE = Path(__file__).resolve().parent / "session.json"


def load() -> dict[str, Any]:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"open": False, "entryUrlLoaded": False, "browserPid": None, "jobId": None}


def save(st: dict[str, Any]) -> dict[str, Any]:
    STATE.write_text(json.dumps(st, indent=2), encoding="utf-8")
    return st


def reset() -> dict[str, Any]:
    if STATE.exists():
        STATE.unlink()
    return load()


def begin(job_id: str, entry_url: str = "") -> dict[str, Any]:
    st = load()
    if st.get("open") and st.get("jobId") and st.get("jobId") != job_id:
        return {"ok": False, "reason": "session_busy", "current": st}
    st.update(
        {
            "open": True,
            "jobId": job_id,
            "entryUrl": entry_url,
            "entryUrlLoaded": False,
            "startedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "law": "Never close browser mid-job. Never page.goto after entry.",
        }
    )
    return {"ok": True, **save(st)}


def mark_entry_loaded() -> dict[str, Any]:
    st = load()
    st["entryUrlLoaded"] = True
    return {"ok": True, **save(st)}


def forbid_goto() -> dict[str, Any]:
    st = load()
    if st.get("entryUrlLoaded"):
        return {"ok": False, "reason": "goto_forbidden_after_entry", "use": "mouse_clicks_only"}
    return {"ok": True, "note": "entry not loaded yet — one goto allowed"}


def end(job_id: str) -> dict[str, Any]:
    st = load()
    if st.get("jobId") != job_id:
        return {"ok": False, "reason": "job_mismatch"}
    st.update({"open": False, "jobId": None, "endedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    return {"ok": True, **save(st)}
