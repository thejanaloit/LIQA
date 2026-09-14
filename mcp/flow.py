"""ISTQB 7-phase flow state for ManualQA-Agent."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from laws import ISTQB_PHASES, VERSION
from paths import WORKSPACE

FOLDERS = [
    "assignedTasks",
    "UserStories",
    "ExistingTestCases",
    "map",
    "knowledgeBase",
    "NewTestCases",
    "outputs",
    "bugs",
    "reports",
    "reports/live-manual",
    "reports/proof",
    "agents",
    "agents/roles",
    "secrets",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def state_path() -> Path:
    return WORKSPACE / "agents" / "flow-state.json"


def ensure_workspace() -> dict[str, Any]:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    for rel in FOLDERS:
        (WORKSPACE / rel).mkdir(parents=True, exist_ok=True)
    sp = state_path()
    if not sp.exists():
        state = {
            "version": VERSION,
            "created_at": _now(),
            "updated_at": _now(),
            "current_phase": 1,
            "phases": {
                str(p["id"]): {
                    "key": p["key"],
                    "title": p["title"],
                    "status": "pending",
                    "notes": "",
                    "completed_at": None,
                }
                for p in ISTQB_PHASES
            },
            "monitor": {"ok": True, "blocker": None, "last_heartbeat": None},
            "honesty": {},
            "credentials": {"requested": False, "enough": None, "notes": ""},
            "announced_planning_done": False,
        }
        sp.parent.mkdir(parents=True, exist_ok=True)
        sp.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state
    return json.loads(sp.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any]) -> dict[str, Any]:
    state["updated_at"] = _now()
    sp = state_path()
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def status_payload() -> dict[str, Any]:
    state = ensure_workspace()
    phases_out = []
    for p in ISTQB_PHASES:
        st = state["phases"].get(str(p["id"]), {})
        phases_out.append(
            {
                "id": p["id"],
                "key": p["key"],
                "title": p["title"],
                "status": st.get("status", "pending"),
                "istqb": p["istqb"],
                "do": p["do"],
                "notes": st.get("notes") or "",
            }
        )
    mon = state.get("monitor") or {}
    return {
        "ok": True,
        "product": "ManualQA-Agent",
        "version": VERSION,
        "workspace": str(WORKSPACE),
        "current_phase": state.get("current_phase", 1),
        "monitor_ok": bool(mon.get("ok", True)),
        "blocker": mon.get("blocker"),
        "phases": phases_out,
        "credentials": state.get("credentials"),
        "announced_planning_done": state.get("announced_planning_done", False),
        "next": _next_action(state),
    }


def todo_list() -> dict[str, Any]:
    """Numbered company TODO list — alias shape of status for operators."""
    st = status_payload()
    items = []
    for p in st.get("phases") or []:
        mark = {"done": "[x]", "in_progress": "[~]", "pending": "[ ]"}.get(
            p.get("status", "pending"), "[ ]"
        )
        items.append(
            {
                "n": p["id"],
                "title": f"{mark} {p['id']}. {p['title']} ({p['status']})",
                "status": p.get("status"),
                "do": (p.get("do") or [""])[0],
                "active": int(st.get("current_phase") or 1) == int(p["id"]),
            }
        )
    numbered = "\n".join(
        f"{it['n']}. [{it['status']}] {it['title'].split('. ', 1)[-1]} — {it['do']}"
        for it in items
    )
    return {
        "ok": True,
        "product": "ManualQA-Agent",
        "current_phase": st.get("current_phase"),
        "monitor_ok": st.get("monitor_ok"),
        "blocker": st.get("blocker"),
        "todos": items,
        "numbered_text": numbered,
        "next": st.get("next"),
        "message": "Company ISTQB TODO — complete in order; no skip.",
    }


def write_flow_chart() -> dict[str, Any]:
    from laws import FLOW_CHART_MD

    ensure_workspace()
    path = WORKSPACE / "agents" / "FLOW-CHART.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(FLOW_CHART_MD, encoding="utf-8")
    return {"ok": True, "path": str(path), "markdown": FLOW_CHART_MD, "text": FLOW_CHART_MD}


def file_bug_draft(
    key: str,
    title: str,
    body: str,
    proof_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Write a local bug draft under bugs/<KEY>/. Agent uploads via Atlassian MCP."""
    ensure_workspace()
    safe_key = "".join(c for c in key if c.isalnum() or c in "-_") or "GENERAL"
    dest = WORKSPACE / "bugs" / safe_key
    dest.mkdir(parents=True, exist_ok=True)
    proofs = [str(p) for p in (proof_paths or []) if str(p).strip()]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in (title or "bug")[:48]).strip("-") or "bug"
    md_path = dest / f"{stamp}-{slug}.md"
    meta_path = dest / f"{stamp}-{slug}.json"
    md = (
        f"# {title}\n\n"
        f"**Story/Key:** {safe_key}\n\n"
        f"## Description\n\n{body}\n\n"
        f"## Proof paths (attach via Atlassian MCP — do not invent)\n\n"
        + ("\n".join(f"- `{p}`" for p in proofs) if proofs else "- (none yet)\n")
        + "\n\n## Upload note\n\n"
        "This file is a **draft only**. Create the Jira bug with Atlassian MCP and attach PNGs.\n"
    )
    md_path.write_text(md, encoding="utf-8")
    meta = {
        "key": safe_key,
        "title": title,
        "body": body,
        "proof_paths": proofs,
        "draft_md": str(md_path),
        "created_at": _now(),
        "upload": "use Atlassian MCP — no hardcoded Jira API in this MCP",
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return {"ok": True, "draft_md": str(md_path), "meta": str(meta_path), **meta}


def _next_action(state: dict[str, Any]) -> str:
    cur = int(state.get("current_phase") or 1)
    for p in ISTQB_PHASES:
        st = state["phases"].get(str(p["id"]), {})
        if st.get("status") != "done":
            return f"Work phase {p['id']}: {p['title']} — {p['do'][0]}"
    return "All ISTQB phases done. Run honesty ×3 + learn, then close."


def complete_phase(phase_id: int, notes: str = "") -> dict[str, Any]:
    state = ensure_workspace()
    pid = int(phase_id)
    if pid < 1 or pid > 7:
        return {"ok": False, "error": "phase_id must be 1..7"}
    # live headed phases need clear monitor
    if pid in (3, 6) and not (state.get("monitor") or {}).get("ok", True):
        return {
            "ok": False,
            "error": "monitor blocked — clear blocker with mqa_heartbeat (no blocker) first",
            "blocker": (state.get("monitor") or {}).get("blocker"),
        }
    # sequential: prior must be done
    for earlier in range(1, pid):
        if state["phases"][str(earlier)].get("status") != "done":
            return {
                "ok": False,
                "error": f"phase {earlier} not done — cannot complete {pid}",
            }
    state["phases"][str(pid)]["status"] = "done"
    state["phases"][str(pid)]["notes"] = notes or state["phases"][str(pid)].get("notes") or ""
    state["phases"][str(pid)]["completed_at"] = _now()
    if pid < 7:
        state["current_phase"] = pid + 1
        state["phases"][str(pid + 1)]["status"] = "in_progress"
    else:
        state["current_phase"] = 7
    save_state(state)
    return {"ok": True, "completed": pid, "status": status_payload()}


def set_notes(phase_id: int, notes: str) -> dict[str, Any]:
    state = ensure_workspace()
    pid = str(int(phase_id))
    if pid not in state["phases"]:
        return {"ok": False, "error": "bad phase"}
    state["phases"][pid]["notes"] = notes
    if state["phases"][pid].get("status") == "pending":
        state["phases"][pid]["status"] = "in_progress"
        state["current_phase"] = int(phase_id)
    save_state(state)
    return {"ok": True, "status": status_payload()}


def heartbeat(blocker: str = "") -> dict[str, Any]:
    state = ensure_workspace()
    mon = state.setdefault("monitor", {})
    mon["last_heartbeat"] = _now()
    if blocker.strip():
        mon["ok"] = False
        mon["blocker"] = blocker.strip()
    else:
        mon["ok"] = True
        mon["blocker"] = None
    save_state(state)
    return {"ok": True, "monitor": mon}


def request_credentials(notes: str = "") -> dict[str, Any]:
    state = ensure_workspace()
    state["credentials"] = {
        "requested": True,
        "enough": None,
        "notes": notes,
        "at": _now(),
        "hint": "Use secrets/tmp-creds.json (gitignored). Never commit passwords.",
    }
    save_state(state)
    return {"ok": True, "credentials": state["credentials"], "ask_mode": True}


def set_credentials_enough(enough: bool, notes: str = "") -> dict[str, Any]:
    state = ensure_workspace()
    cred = state.setdefault("credentials", {})
    cred["enough"] = bool(enough)
    cred["notes"] = notes
    cred["checked_at"] = _now()
    save_state(state)
    return {"ok": True, "credentials": cred}


def announce_planning_done() -> dict[str, Any]:
    state = ensure_workspace()
    for need in (1,):  # planning must be done; analysis intake may still be open
        if state["phases"]["1"].get("status") != "done":
            return {"ok": False, "error": "Complete phase 1 (planning) first"}
    state["announced_planning_done"] = True
    save_state(state)
    return {
        "ok": True,
        "message": (
            "Planning intake complete (assigned tasks + credentials path). "
            "Continue ISTQB analysis (stories, existing tests, experience map)."
        ),
    }


def save_md(folder: str, key: str, filename: str, content: str) -> dict[str, Any]:
    state = ensure_workspace()
    safe_key = "".join(c for c in key if c.isalnum() or c in "-_") or "GENERAL"
    dest_dir = WORKSPACE / folder / safe_key
    dest_dir.mkdir(parents=True, exist_ok=True)
    fname = filename if filename.endswith(".md") else f"{filename}.md"
    path = dest_dir / fname
    path.write_text(content, encoding="utf-8")
    return {"ok": True, "path": str(path), "workspace": str(WORKSPACE)}
