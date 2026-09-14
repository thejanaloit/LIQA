"""Rewrite ManualQA server.py copy into LIQA-branded FastMCP."""
from __future__ import annotations

import re
from pathlib import Path

src = Path(r"E:\LIQA\mcp\server.py")
text = src.read_text(encoding="utf-8")

text = text.replace('"""\nManualQA-Agent MCP', '"""\nLIQA MCP — Live Intelligent QA')
text = text.replace('Trigger: "use ManualQA" / "manualqa agent" / "manualqa mcp"', 'Trigger: "use LIQA" / "liqa agent" / "liqa mcp"')
text = text.replace("Identity: You ARE the Manual QA Engineer", "Identity: You ARE the LIQA Engineer (Manual QA clone)")
text = text.replace('FastMCP("manualqa"', 'FastMCP("liqa"')
text = text.replace("def mqa_", "def liqa_")
text = text.replace("mqa_boot", "liqa_boot")
text = text.replace("mqa_orchestrator_assign", "liqa_orchestrator_assign")
text = text.replace("mqa_book1_validate", "liqa_book1_validate")
text = text.replace('label: str = "mqa"', 'label: str = "liqa"')

needle = "try:\n    from mcp.server.fastmcp import FastMCP"
extra = """try:
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

"""
if "import agency_mesh" not in text:
    text = text.replace(needle, extra + needle)

append = '''

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
        "message": "LIQA MCP ready — call liqa_boot to start ISTQB flow.",
    }

'''

if "def liqa_agency_list" not in text:
    if "\nif __name__" in text:
        text = text.replace("\nif __name__", append + "\nif __name__")
    else:
        text += append

m = re.search(
    r"@mcp\.tool\(\)\ndef liqa_learn_cycle\(notes: str = \"\"\) -> dict\[str, Any\]:.*?(?=\n@mcp\.tool|\nif __name__)",
    text,
    re.S,
)
if m and "learner.learn_cycle" not in m.group(0):
    new_fn = '''@mcp.tool()
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

'''
    text = text[: m.start()] + new_fn + text[m.end() :]

src.write_text(text, encoding="utf-8")
print("ok", src)
print("liqa_defs", text.count("def liqa_"))
print("agency", "import agency_mesh" in text)
