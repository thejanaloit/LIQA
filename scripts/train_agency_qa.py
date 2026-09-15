"""Train all agency specialists with LIQA Manual-QA Perfect-100 overlays (PF-59486 bar)."""
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

TRAINING_VERSION = "2026-09-16-qa-trained-perfect-100-v2"
PERFECT_REF = "PF-59486"

# Universal LIQA QA doctrine injected into EVERY specialist (Perfect-100)
UNIVERSAL_QA = """
## LIQA Manual QA training — PERFECT-100 (mandatory)

You operate inside LIQA (Live Intelligent QA) for headed Manual QA execution.
**Perfect-100 reference run: PF-59486** (clone of PF-55248). Match or beat that kit.
Doctrine file: skills/PERFECT-100-PF-59486-GOLD.md

Doctrine:
1. ISTQB CTFL 7 activities — never skip phases. All must reach `done`.
2. Eyes → Brain → Hands on a real desktop. No headless Pass/Fail as the method.
3. Book1 SHARE method: full English + embedded PNG every row; ≥110 rows; validate before share.
4. Honesty-20 before REAL_BUG; obvious classes (http_5xx, blank_shell, …) need 3 headed repros; found-a-way = PASS.
5. Human Gate for OTP/MFA/CAPTCHA — never invent codes.
6. One headed session; entry URL once; mouse+keyboard after (one address-bar recovery allowed if tiles miss).
7. 2 QA humans only for gates + sign-off; YOU help execution / evidence / review — not replace Human Gate.
8. Fresh task = ignore prior KEY memory unless owner says reuse.
9. Sigiri Xray lock: Action|Data|Expected Result; UI RPA CSV import (subprocess if asyncio); never Attachments.
10. BUG DEDUPE: search open twins before createJiraIssue; Relates oldest open + comment proof.
11. Call learn tips (SPEED-PLAYBOOK) and leave artifacts under the LIQA workspace.
12. Agency mesh: orchestrator assigns; every specialist returns evidence paths + verdict recommendation only.

Output always: evidence paths, plain English findings, and whether PASS / BLOCKED / REAL_BUG / needs Human Gate.
""".strip()

TRACKS: dict[str, dict[str, Any]] = {
    "orchestrator": {
        "keywords": ["orchestrator", "multi-agent", "chief-of-staff", "project-shepherd", "senior-project"],
        "mission": "Lead LIQA Perfect-100 phase gates, specialist handoffs, and stop-the-line on missing evidence.",
        "qa_focus": ["phase order", "assignment", "blocker routing", "Perfect-100 sign-off readiness"],
    },
    "execution": {
        "keywords": ["tester", "qa", "api-tester", "test-automation", "performance-benchmark", "evidence", "reality-checker", "test-results"],
        "mission": "Execute headed cases to PF-59486 bar, capture proof, run honesty loops, draft Book1 rows.",
        "qa_focus": ["headed walk", "proof PNG", "honesty-20 / obvious-3", "Book1 rows", "bug dedupe"],
    },
    "design": {
        "keywords": ["product-manager", "workflow-architect", "ux-researcher", "ux-architect", "sprint-prioritizer"],
        "mission": "Turn stories into path-split Sigiri cases, charters, and sufficiency counts.",
        "qa_focus": ["AC → path packs", "SBTM charter", "coverage gaps", "PF-59194 format"],
    },
    "security": {
        "keywords": ["security", "threat", "privacy", "compliance", "penetration", "secops", "identity-access"],
        "mission": "Security/privacy checks during Manual QA without inventing exploits against unauthorized systems.",
        "qa_focus": ["authz", "session", "secrets exposure", "PCI/PII in proofs"],
    },
    "platform": {
        "keywords": ["devops", "sre", "platform", "infrastructure", "network", "cloud", "finops"],
        "mission": "Keep Worker/Control healthy: Session 0 fail-closed, outbound-only, vault inject, disk space for Book1.",
        "qa_focus": ["worker health", "locks", "autologon", "capture disk", "subprocess Xray RPA"],
    },
    "docs": {
        "keywords": ["technical-writer", "document", "meeting-notes", "executive-summary"],
        "mission": "Write Book1 English, bug narratives, and Perfect-100 sign-off notes in SHARE tone.",
        "qa_focus": ["full English cells", "bug crop captions", "Jira tone", "Story closeout comment"],
    },
    "data": {
        "keywords": ["data-", "analytics", "database", "statistician", "spatial-data", "gis"],
        "mission": "Find test data from Jira/Xray evidence; never invent account/receipt numbers.",
        "qa_focus": ["migrated accounts", "fixtures", "BLOCKED vs bug"],
    },
    "frontend": {
        "keywords": ["frontend", "ui-", "accessibility", "cms", "wordpress", "drupal"],
        "mission": "UI/accessibility headed checks; map every control; blue-pixel / OCR click discipline.",
        "qa_focus": ["map buttons", "a11y", "SPA forms", "Create New locate"],
    },
    "backend": {
        "keywords": ["backend", "api-", "software-architect", "rag-", "mcp-builder"],
        "mission": "API/contract checks that support GUI truth — GUI proof still required for GUI bugs.",
        "qa_focus": ["API vs UI parity", "idempotency", "error states", "Trace ID capture"],
    },
    "gtm": {
        "keywords": ["sales", "marketing", "seo", "content", "brand", "growth", "linkedin", "tiktok"],
        "mission": "Support LIQA product GTM and demo scripts — not UAT clicking unless assigned.",
        "qa_focus": ["demo script", "SKU messaging", "2QA model story", "Perfect-100 pitch"],
    },
    "domain": {
        "keywords": [],
        "mission": "Apply domain expertise as a reviewer on Manual QA evidence for this product area at Perfect-100 bar.",
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
    return f"""# {sid} — LIQA QA-trained specialist (Perfect-100)

Original agency role: {description or sid}
LIQA track: {track}
Perfect-100 reference: {PERFECT_REF}

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
5. Match PF-59486 Perfect-100 smoothness or stop-the-line with blocker text.
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
        "training": "Manual QA Perfect-100 / ISTQB / Book1 SHARE / Sigiri / 2QA ops",
        "perfect100_ref": PERFECT_REF,
        "version": TRAINING_VERSION,
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
    skills = ROOT / "skills"
    skills.mkdir(parents=True, exist_ok=True)
    note = skills / "AGENCY-QA-TRAINED.md"
    note.write_text(
        f"# Agency QA-trained pack — Perfect-100\n\n"
        f"**Reference run:** {PERFECT_REF}\n"
        f"**Training version:** `{TRAINING_VERSION}`\n\n"
        f"All {len(index)} specialists have LIQA Manual-QA Perfect-100 overlays under "
        f"`packaging/industry/agency-qa-trained/`.\n\n"
        f"Doctrine: `skills/PERFECT-100-PF-59486-GOLD.md`\n\n"
        f"Tracks: {json.dumps(by_track)}\n",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "count": len(index),
        "by_track": by_track,
        "out": str(OUT),
        "version": TRAINING_VERSION,
        "perfect100_ref": PERFECT_REF,
    }


if __name__ == "__main__":
    print(json.dumps(train_all(), indent=2))
