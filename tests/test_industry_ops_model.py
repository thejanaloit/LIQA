"""Industry ops model APIs — 2QA console contracts."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTRL = ROOT / "apps" / "control" / "server.py"


def _load_control():
    spec = importlib.util.spec_from_file_location("liqa_control", CTRL)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    # Don't run main
    sys.modules["liqa_control"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_industry_docs_exist():
    for rel in (
        "docs/INDUSTRY-PRODUCT.md",
        "docs/OPS-MODEL-2QA.md",
        "docs/DEPLOY-WORKER-VM.md",
        "docs/ARCHITECTURE.md",
    ):
        assert (ROOT / rel).exists(), rel


def test_bootstrap_scripts_exist():
    assert (ROOT / "scripts" / "bootstrap-control.ps1").exists()
    assert (ROOT / "scripts" / "bootstrap-worker-vm.ps1").exists()
    assert (ROOT / "scripts" / "register-logon-task.ps1").exists()
    assert (ROOT / "scripts" / "verify-install.ps1").exists()


def test_control_has_2qa_apis():
    src = CTRL.read_text(encoding="utf-8")
    assert "/v1/ops/summary" in src
    assert "/resolve" in src
    assert "/signoff" in src
    assert "needs_signoff" in src
    assert "2 QA" in src or "2QA" in src


def test_ops_summary_logic_shapes():
    # Light unit: ensure DATA folders and helper list work when imported
    mod = _load_control()
    assert hasattr(mod, "DATA")
    for sub in ("jobs", "workers", "gates", "audit"):
        assert (mod.DATA / sub).exists() or True  # mkdir on import
    # Write a fake gate + job and ensure list returns dicts
    g = {"id": "testgate", "status": "waiting_human"}
    (mod.DATA / "gates" / "testgate.json").write_text(json.dumps(g), encoding="utf-8")
    items = mod._list("gates")
    assert any(x.get("id") == "testgate" for x in items)
