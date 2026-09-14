"""Install LIQA into Cursor mcp.json — portable paths for any developer machine."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _detect_agency() -> str:
    env = (os.environ.get("LIQA_AGENCY_HOME") or "").strip()
    if env and Path(env).exists():
        return str(Path(env).resolve()).replace("\\", "/")
    candidates = [
        ROOT.parent / "agency-agents",
        Path(r"E:/agency-agents"),
        Path.home() / "agency-agents",
        Path.home() / "src" / "agency-agents",
    ]
    for c in candidates:
        if c.exists():
            return str(c.resolve()).replace("\\", "/")
    return str((ROOT.parent / "agency-agents").resolve()).replace("\\", "/")


def _detect_manualqa() -> str:
    env = (os.environ.get("MANUAL_QA_HOME") or "").strip()
    if env and Path(env).exists():
        return str(Path(env).resolve()).replace("\\", "/")
    for c in (
        ROOT.parent / "ManualQA-Agent",
        Path(r"E:/ManualQA-Agent"),
        Path(r"E:/QAFusionX/manualQA"),
    ):
        if c.exists():
            return str(c.resolve()).replace("\\", "/")
    return str((ROOT.parent / "ManualQA-Agent").resolve()).replace("\\", "/")


def _detect_qafusionx() -> str:
    env = (os.environ.get("QAFUSIONX_HOME") or "").strip()
    if env and Path(env).exists():
        return str(Path(env).resolve()).replace("\\", "/")
    for c in (ROOT.parent / "QAFusionX", Path(r"E:/QAFusionX")):
        if c.exists():
            return str(c.resolve()).replace("\\", "/")
    return str((ROOT.parent / "QAFusionX").resolve()).replace("\\", "/")


def main() -> None:
    home = str(ROOT.resolve()).replace("\\", "/")
    server = f"{home}/mcp/server.py"
    p = Path.home() / ".cursor" / "mcp.json"
    raw = p.read_text(encoding="utf-8-sig") if p.exists() else '{"mcpServers":{}}'
    d = json.loads(raw)
    d.setdefault("mcpServers", {})["liqa"] = {
        "command": "py",
        "args": ["-3", server],
        "env": {
            "PYTHONIOENCODING": "utf-8",
            "LIQA_HOME": home,
            "LIQA_AGENCY_HOME": _detect_agency(),
            "MANUAL_QA_HOME": _detect_manualqa(),
            "QAFUSIONX_HOME": _detect_qafusionx(),
        },
    }
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((json.dumps(d, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print("Installed LIQA ->", p)
    print(json.dumps(d["mcpServers"]["liqa"], indent=2))
    print("\nNext: Reload MCP in Cursor, then say: use LIQA")
    print("Same-level gate: pytest tests/test_same_level_contract.py")


if __name__ == "__main__":
    main()
