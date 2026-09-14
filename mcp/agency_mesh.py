"""Agency-agents mesh — index and dispatch specialist roles into LIQA runs."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from paths import AGENCY_ROOT, WORKSPACE

# Core QA cell always available even if agency-agents path missing
CORE_SPECIALISTS = [
    "agents-orchestrator",
    "evidence-collector",
    "reality-checker",
    "senior-project-manager",
    "multi-agent-systems-architect",
    "test-results-analyzer",
    "test-automation-engineer",
    "product-manager",
    "workflow-architect",
    "code-reviewer",
    "technical-writer",
    "api-tester",
    "accessibility-auditor",
    "performance-benchmarker",
    "incident-responder",
]


def _agents_dir() -> Path:
    rules = AGENCY_ROOT / ".cursor" / "rules"
    if rules.is_dir():
        return rules
    return AGENCY_ROOT


def list_specialists(limit: int = 300) -> dict[str, Any]:
    root = _agents_dir()
    all_items: list[dict[str, Any]] = []
    source = "agency-agents"
    if root.is_dir() and any(root.glob("*.mdc")):
        for p in sorted(root.glob("*.mdc")):
            name = p.stem
            desc = ""
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                m = re.search(r"(?m)^description:\s*(.+)$", text)
                if m:
                    desc = m.group(1).strip().strip("'\"")
                else:
                    for line in text.splitlines():
                        s = line.strip()
                        if s and not s.startswith("---") and not s.startswith("description"):
                            desc = s[:240]
                            break
            except Exception:  # noqa: BLE001
                desc = ""
            all_items.append({"id": name, "path": str(p), "description": desc})
    else:
        # Bundled catalog for Worker VMs without agency-agents checkout
        from paths import REPO_ROOT

        catalog = REPO_ROOT / "packaging" / "industry" / "agency-catalog.json"
        if catalog.exists():
            source = "bundled-catalog"
            try:
                data = json.loads(catalog.read_text(encoding="utf-8"))
                for s in data.get("specialists") or []:
                    all_items.append(
                        {
                            "id": s.get("id") or "",
                            "path": s.get("path") or str(catalog),
                            "description": s.get("description") or "",
                            "bundled": True,
                        }
                    )
            except Exception:  # noqa: BLE001
                source = "core-fallback"
        else:
            source = "core-fallback"

    have = {i["id"] for i in all_items}
    for c in CORE_SPECIALISTS:
        if c not in have:
            all_items.append({"id": c, "path": "", "description": "core LIQA specialist", "core": True})
    total = len(all_items)
    items = all_items[: max(1, int(limit))]
    return {
        "ok": True,
        "agency_root": str(AGENCY_ROOT),
        "source": source,
        "count": total,
        "returned": len(items),
        "specialists": items,
        "core": CORE_SPECIALISTS,
    }


def _assign_log() -> Path:
    d = WORKSPACE / "agents" / "mesh"
    d.mkdir(parents=True, exist_ok=True)
    return d / "assignments.jsonl"


def _trained_dir() -> Path:
    from paths import REPO_ROOT

    return REPO_ROOT / "packaging" / "industry" / "agency-qa-trained"


def training_status() -> dict[str, Any]:
    d = _trained_dir()
    manifest = d / "MANIFEST.json"
    if not manifest.exists():
        return {
            "ok": False,
            "trained": False,
            "hint": "Run: py -3 scripts/train_agency_qa.py",
            "path": str(d),
        }
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return {
        "ok": True,
        "trained": True,
        "count": data.get("count"),
        "by_track": data.get("by_track"),
        "version": data.get("version"),
        "trainedAt": data.get("trainedAt"),
        "path": str(d),
    }


def load_qa_training(specialist_id: str) -> dict[str, Any]:
    path = _trained_dir() / f"{specialist_id}.md"
    if not path.exists():
        return {"ok": False, "trained": False, "id": specialist_id, "path": str(path)}
    return {
        "ok": True,
        "trained": True,
        "id": specialist_id,
        "path": str(path),
        "overlay": path.read_text(encoding="utf-8"),
    }


def dispatch(specialist_id: str, workstream: str, brief: str) -> dict[str, Any]:
    catalog = list_specialists()
    match = next((s for s in catalog["specialists"] if s["id"] == specialist_id), None)
    if match is None:
        match = next((s for s in catalog["specialists"] if specialist_id in s["id"]), None)
    if match is None:
        return {
            "ok": False,
            "error": f"specialist not found: {specialist_id}",
            "hint": "Call liqa_agency_list",
        }
    trained = load_qa_training(match["id"])
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "specialist": match["id"],
        "workstream": workstream,
        "brief": brief,
        "path": match.get("path", ""),
        "qa_trained": bool(trained.get("trained")),
        "qa_overlay": trained.get("path") if trained.get("trained") else None,
    }
    with _assign_log().open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    role_dir = WORKSPACE / "agents" / "mesh" / match["id"]
    role_dir.mkdir(parents=True, exist_ok=True)
    (role_dir / "latest.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
    if trained.get("trained"):
        (role_dir / "QA-TRAINED.md").write_text(trained["overlay"], encoding="utf-8")
    instruction = (
        f"Operate as QA-TRAINED agency specialist '{match['id']}' for workstream '{workstream}'. "
        f"Brief: {brief}. Obey LIQA Manual-QA overlay. Return evidence paths only."
    )
    if trained.get("trained"):
        instruction = trained["overlay"] + "\n\n## Workstream brief\n" + brief
    return {
        "ok": True,
        "assigned": row,
        "qa_trained": bool(trained.get("trained")),
        "instruction": instruction,
    }


def mesh_status() -> dict[str, Any]:
    log = _assign_log()
    recent: list[dict[str, Any]] = []
    if log.exists():
        lines = log.read_text(encoding="utf-8").splitlines()[-40:]
        for line in lines:
            try:
                recent.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    catalog = list_specialists()
    train = training_status()
    return {
        "ok": True,
        "specialist_count": catalog["count"],
        "qa_trained": train,
        "assignments_recent": recent,
        "agency_root": catalog["agency_root"],
        "core": CORE_SPECIALISTS,
    }
