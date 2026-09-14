"""
LIQA MCP — Live Intelligent QA — ISTQB-first human Manual QA Engineer clone.

Trigger: "use LIQA" / "liqa agent" / "liqa mcp"
Process: ISTQB CTFL Fundamental Test Process (7 activities)
Device: Eyes → Brain → Hands (headed, visible)
Identity: You ARE the LIQA Engineer (Manual QA clone) (YouTube analogy).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_MCP_DIR = Path(__file__).resolve().parent
if str(_MCP_DIR) not in sys.path:
    sys.path.insert(0, str(_MCP_DIR))

from laws import FLOW_CHART_MD, GLOBAL_RULES, ISTQB_PHASES, MCP_INSTRUCTIONS, VERSION
from paths import CAPTURE_ROOT, REPO_ROOT, SECRETS, WORKSPACE
from engineer_persona import persona_payload

import flow

try:
    import agents_roles as roles
except ImportError:
    roles = None  # type: ignore

try:
    from device_core import (
        capture_desktop,
        click_at,
        click_text,
        click_window_center,
        device_status,
        focus_window,
        hotkey as device_hotkey,
        list_monitors,
        list_windows,
        move_mouse,
        recursive_control_step,
        type_text as device_type_text,
        wait_frame_change,
        device_loop_step,
    )
except ImportError:
    capture_desktop = None  # type: ignore
    device_type_text = None  # type: ignore
    device_hotkey = None  # type: ignore
    list_monitors = None  # type: ignore
    recursive_control_step = None  # type: ignore
    click_at = click_text = device_status = focus_window = None  # type: ignore
    list_windows = move_mouse = wait_frame_change = None  # type: ignore
    click_window_center = device_loop_step = None  # type: ignore

try:
    from excel_outputs import (
        book1_append_row,
        generate_book1_sample,
        list_outputs,
        testcase_sufficiency,
        validate_book1,
    )
except ImportError:
    book1_append_row = generate_book1_sample = list_outputs = testcase_sufficiency = validate_book1 = None  # type: ignore

try:
    import honesty_contract as honesty
except ImportError:
    honesty = None  # type: ignore

try:
    from human_gate import human_gate as _human_gate
    from human_gate import await_otp_field as _await_otp
    from human_gate import ack_gate as _ack_gate
except ImportError:
    _human_gate = None  # type: ignore
    _await_otp = None  # type: ignore
    _ack_gate = None  # type: ignore

try:
    import engineer_extras as extras
except ImportError:
    extras = None  # type: ignore


def _load_creds() -> dict[str, Any]:
    """Load gitignored secrets only — never echo password values to logs."""
    out: dict[str, Any] = {"found": False, "keys": []}
    for p in (SECRETS / "tmp-creds.json", WORKSPACE / "tmp-creds.json"):
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            out["found"] = True
            out["path"] = str(p)
            out["keys"] = list(data.keys())
            out["email"] = data.get("maker_email") or data.get("email") or data.get("username")
            out["has_password"] = bool(data.get("maker_password") or data.get("password"))
            return out
        except Exception as e:  # noqa: BLE001
            out["error"] = str(e)
    return out


def _honesty_store() -> dict[str, Any]:
    state = flow.ensure_workspace()
    return state.setdefault("honesty", {})


def _save_honesty(store: dict[str, Any]) -> None:
    state = flow.ensure_workspace()
    state["honesty"] = store
    flow.save_state(state)


try:
    import agency_mesh as agency
except ImportError:
    agency = None  # type: ignore

try:
    import learner_speed as learner
except ImportError:
    learner = None  # type: ignore

try:
    import resource_map as resources
except ImportError:
    resources = None  # type: ignore

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP  # type: ignore

mcp = FastMCP("liqa", instructions=MCP_INSTRUCTIONS)


@mcp.tool()
def liqa_boot() -> dict[str, Any]:
    """Boot Theja Manual QA Company (merged FINAL): workspace, persona, next phase."""
    st = flow.ensure_workspace()
    specialists = sorted((REPO_ROOT / "company" / "specialists").glob("*.mdc")) if (REPO_ROOT / "company" / "specialists").exists() else []
    tool_count = len(mcp._tool_manager._tools) if hasattr(mcp, "_tool_manager") else None
    import os

    return {
        "ok": True,
        "product": "Theja Manual QA Company",
        "identity": persona_payload().get("identity"),
        "engineer": persona_payload().get("engineer"),
        "version": VERSION,
        "build": os.environ.get("MQA_BUILD", "local"),
        "tool_count": tool_count,
        "process": "ISTQB CTFL Fundamental Test Process",
        "workspace": str(WORKSPACE),
        "repo": str(REPO_ROOT),
        "creds": _load_creds(),
        "current_phase": st.get("current_phase"),
        "company_specialists": [p.stem for p in specialists],
        "persona": persona_payload(),
        "message": (
            "Merged company FINAL. Expect tool_count ~67. "
            "If Cursor UI shows ~47, refresh MCP / Reload Window. "
            "On new task: liqa_fresh_task + liqa_self_assign."
        ),
    }


@mcp.tool()
def liqa_laws() -> dict[str, Any]:
    """Return global ManualQA laws + ISTQB phase map + engineer absolute laws."""
    return {
        "ok": True,
        "version": VERSION,
        "rules": GLOBAL_RULES,
        "phases": ISTQB_PHASES,
        "persona": persona_payload(),
    }


@mcp.tool()
def liqa_engineer_persona() -> dict[str, Any]:
    """Full Manual QA Engineer identity: YouTube analogy + absolute laws + Book1 columns."""
    return persona_payload()


@mcp.tool()
def liqa_status() -> dict[str, Any]:
    """ISTQB phase checklist + monitor + next action. Call every turn."""
    return flow.status_payload()


@mcp.tool()
def liqa_todo_list() -> dict[str, Any]:
    """Numbered company TODO list (ISTQB phases) — alias of status for operators."""
    return flow.todo_list()


@mcp.tool()
def liqa_flow_chart() -> dict[str, Any]:
    """Return ISTQB mermaid/text flow chart and write agents/FLOW-CHART.md."""
    try:
        return flow.write_flow_chart()
    except Exception:
        return {"ok": True, "markdown": FLOW_CHART_MD, "text": FLOW_CHART_MD}


@mcp.tool()
def liqa_complete_phase(phase_id: int, notes: str = "") -> dict[str, Any]:
    """Mark an ISTQB phase done (1..7). Prior phases must already be done."""
    return flow.complete_phase(phase_id, notes)


@mcp.tool()
def liqa_set_notes(phase_id: int, notes: str) -> dict[str, Any]:
    """Attach notes / mark phase in_progress."""
    return flow.set_notes(phase_id, notes)


@mcp.tool()
def liqa_heartbeat(blocker: str = "") -> dict[str, Any]:
    """Heartbeat after meaningful work. Pass blocker text to freeze live phases; empty to clear."""
    return flow.heartbeat(blocker)


@mcp.tool()
def liqa_request_credentials(notes: str = "") -> dict[str, Any]:
    """Ask for 2–3 credentials (Ask mode). Secrets go in secrets/tmp-creds.json only."""
    return flow.request_credentials(notes)


@mcp.tool()
def liqa_credentials_status(enough: bool | None = None, notes: str = "") -> dict[str, Any]:
    """Report whether credentials/access are enough. Omit enough to only read status."""
    if enough is None:
        st = flow.ensure_workspace()
        return {"ok": True, "credentials": st.get("credentials"), "file": _load_creds()}
    return flow.set_credentials_enough(bool(enough), notes)


@mcp.tool()
def liqa_announce_planning_done() -> dict[str, Any]:
    """Tell the user planning intake succeeded (after phase 1 done)."""
    return flow.announce_planning_done()


@mcp.tool()
def liqa_save_assigned_task(key: str, content: str, filename: str = "task.md") -> dict[str, Any]:
    """Save assigned Jira task as plain-English MD under assignedTasks/<KEY>/."""
    return flow.save_md("assignedTasks", key, filename, content)


@mcp.tool()
def liqa_save_user_story(key: str, content: str, filename: str = "story.md") -> dict[str, Any]:
    """Save user story under UserStories/<KEY>/."""
    return flow.save_md("UserStories", key, filename, content)


@mcp.tool()
def liqa_save_existing_testcase(key: str, content: str, filename: str = "existing.md") -> dict[str, Any]:
    """Save existing Xray/is-tested-by reference (read-only) under ExistingTestCases/<KEY>/."""
    return flow.save_md("ExistingTestCases", key, filename, content)


@mcp.tool()
def liqa_save_map_node(key: str, content: str, filename: str = "map.md") -> dict[str, Any]:
    """Save experience-map node under map/<KEY>/ (no Pass/Fail)."""
    return flow.save_md("map", key, filename, content)


@mcp.tool()
def liqa_save_new_testcase(key: str, content: str, filename: str = "new-tc.md") -> dict[str, Any]:
    """Save NEW test case under NewTestCases/<KEY>/. Never edit existing Xray."""
    return flow.save_md("NewTestCases", key, filename, content)


@mcp.tool()
def liqa_save_knowledge(name: str, content: str) -> dict[str, Any]:
    """Harvest Jira tone / format notes into knowledgeBase/."""
    return flow.save_md("knowledgeBase", "harvest", name, content)


@mcp.tool()
def liqa_testcase_sufficiency(
    story_key: str,
    new_count: int,
    existing_count: int = 0,
    enough: bool = False,
    notes: str = "",
) -> dict[str, Any]:
    """Record whether new test count is enough for a story (show count + enough yes/no)."""
    if testcase_sufficiency is not None:
        try:
            out = testcase_sufficiency(story_key, new_count, existing_count, notes)
            if isinstance(out, dict):
                out["enough"] = enough
            return out
        except TypeError:
            pass
    path = WORKSPACE / "NewTestCases" / story_key / "sufficiency.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "story_key": story_key,
        "new_count": new_count,
        "existing_count": existing_count,
        "enough": enough,
        "notes": notes,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"ok": True, **payload, "path": str(path)}


# --- Roles ---
@mcp.tool()
def liqa_role_list() -> dict[str, Any]:
    """List in-process Manual QA roles (intake, mapper, designer, executor, …)."""
    if roles is None:
        return {"ok": False, "error": "agents_roles missing"}
    return roles.list_roles()


@mcp.tool()
def liqa_role_start(role: str, instruction: str = "") -> dict[str, Any]:
    """Start a role; writes workspace/agents/role-<name>.json."""
    if roles is None:
        return {"ok": False, "error": "agents_roles missing"}
    return roles.role_start(role, instruction)


@mcp.tool()
def liqa_role_status(role: str = "") -> dict[str, Any]:
    """Status for one role or all roles (from workspace/agents/*.json)."""
    if roles is None:
        return {"ok": False, "error": "agents_roles missing"}
    return roles.role_status(role)


@mcp.tool()
def liqa_role_dispatch(role: str, instruction: str) -> dict[str, Any]:
    """Dispatch a role with an instruction; returns role contract for the agent to obey."""
    if roles is None:
        return {"ok": False, "error": "agents_roles missing"}
    return roles.role_dispatch(role, instruction)


# --- Book1 ---
@mcp.tool()
def liqa_book1_sample(story_key: str) -> dict[str, Any]:
    """Create Book1 sample workbook scaffold for a story."""
    if generate_book1_sample is None:
        return {"ok": False, "error": "excel_outputs missing — pip install openpyxl"}
    return generate_book1_sample(story_key)


@mcp.tool()
def liqa_book1_append_row(
    story_key: str,
    area: str,
    issue: str,
    what_is_testing: str,
    why_prediction: str,
    second_qa: str,
    simple_explanation: str,
    screenshot_path: str = "",
    is_bug: bool = False,
) -> dict[str, Any]:
    """Append one full-English Book1 row. Embed screenshot when path exists. Bugs use red Issue fill."""
    if book1_append_row is None:
        return {"ok": False, "error": "excel_outputs missing"}
    return book1_append_row(
        story_key,
        area=area,
        issue=issue,
        screenshot_path=screenshot_path,
        what_is_testing=what_is_testing,
        why_prediction=why_prediction,
        second_qa=second_qa,
        english_explanation=simple_explanation,
        is_bug=is_bug,
    )


@mcp.tool()
def liqa_book1_validate(story_key: str = "", path: str = "") -> dict[str, Any]:
    """Validate Book1 against SHARE gold contract (100% screenshots + full English)."""
    if validate_book1 is None:
        return {"ok": False, "error": "excel_outputs missing"}
    target = path.strip()
    if not target and story_key:
        target = str(WORKSPACE / "outputs" / story_key / f"{story_key}-Book1.xlsx")
    if not target:
        return {"ok": False, "error": "pass story_key or path"}
    return validate_book1(target)


@mcp.tool()
def liqa_list_outputs() -> dict[str, Any]:
    """List Book1 / report outputs in workspace."""
    if list_outputs is None:
        outs = list((WORKSPACE / "outputs").rglob("*")) if (WORKSPACE / "outputs").exists() else []
        return {"ok": True, "files": [str(p) for p in outs[:200]]}
    return list_outputs()


@mcp.tool()
def liqa_file_bug_draft(
    key: str,
    title: str,
    body: str,
    proof_paths: str = "",
) -> dict[str, Any]:
    """Write bugs/<KEY>/ draft MD+JSON. Agent uploads to Jira via Atlassian MCP (not hardcoded API).

    proof_paths: comma-separated or JSON list of PNG paths.
    """
    paths: list[str] = []
    raw = (proof_paths or "").strip()
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                paths = [str(x) for x in parsed]
        except json.JSONDecodeError:
            paths = [p.strip() for p in raw.split(",") if p.strip()]
    elif raw:
        paths = [p.strip() for p in raw.split(",") if p.strip()]
    return flow.file_bug_draft(key, title, body, paths)


# --- Honesty ---
@mcp.tool()
def liqa_honesty_start(case_id: str, summary: str = "", defect_class: str = "") -> dict[str, Any]:
    """Start an honesty case (20 approaches before REAL_BUG; 3 for obvious classes)."""
    store = _honesty_store()
    store[case_id] = {
        "summary": summary,
        "defect_class": (defect_class or "").strip().lower(),
        "attempts": [],
        "verdict": None,
    }
    _save_honesty(store)
    return {"ok": True, "case_id": case_id, "contract": honesty.HONESTY_CONTRACT_VERSION if honesty else "n/a"}


@mcp.tool()
def liqa_honesty_attempt(case_id: str, result: str, proof: str = "", approach: str = "") -> dict[str, Any]:
    """Record one headed approach with proof path."""
    store = _honesty_store()
    if case_id not in store:
        return {"ok": False, "error": "unknown case — call liqa_honesty_start first"}
    store[case_id].setdefault("attempts", []).append(
        {"result": result, "proof": proof, "approach": approach}
    )
    _save_honesty(store)
    summary = honesty.summarize_honesty_case(store[case_id]) if honesty else {}
    return {"ok": True, "case_id": case_id, "summary": summary}


@mcp.tool()
def liqa_honesty_verdict(case_id: str, verdict: str, defect_class: str = "") -> dict[str, Any]:
    """Set PASS | REAL_BUG | BLOCKED | N/A — enforced by honesty contract."""
    if honesty is None:
        return {"ok": False, "error": "honesty_contract missing"}
    store = _honesty_store()
    if case_id not in store:
        return {"ok": False, "error": "unknown case"}
    check = honesty.allow_verdict(store[case_id], verdict, defect_class=defect_class)
    if not check.get("ok"):
        return check
    store[case_id]["verdict"] = check.get("verdict") or verdict.upper()
    if defect_class:
        store[case_id]["defect_class"] = defect_class.strip().lower()
    _save_honesty(store)
    return {"ok": True, **check, "case": store[case_id]}


# --- Device ---
@mcp.tool()
def liqa_device_status() -> dict[str, Any]:
    """Windows device / OCR / monitor status."""
    if device_status is None:
        return {"ok": False, "error": "device_core missing — pip install mss pillow pyautogui"}
    return device_status()


@mcp.tool()
def liqa_capture(label: str = "liqa", ocr: bool = False, monitor_index: int | None = None) -> dict[str, Any]:
    """Full-desktop screenshot. OCR off by default (fast). Optional monitor_index for multi-monitor."""
    if capture_desktop is None:
        return {"ok": False, "error": "device_core missing"}
    return capture_desktop(label, monitor_index=monitor_index, ocr=ocr)


@mcp.tool()
def liqa_click(x: int, y: int, button: str = "left", clicks: int = 1) -> dict[str, Any]:
    """Visible mouse click at screen coordinates (Eyes first — never guess)."""
    if click_at is None:
        return {"ok": False, "error": "device_core missing"}
    return click_at(x, y, button=button, clicks=clicks)


@mcp.tool()
def liqa_click_text(text: str) -> dict[str, Any]:
    """OCR find text then click center. Requires Tesseract."""
    if click_text is None:
        return {"ok": False, "error": "device_core missing"}
    return click_text(text)


@mcp.tool()
def liqa_move(x: int, y: int) -> dict[str, Any]:
    """Bezier mouse move (visible)."""
    if move_mouse is None:
        return {"ok": False, "error": "device_core missing"}
    return move_mouse(x, y)


@mcp.tool()
def liqa_type(text: str, interval: float = 0.03, enter: bool = False) -> dict[str, Any]:
    """Type text via pyautogui (visible delay). Never pass passwords into chat — use Human Gate for secrets."""
    if device_type_text is None:
        return {"ok": False, "error": "device_core missing — pip install pyautogui"}
    return device_type_text(text, interval=interval, enter=enter)


@mcp.tool()
def liqa_hotkey(keys: str) -> dict[str, Any]:
    """Press hotkey combo via pyautogui, e.g. 'ctrl+s' or 'alt+tab'."""
    if device_hotkey is None:
        return {"ok": False, "error": "device_core missing — pip install pyautogui"}
    return device_hotkey(keys)


@mcp.tool()
def liqa_wait_frame(timeout_sec: float = 8.0) -> dict[str, Any]:
    """Wait until desktop pixels change (hash-only, fast)."""
    if wait_frame_change is None:
        return {"ok": False, "error": "device_core missing"}
    return wait_frame_change(timeout_sec=timeout_sec)


@mcp.tool()
def liqa_list_windows(limit: int = 40) -> dict[str, Any]:
    """List top-level Windows titles."""
    if list_windows is None:
        return {"ok": False, "error": "device_core missing"}
    return {"ok": True, "windows": list_windows(limit=limit)}


@mcp.tool()
def liqa_focus_window(title_substr: str) -> dict[str, Any]:
    """Focus a window by title substring."""
    if focus_window is None:
        return {"ok": False, "error": "device_core missing"}
    return focus_window(title_substr)


@mcp.tool()
def liqa_human_gate(kind: str = "other", prompt: str = "Human action required", timeout_sec: int = 180) -> dict[str, Any]:
    """Pause for OTP / MFA / CAPTCHA — never invent codes."""
    if _human_gate is None:
        return {"ok": False, "error": "human_gate missing", "ask_mode": True, "prompt": prompt}
    return _human_gate(kind=kind, prompt=prompt, timeout_sec=timeout_sec)


@mcp.tool()
def liqa_learn_cycle(notes: str = "", task_key: str = "") -> dict[str, Any]:
    """ISTQB completion learn cycle + speed playbook uplift."""
    base: dict[str, Any] = {"ok": True, "notes": notes}
    if extras is not None and hasattr(extras, "learn_cycle"):
        try:
            base["extras"] = extras.learn_cycle(notes=notes)
        except Exception as e:  # noqa: BLE001
            base["extras_error"] = str(e)
    if learner is not None:
        base["speed"] = learner.learn_cycle(notes=notes, task_key=task_key)
    try:
        from paths import KNOWLEDGE_ROOT as KR

        skills = list(KR.glob("*.md"))
    except Exception:  # noqa: BLE001
        skills = []
    base["skills"] = [p.name for p in skills]
    return base


@mcp.tool()
def liqa_list_skills() -> dict[str, Any]:
    """List skill packs under repo skills/ (SBTM, defect-reporting, jira-tone, book1-english, …)."""
    root = REPO_ROOT / "skills"
    files = sorted(root.rglob("*.md")) if root.exists() else []
    return {
        "ok": True,
        "skills_root": str(root),
        "files": [str(p.relative_to(root)).replace("\\", "/") for p in files],
        "count": len(files),
    }


@mcp.tool()
def liqa_orchestrator_assign(workstream: str, owner_role: str, brief: str) -> dict[str, Any]:
    """Company orchestrator: assign a workstream to a specialist role and log it."""
    flow.ensure_workspace()
    path = WORKSPACE / "agents" / "orchestrator-assignments.json"
    data: dict[str, Any] = {"assignments": []}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {"assignments": []}
    from datetime import datetime, timezone

    item = {
        "workstream": workstream,
        "owner_role": owner_role,
        "brief": brief,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    data.setdefault("assignments", []).append(item)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    role_out: dict[str, Any] = {"ok": False}
    if roles is not None and hasattr(roles, "role_dispatch"):
        role_out = roles.role_dispatch(owner_role, brief)
    return {"ok": True, "assignment": item, "role_dispatch": role_out, "path": str(path)}


@mcp.tool()
def liqa_company_status() -> dict[str, Any]:
    """Full company snapshot: engineer + ISTQB phases + roles + embedded agency specialists."""
    assigns = WORKSPACE / "agents" / "orchestrator-assignments.json"
    specs = []
    sp = REPO_ROOT / "company" / "specialists"
    if sp.exists():
        specs = sorted(p.stem for p in sp.glob("*.mdc"))
    return {
        "ok": True,
        "product": "Theja Manual QA Company",
        "identity": persona_payload().get("identity"),
        "version": VERSION,
        "flow": flow.status_payload(),
        "roles": roles.role_status() if roles else {},
        "assignments": json.loads(assigns.read_text(encoding="utf-8")) if assigns.exists() else {"assignments": []},
        "agency_specialists_embedded": specs,
        "repo": str(REPO_ROOT),
        "charter": str(REPO_ROOT / "company" / "CHARTER.md"),
        "final_product": str(REPO_ROOT / "docs" / "FINAL-PRODUCT.md"),
    }


@mcp.tool()
def liqa_fresh_task(task_key: str, title: str = "", ignore_prior_memory: bool = True) -> dict[str, Any]:
    """Start a task clean: ignore prior memories for this KEY."""
    safe = "".join(c for c in task_key if c.isalnum() or c in "-_") or "TASK"
    dest = WORKSPACE / "assignedTasks" / safe
    dest.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone

    marker = {
        "task_key": safe,
        "title": title,
        "ignore_prior_memory": bool(ignore_prior_memory),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "law": "Do not reuse prior chat conclusions for this KEY unless user overrides.",
    }
    path = dest / "FRESH-START.json"
    path.write_text(json.dumps(marker, indent=2), encoding="utf-8")
    st = flow.ensure_workspace()
    st["active_task"] = safe
    st.setdefault("fresh_starts", {})[safe] = marker
    flow.save_state(st)
    return {
        "ok": True,
        "task_key": safe,
        "path": str(path),
        "ignore_prior_memory": ignore_prior_memory,
        "next": "Call liqa_self_assign then ISTQB phase 1 via Atlassian MCP.",
    }


@mcp.tool()
def liqa_self_assign(task_key: str, brief: str = "") -> dict[str, Any]:
    """Assign yourself (company Manual QA Engineer) and dispatch all core roles."""
    safe = "".join(c for c in task_key if c.isalnum() or c in "-_") or "TASK"
    brief = brief or f"Own full Manual QA for {safe}: ISTQB 1-7, headed, honesty, Book1, bugs."
    outs = []
    chain = [
        ("orchestrator", f"Gate full run for {safe}. No phase skip."),
        ("intake", f"Intake Jira/stories/Xray for {safe}. Fresh memory."),
        ("mapper", f"SBTM experience map for {safe}. No Pass/Fail."),
        ("designer", f"NEW tests only for {safe}."),
        ("executor", f"Headed Eyes-Brain-Hands for {safe}."),
        ("honesty_referee", f"Honesty gate for {safe}."),
        ("book1_reporter", f"Book1 SHARE + bug drafts for {safe}."),
        ("learner", f"Learn cycle after {safe} close."),
    ]
    for role, instruction in chain:
        if roles and hasattr(roles, "role_dispatch"):
            outs.append(roles.role_dispatch(role, instruction))
        liqa_orchestrator_assign(f"{safe}-{role}", role, instruction)
    flow.save_md(
        "assignedTasks",
        safe,
        "self-assigned.md",
        f"# Self-assigned\n\n**Company:** Theja Manual QA Company\n**Task:** {safe}\n\n{brief}\n",
    )
    return {
        "ok": True,
        "task_key": safe,
        "assigned_to": "Theja Manual QA Company / Manual QA Engineer",
        "roles_dispatched": [o.get("role") for o in outs if isinstance(o, dict)],
        "brief": brief,
        "next": "Phase 1: Atlassian Jira intake → liqa_save_assigned_task → liqa_request_credentials.",
    }


@mcp.tool()
def liqa_await_otp_field(digits: int = 6, timeout_sec: int = 120) -> dict[str, Any]:
    """Poll OCR/clipboard for OTP digits — never invent codes; human types or copies."""
    if _await_otp is None:
        return {"ok": False, "error": "human_gate.await_otp_field missing", "ask_mode": True}
    return _await_otp(digits=digits, timeout_sec=timeout_sec)


@mcp.tool()
def liqa_ack_gate() -> dict[str, Any]:
    """Create ACK so an active Human Gate (manual_ack) resumes."""
    if _ack_gate is None:
        return {"ok": False, "error": "human_gate.ack_gate missing"}
    return _ack_gate()


@mcp.tool()
def liqa_browser_open(url: str) -> dict[str, Any]:
    """Open entry URL once in headed default browser. After: mouse-click navigation only."""
    if extras is None:
        return {"ok": False, "error": "engineer_extras missing"}
    return extras.browser_open(url)


@mcp.tool()
def liqa_sbtm_charter(
    task_key: str,
    charter_id: str,
    mission: str,
    risks: str = "",
    duration_min: int = 90,
) -> dict[str, Any]:
    """Create SBTM exploratory charter under map/<KEY>/sbtm/ (no Pass/Fail)."""
    if extras is None:
        return {"ok": False, "error": "engineer_extras missing"}
    return extras.sbtm_charter(task_key, charter_id, mission, risks, duration_min)


@mcp.tool()
def liqa_revalidate_cycle(
    task_key: str, cycle: int, summary: str, still_honest: bool
) -> dict[str, Any]:
    """Completion honesty revalidate cycle 1|2|3 — need 3 honest cycles to close."""
    if extras is None:
        return {"ok": False, "error": "engineer_extras missing"}
    return extras.revalidate_cycle(task_key, cycle, summary, still_honest)


@mcp.tool()
def liqa_seed_format_refs() -> dict[str, Any]:
    """Seed knowledgeBase harvest format refs (SSP/PF gold URLs) — then harvest live tone."""
    if extras is None:
        return {"ok": False, "error": "engineer_extras missing"}
    return extras.seed_format_refs()


@mcp.tool()
def liqa_test_case_template(parent_key: str = "") -> dict[str, Any]:
    """Emit Jira-shaped functional test template for NEW cases only."""
    if extras is None:
        return {"ok": False, "error": "engineer_extras missing"}
    return extras.test_case_template(parent_key)


@mcp.tool()
def liqa_evaluate_all() -> dict[str, Any]:
    """Re-evaluate ISTQB phases 1..7 for regressions / monitor blockers."""
    if extras is None:
        return {"ok": False, "error": "engineer_extras missing"}
    return extras.evaluate_all_phases()


@mcp.tool()
def liqa_stop_the_line(reason: str) -> dict[str, Any]:
    """Freeze live phases with a blocker (quality stop). Clear via liqa_heartbeat() empty."""
    if extras is None:
        return {"ok": False, "error": "engineer_extras missing"}
    return extras.stop_the_line(reason)


@mcp.tool()
def liqa_proof_crop(
    image_path: str,
    x: int,
    y: int,
    w: int,
    h: int,
    label: str = "proof",
    red_box: bool = True,
) -> dict[str, Any]:
    """Crop proof PNG to bbox with optional red outline for Book1 + Jira attach."""
    if extras is None:
        return {"ok": False, "error": "engineer_extras missing"}
    return extras.proof_crop(image_path, x, y, w, h, label=label, red_box=red_box)


@mcp.tool()
def liqa_list_monitors() -> dict[str, Any]:
    """List monitors for multi-monitor capture targeting."""
    if list_monitors is None:
        return {"ok": False, "error": "device_core missing"}
    return {"ok": True, "monitors": list_monitors()}


@mcp.tool()
def liqa_recursive_step(intent: str = "", wait_change: bool = False) -> dict[str, Any]:
    """One Eyes→Hands recursive step: capture + actionable summary (brain = host LLM)."""
    if recursive_control_step is None:
        return {"ok": False, "error": "device_core missing"}
    return recursive_control_step(intent=intent, wait_change=wait_change)


@mcp.tool()
def liqa_calibrate_viewport(
    origin_x: float, origin_y: float, inner_w: float = 0, inner_h: float = 0, notes: str = ""
) -> dict[str, Any]:
    """Save browser viewport→screen calibration for accurate clicks."""
    try:
        from device_core import save_viewport_calib
    except ImportError:
        return {"ok": False, "error": "device_core.save_viewport_calib missing"}
    return save_viewport_calib(origin_x, origin_y, inner_w, inner_h, notes)


@mcp.tool()
def liqa_viewport_click(vx: float, vy: float) -> dict[str, Any]:
    """Click using calibrated viewport coordinates."""
    try:
        from device_core import viewport_click
    except ImportError:
        return {"ok": False, "error": "device_core.viewport_click missing"}
    return viewport_click(vx, vy)


@mcp.tool()
def liqa_persona() -> dict[str, Any]:
    """Alias of liqa_engineer_persona — company + engineer identity."""
    return liqa_engineer_persona()


@mcp.tool()
def liqa_list_roles() -> dict[str, Any]:
    """Alias of liqa_role_list."""
    return liqa_role_list()


@mcp.tool()
def liqa_press(key: str) -> dict[str, Any]:
    """Press a single key (enter, tab, esc, …)."""
    try:
        import pyautogui

        pyautogui.FAILSAFE = True
        pyautogui.press(key)
        return {"ok": True, "key": key}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


@mcp.tool()
def liqa_hotkey_chord(keys: str) -> dict[str, Any]:
    """Hotkey from comma-separated string, e.g. 'ctrl,v' — also accepts 'ctrl+v' via liqa_hotkey."""
    if "," in keys:
        parts = [p.strip() for p in keys.split(",") if p.strip()]
        try:
            import pyautogui

            pyautogui.FAILSAFE = True
            pyautogui.hotkey(*parts)
            return {"ok": True, "keys": parts}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}
    return liqa_hotkey(keys)


@mcp.tool()
def liqa_device_loop(intent: str = "", tag: str = "loop") -> dict[str, Any]:
    """One Eyes-Brain-Hands loop step (capture + actionable summary)."""
    if device_loop_step is None:
        return {"ok": False, "error": "device_core.device_loop_step missing"}
    return device_loop_step(intent=intent, tag=tag)



@mcp.tool()
def liqa_agency_list(limit: int = 300) -> dict[str, Any]:
    """List agency-agents specialists available to LIQA orchestrator (250+)."""
    if agency is None:
        return {"ok": False, "error": "agency_mesh missing"}
    return agency.list_specialists(limit=limit)


@mcp.tool()
def liqa_agency_dispatch(specialist_id: str, workstream: str, brief: str) -> dict[str, Any]:
    """Assign an agency specialist workstream under LIQA orchestrator."""
    if agency is None:
        return {"ok": False, "error": "agency_mesh missing"}
    return agency.dispatch(specialist_id, workstream, brief)


@mcp.tool()
def liqa_mesh_status() -> dict[str, Any]:
    """Agency mesh assignment snapshot."""
    if agency is None:
        return {"ok": False, "error": "agency_mesh missing"}
    return agency.mesh_status()


@mcp.tool()
def liqa_agency_train_status() -> dict[str, Any]:
    """Status of QA training overlays for all agency specialists."""
    if agency is None:
        return {"ok": False, "error": "agency_mesh missing"}
    return agency.training_status()


@mcp.tool()
def liqa_agency_trained_prompt(specialist_id: str) -> dict[str, Any]:
    """Load the LIQA Manual-QA trained overlay for one specialist."""
    if agency is None:
        return {"ok": False, "error": "agency_mesh missing"}
    return agency.load_qa_training(specialist_id)


@mcp.tool()
def liqa_learn_speed(task_key: str = "", limit: int = 12) -> dict[str, Any]:
    """Suggest speed-up tips from prior LIQA rounds (call at planning)."""
    if learner is None:
        return {"ok": False, "error": "learner_speed missing"}
    return learner.suggest(task_key=task_key, limit=limit)


@mcp.tool()
def liqa_learn_record(
    task_key: str,
    notes: str = "",
    what_worked: str = "",
    what_slowed: str = "",
    seconds_saved_estimate: int = 0,
) -> dict[str, Any]:
    """Record a learning round to uplift future QA speed."""
    if learner is None:
        return {"ok": False, "error": "learner_speed missing"}
    return learner.record(
        task_key=task_key,
        notes=notes,
        what_worked=what_worked,
        what_slowed=what_slowed,
        seconds_saved_estimate=seconds_saved_estimate,
    )


@mcp.tool()
def liqa_resource_map() -> dict[str, Any]:
    """Map connected product sources LIQA absorbs (ManualQA, QAFusionX, agency, worker)."""
    if resources is None:
        from paths import REPO_ROOT, AGENCY_ROOT, MANUALQA_HOME, QAFUSIONX_HOME

        return {
            "ok": True,
            "liqa_home": str(REPO_ROOT),
            "sources": {
                "manualqa_agent": str(MANUALQA_HOME),
                "qafusionx": str(QAFUSIONX_HOME),
                "agency_agents": str(AGENCY_ROOT),
                "worker": str(REPO_ROOT / "apps" / "worker"),
                "control": str(REPO_ROOT / "apps" / "control"),
            },
        }
    return resources.map_resources()


@mcp.tool()
def liqa_product_status() -> dict[str, Any]:
    """Final product readiness snapshot for LIQA MCP."""
    from paths import REPO_ROOT

    tool_names = sorted(n for n in globals() if n.startswith("liqa_") and callable(globals()[n]))
    train = agency.training_status() if agency is not None else {"trained": False}
    return {
        "ok": True,
        "product": "LIQA",
        "version": VERSION,
        "home": str(REPO_ROOT),
        "tool_count": len(tool_names),
        "tools_sample": [n.replace("liqa_", "", 1) for n in tool_names[:40]],
        "guards": ["book1_share_parity", "honesty_20", "human_gate_otp", "evaluator_gate"],
        "learner": learner is not None,
        "agency_mesh": agency is not None,
        "agency_qa_trained": train,
        "message": "LIQA MCP ready — call liqa_boot to start ISTQB flow.",
    }


if __name__ == "__main__":
    mcp.run()
