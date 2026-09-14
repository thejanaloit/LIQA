"""Train all agency specialists with LIQA Manual-QA overlays (prompt specialization)."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MCP = ROOT / "mcp"
OUT = ROOT / "packaging" / "industry" / "agency-qa-trained"
CATALOG = ROOT / "packaging" / "industry" / "agency-catalog.json"

# Universal LIQA QA doctrine injected into EVERY specialist
UNIVERSAL_QA = """
## LIQA Manual QA training (mandatory)

You operate inside LIQA (Live Intelligent QA) for headed Manual QA execution.

Doctrine:
1. ISTQB CTFL 7 activities — never skip phases.
2. Eyes → Brain → Hands on a real desktop. No headless Pass/Fail as the method.
3. Book1 SHARE method: full English + embedded PNG every row; validate before share.
4. Honesty-20 before REAL_BUG; found-a-way = PASS; missing data = BLOCKED not REAL_BUG.
5. Human Gate for OTP/MFA/CAPTCHA — never invent codes.
6. One headed session; entry URL once; mouse+keyboard after.
7. 2 QA humans only for gates + sign-off; YOU help execution / evidence / review — not replace Human Gate.
8. Fresh task = ignore prior KEY memory unless owner says reuse.
9. Prefer Playwright CDP for SPA; minimize Excel before proof captures.
10. Call learn tips (SPEED-PLAYBOOK) and leave artifacts under the LIQA workspace.

Output always: evidence paths, plain English findings, and whether PASS / BLOCKED / REAL_BUG / needs Human Gate.
""".strip()

TRACKS: dict[str, dict[str, Any]] = {
    "orchestrator": {
        "keywords": ["orchestrator", "multi-agent", "chief-of-staff", "project-shepherd", "senior-project"],
        "mission": "Lead LIQA phase gates, specialist handoffs, and stop-the-line on missing evidence.",
        "qa_focus": ["phase order", "assignment", "blocker routing", "sign-off readiness"],
    },
    "execution": {
        "keywords": ["tester", "qa", "api-tester", "test-automation", "performance-benchmark", "evidence", "reality-checker", "test-results"],
        "mission": "Execute headed cases, capture proof, run honesty loops, draft Book1 rows.",
        "qa_focus": ["headed walk", "proof PNG", "honesty-20", "Book1 rows"],
    },
    "design": {
        "keywords": ["product-manager", "workflow-architect", "ux-researcher", "ux-architect", "sprint-prioritizer"],
        "mission": "Turn stories into test conditions, charters, and sufficiency counts.",
        "qa_focus": ["AC → cases", "SBTM charter", "coverage gaps"],
    },
    "security": {
        "keywords": ["security", "threat", "privacy", "compliance", "penetration", "secops", "identity-access"],
        "mission": "Security/privacy checks during Manual QA without inventing exploits against unauthorized systems.",
        "qa_focus": ["authz", "session", "secrets exposure", "PCI/PII in proofs"],
    },
    "platform": {
        "keywords": ["devops", "sre", "platform", "infrastructure", "network", "cloud", "finops"],
        "mission": "Keep Worker/Control healthy: Session 0 fail-closed, outbound-only, vault inject.",
        "qa_focus": ["worker health", "locks", "autologon", "capture disk"],
    },
    "docs": {
        "keywords": ["technical-writer", "document", "meeting-notes", "executive-summary"],
        "mission": "Write Book1 English, bug narratives, and sign-off notes in SHARE tone.",
        "qa_focus": ["full English cells", "bug crop captions", "Jira tone"],
    },
    "data": {
        "keywords": ["data-", "analytics", "database", "statistician", "spatial-data", "gis"],
        "mission": "Find test data from Jira/Xray evidence; never invent account/receipt numbers.",
        "qa_focus": ["migrated accounts", "fixtures", "BLOCKED vs bug"],
    },
    "frontend": {
        "keywords": ["frontend", "ui-", "accessibility", "cms", "wordpress", "drupal"],
        "mission": "UI/accessibility headed checks; map every control reachable from stories.",
        "qa_focus": ["map buttons", "a11y", "SPA forms"],
    },
    "backend": {
        "keywords": ["backend", "api-", "software-architect", "rag-", "mcp-builder"],
        "mission": "API/contract checks that support GUI truth — GUI proof still required for GUI bugs.",
        "qa_focus": ["API vs UI parity", "idempotency", "error states"],
    },
    "gtm": {
        "keywords": ["sales", "marketing", "seo", "content", "brand", "growth", "linkedin", "tiktok"],
        "mission": "Support LIQA product GTM and demo scripts — not UAT clicking unless assigned.",
        "qa_focus": ["demo script", "SKU messaging", "2QA model story"],
    },
    "domain": {
        "keywords": [],
        "mission": "Apply domain expertise as a reviewer on Manual QA evidence for this product area.",
        "qa_focus": ["domain risks", "edge cases", "acceptance critique"],
    },
}


def _track_for(sid: str) -> str:
    s = sid.lower()
    for track, meta in TRACKS.items():
        if track == "domain":
            continue
        for kw in meta["keywords"]:
            if kw in s:
                return track
    return "domain"


def _trained_prompt(sid: str, description: str, track: str) -> str:
    meta = TRACKS[track]
    return f"""# {sid} — LIQA QA-trained specialist

