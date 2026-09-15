"""Resource map — sources LIQA absorbs into one MCP product."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from paths import AGENCY_ROOT, MANUALQA_HOME, QAFUSIONX_HOME, REPO_ROOT


def map_resources() -> dict[str, Any]:
    sources = {
        "liqa_mcp": REPO_ROOT / "mcp",
        "liqa_worker": REPO_ROOT / "apps" / "worker",
        "liqa_control": REPO_ROOT / "apps" / "control",
        "manualqa_agent": MANUALQA_HOME,
        "qafusionx": QAFUSIONX_HOME,
        "agency_agents": AGENCY_ROOT,
        "book1_gold": REPO_ROOT / "artifacts" / "book1-samples",
        "skills": REPO_ROOT / "skills",
        "lolc_pack": REPO_ROOT / "packaging" / "lolc",
    }
    out = {}
    for k, p in sources.items():
        path = Path(p)
        out[k] = {
            "path": str(path),
            "exists": path.exists(),
        }
    return {
        "ok": True,
        "product": "LIQA",
        "liqa_home": str(REPO_ROOT),
        "sources": out,
        "mcp_peers": [
            "atlassian",
            "theja-humanize",
            "manualqa",
            "QAFusionX",
            "ThejaThinkingPattern",
            "ThejaUltimate",
            "theGod",
            "n8n-mcp",
            "chrome-bridge",
            "AIThejaBrowser",
        ],
        "lolc_overlay": {
            "path": str(REPO_ROOT / "packaging" / "lolc"),
            "version": "2026-09-16-lolc-fusionx-v1",
            "replaces_perfect100": False,
        },
        "message": "LIQA MCP is the primary surface; LOLC pack is a separate FusionX overlay; peers are called by the agent as needed.",
    }
