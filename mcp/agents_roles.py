"""Lightweight in-process Manual QA roles — status under workspace/agents/*.json."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from paths import WORKSPACE

ROLES: dict[str, dict[str, Any]] = {
    "orchestrator": {
        "title": "Agents Orchestrator",
        "mission": "Lead company pipeline quality gates; ISTQB order; handoffs between roles.",
        "istqb_phases": [1, 2, 3, 4, 5, 6, 7],
        "contract": [
            "No phase skip.",
            "Evidence-based advance only.",
            "Assign workstreams via liqa_orchestrator_assign.",
        ],
    },
    "intake": {
        "title": "Intake",
        "mission": "Pull assigned Jira tasks, credentials request, stories + existing Xray refs.",
        "istqb_phases": [1, 2, 3],
        "contract": [
            "Save assignedTasks/<KEY>/ in plain English.",
            "Request 2–3 credentials; never print passwords.",
            "Save UserStories/ and ExistingTestCases/ (read-only clones).",
            "Announce planning intake done when ready.",
        ],
    },
    "mapper": {
        "title": "Experience Mapper",
        "mission": "Headed UI experience map — every story control; NO Pass/Fail.",
        "istqb_phases": [3],
        "contract": [
            "Eyes→Brain→Hands; map click X → screen Y into map/<KEY>/.",
            "SBTM charter OK; no verdict labels during map.",
            "If control not visible, ASK — never invent labels.",
        ],
    },
    "designer": {
        "title": "Test Designer",
        "mission": "Harvest Jira tone; design NEW cases (EP/BVA/state/SBTM).",
        "istqb_phases": [4, 5],
        "contract": [
            "knowledgeBase harvest before inventing format.",
            "NEW tests only — never edit/delete existing Xray.",
            "Sufficiency loop: show count + enough yes/no.",
        ],
    },
    "executor": {
        "title": "Headed Executor",
        "mission": "Execute cases on real UI; collect proof.",
        "istqb_phases": [6],
        "contract": [
            "Visible mouse + keyboard; wait frame after every action.",
            "Human Gate for OTP — never invent codes.",
            "Record honesty attempts with proof paths.",
        ],
    },
    "honesty_referee": {
        "title": "Honesty Referee",
        "mission": "Enforce 20-approach / obvious-class rules before REAL_BUG.",
        "istqb_phases": [6, 7],
        "contract": [
            "Found-a-way ⇒ PASS, not a bug.",
            "REAL_BUG only after exhausted failures with proof.",
            "Triple honesty cycle at completion.",
        ],
    },
    "book1_reporter": {
        "title": "Book1 Reporter",
        "mission": "Kenya-UAT / SHARE-gold Book1 + bug drafts.",
        "istqb_phases": [5, 6, 7],
        "contract": [
            "Full English on every text column; 100% screenshot coverage.",
            "Draft bugs under bugs/<KEY>/; agent uploads via Atlassian MCP.",
            "Validate with liqa_book1_validate before share.",
        ],
    },
    "learner": {
        "title": "Retrospective Learner",
        "mission": "After close: learn-cycle into knowledgeBase/skills.",
        "istqb_phases": [7],
        "contract": [
            "Write what worked / failed / format tone lessons.",
            "Update SBTM / defect / Book1 skill packs when gaps found.",
        ],
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def agents_dir() -> Path:
    d = WORKSPACE / "agents"
    d.mkdir(parents=True, exist_ok=True)
    return d


def role_path(role: str) -> Path:
    return agents_dir() / f"role-{role}.json"


def list_roles() -> dict[str, Any]:
    return {
        "ok": True,
        "roles": {k: {"title": v["title"], "mission": v["mission"]} for k, v in ROLES.items()},
    }


def role_start(role: str, instruction: str = "") -> dict[str, Any]:
    key = (role or "").strip().lower()
    if key not in ROLES:
        return {"ok": False, "error": f"unknown role — choose one of: {', '.join(ROLES)}"}
    meta = ROLES[key]
    payload = {
        "role": key,
        "title": meta["title"],
        "mission": meta["mission"],
        "istqb_phases": meta["istqb_phases"],
        "contract": meta["contract"],
        "status": "active",
        "instruction": (instruction or "").strip(),
        "started_at": _now(),
        "updated_at": _now(),
        "history": [{"at": _now(), "event": "start", "instruction": instruction[:2000]}],
    }
    path = role_path(key)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"ok": True, "path": str(path), "role": payload}


def role_status(role: str = "") -> dict[str, Any]:
    if role.strip():
        key = role.strip().lower()
        path = role_path(key)
        if not path.exists():
            return {"ok": True, "role": key, "status": "never_started", "definition": ROLES.get(key)}
        data = json.loads(path.read_text(encoding="utf-8"))
        return {"ok": True, "role": data}
    out = {}
    for key in ROLES:
        path = role_path(key)
        if path.exists():
            out[key] = json.loads(path.read_text(encoding="utf-8"))
        else:
            out[key] = {"status": "never_started", "title": ROLES[key]["title"]}
    return {"ok": True, "roles": out}


def role_dispatch(role: str, instruction: str) -> dict[str, Any]:
    """Record a dispatch and return the role contract for the agent to obey."""
    key = (role or "").strip().lower()
    if key not in ROLES:
        return {"ok": False, "error": f"unknown role — choose one of: {', '.join(ROLES)}"}
    path = role_path(key)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        started = role_start(key, instruction)
        if not started.get("ok"):
            return started
        data = started["role"]
    data["status"] = "dispatched"
    data["instruction"] = (instruction or "").strip()
    data["updated_at"] = _now()
    data.setdefault("history", []).append(
        {"at": _now(), "event": "dispatch", "instruction": instruction[:2000]}
    )
    data["history"] = data["history"][-50:]
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    meta = ROLES[key]
    return {
        "ok": True,
        "path": str(path),
        "role": key,
        "title": meta["title"],
        "mission": meta["mission"],
        "contract": meta["contract"],
        "instruction": data["instruction"],
        "istqb_phases": meta["istqb_phases"],
        "message": f"Dispatched {meta['title']}. Obey contract; record outcomes in workspace.",
    }
