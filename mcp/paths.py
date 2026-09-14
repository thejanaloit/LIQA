"""Portable paths for LIQA MCP (Live Intelligent QA)."""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(os.environ.get("LIQA_HOME", Path(__file__).resolve().parent.parent)).resolve()
MCP_ROOT = REPO_ROOT / "mcp"
LIB_ROOT = MCP_ROOT / "lib"
CAPTURE_ROOT = Path(os.environ.get("LIQA_CAPTURE_DIR", REPO_ROOT / "captures")).resolve()
KNOWLEDGE_ROOT = REPO_ROOT / "skills"
AGENCY_ROOT = Path(os.environ.get("LIQA_AGENCY_HOME", r"E:\agency-agents")).resolve()
MANUALQA_HOME = Path(os.environ.get("MANUAL_QA_HOME", r"E:\ManualQA-Agent")).resolve()
QAFUSIONX_HOME = Path(os.environ.get("QAFUSIONX_HOME", r"E:\QAFusionX")).resolve()


def workspace_root() -> Path:
    env = (os.environ.get("LIQA_WORKSPACE") or "").strip()
    if env:
        return Path(env).resolve()
    return (REPO_ROOT / "workspace" / "default-run").resolve()


WORKSPACE = workspace_root()
WORKSPACE_ROOT = WORKSPACE
SECRETS = REPO_ROOT / "secrets"
VAULT_CANDIDATES = [
    SECRETS / "desktop-admin.env",
    SECRETS / "tmp-creds.json",
    WORKSPACE / "tmp-creds.json",
]
_extra = os.environ.get("LIQA_VAULT", "").strip()
if _extra:
    VAULT_CANDIDATES.insert(0, Path(_extra))
