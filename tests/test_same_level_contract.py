"""Same-level contract tests — other developers must pass these before handover PASS."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MCP = ROOT / "mcp"
sys.path.insert(0, str(MCP))


def test_persona_is_liqa():
    import engineer_persona as ep

    assert ep.PERSONA_NAME == "LIQA"
    assert "Eyes" in " ".join(ep.ABSOLUTE_LAWS) or any("Eyes" in x for x in ep.ABSOLUTE_LAWS)
    assert len(ep.BOOK1_COLUMNS) == 7


def test_istqb_seven_phases():
    import laws

    assert laws.VERSION.startswith("2026-")
    assert len(laws.ISTQB_PHASES) == 7
    assert "liqa_boot" in laws.FLOW_CHART_MD


def test_server_has_enough_liqa_tools():
    src = (MCP / "server.py").read_text(encoding="utf-8")
    assert 'FastMCP("liqa"' in src or "FastMCP('liqa'" in src
    assert src.count("def liqa_") >= 70
    for name in (
        "liqa_boot",
        "liqa_book1_validate",
        "liqa_honesty_verdict",
        "liqa_learn_speed",
        "liqa_agency_dispatch",
        "liqa_fresh_task",
        "liqa_self_assign",
    ):
        assert f"def {name}" in src, name


def test_book1_share_floors():
    import book1_contract as b1

    assert b1.BOOK1_MIN_ROWS >= 110
    assert b1.BOOK1_MIN_IMAGE_COVERAGE >= 1.0
    for col, floor in b1.BOOK1_MIN_CHARS.items():
        assert floor >= 200, col


def test_gold_samples_present():
    golds = list((ROOT / "artifacts" / "book1-samples").rglob("*SHARE*.xlsx"))
    assert golds, "Need at least one SHARE gold xlsx for other developers"
    playbook = ROOT / "skills" / "SPEED-PLAYBOOK.md"
    assert playbook.exists()
    text = playbook.read_text(encoding="utf-8")
    assert "Playwright" in text or "CDP" in text
    assert "Excel" in text


def test_agency_mesh_or_catalog():
    import agency_mesh

    cat = agency_mesh.list_specialists(limit=50)
    assert cat["ok"] is True
    ids = {s["id"] for s in cat["specialists"]}
    assert "agents-orchestrator" in ids or any("orchestrator" in i for i in ids)
    # Prefer live agency-agents; else bundled catalog (≥200) is same-level OK
    if cat.get("source") == "agency-agents" and cat["count"] < 200:
        raise AssertionError(f"agency count too low for same-level: {cat['count']}")
    if cat.get("source") in ("bundled-catalog", "core-fallback"):
        assert cat["count"] >= 15, f"catalog too small: {cat['count']}"
        if cat.get("source") == "bundled-catalog":
            assert cat["count"] >= 200, f"bundled catalog incomplete: {cat['count']}"
    elif Path(cat["agency_root"]).exists() and (Path(cat["agency_root"]) / ".cursor" / "rules").exists():
        assert cat["count"] >= 200, f"agency count too low for same-level: {cat['count']}"


def test_learner_speed_tips():
    import learner_speed

    out = learner_speed.suggest(task_key="PF-55248", limit=8)
    assert out["ok"] is True
    assert len(out["tips"]) >= 3


def test_resource_map():
    import resource_map

    m = resource_map.map_resources()
    assert m["ok"] is True
    assert m["sources"]["liqa_mcp"]["exists"] is True


def test_quality_docs_exist():
    for rel in (
        "docs/QUALITY-CONTRACT.md",
        "docs/DEVELOPER-HANDOVER.md",
        "docs/SAME-LEVEL-ACCEPTANCE.md",
        "docs/FINAL-PRODUCT.md",
    ):
        assert (ROOT / rel).exists(), rel


def test_secrets_not_committed_example_only():
    example = ROOT / "secrets" / "tmp-creds.example.json"
    assert example.exists()
    data = json.loads(example.read_text(encoding="utf-8"))
    assert "REPLACE" in json.dumps(data).upper() or data.get("maker_password") == "REPLACE_ME"