Original agency role: {description or sid}
LIQA track: {track}

## Mission under LIQA
{meta['mission']}

## QA focus
{chr(10).join(f'- {x}' for x in meta['qa_focus'])}

{UNIVERSAL_QA}

## When dispatched
1. Read the workstream brief.
2. Stay inside your track; hand off via orchestrator if out of scope.
3. Return evidence paths + verdict recommendation only.
4. Never invent OTP, passwords, or business keys.
"""


def train_all() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    if CATALOG.exists():
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        specialists = catalog.get("specialists") or []
    else:
        import sys

        sys.path.insert(0, str(MCP))
        import agency_mesh

        specialists = agency_mesh.list_specialists(limit=500)["specialists"]

    index: list[dict[str, Any]] = []
    by_track: dict[str, int] = {}
    for s in specialists:
        sid = s.get("id") or ""
        if not sid:
            continue
        track = _track_for(sid)
        by_track[track] = by_track.get(track, 0) + 1
        prompt = _trained_prompt(sid, s.get("description") or "", track)
        path = OUT / f"{sid}.md"
        path.write_text(prompt, encoding="utf-8")
        index.append(
            {
                "id": sid,
                "track": track,
                "trained": True,
                "overlay": f"packaging/industry/agency-qa-trained/{sid}.md",
                "description": (s.get("description") or "")[:200],
            }
        )

    manifest = {
        "product": "LIQA",
        "training": "Manual QA / ISTQB / Book1 SHARE / 2QA ops",
        "version": "2026-09-14-qa-trained-v1",
        "trainedAt": datetime.now(timezone.utc).isoformat(),
        "count": len(index),
        "by_track": by_track,
        "universal_doctrine": UNIVERSAL_QA,
        "specialists": index,
    }
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (ROOT / "packaging" / "industry" / "agency-qa-trained-index.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    # SPEED playbook note
    skills = ROOT / "skills"
    skills.mkdir(parents=True, exist_ok=True)
    note = skills / "AGENCY-QA-TRAINED.md"
    note.write_text(
        f"# Agency QA-trained pack\n\nAll {len(index)} specialists have LIQA Manual-QA overlays under "
        f"`packaging/industry/agency-qa-trained/`.\n\nTracks: {json.dumps(by_track)}\n",
        encoding="utf-8",
    )
    return {"ok": True, "count": len(index), "by_track": by_track, "out": str(OUT)}


if __name__ == "__main__":
    print(json.dumps(train_all(), indent=2))
