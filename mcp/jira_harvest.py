"""Mandatory Jira full harvest gate for LIQA intake.

Before headed map / Book1 design, the agent MUST harvest from Atlassian:
- Assigned / clone KEY fields + comments
- Linked stories (Cloners, Relates, Tests)
- Feature / epic / parent issues
- ALL attachments (PDF, images, msg) into knowledgeBase/<KEY>/jira-attachments/
- Confluence pages linked from description when present

This module records a checklist; announce_planning_done / phase-1 complete
should not be treated as honest if harvest.ok is false.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from paths import WORKSPACE

REQUIRED_BUCKETS = (
    "issue_fields",
    "linked_issues",
    "feature_or_epic",
    "attachments",
    "existing_xray",
    "comments_or_description",
)


def _harvest_dir(task_key: str) -> Path:
    d = WORKSPACE / "knowledgeBase" / task_key / "jira-harvest"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _attachments_dir(task_key: str) -> Path:
    d = WORKSPACE / "knowledgeBase" / task_key / "jira-attachments"
    d.mkdir(parents=True, exist_ok=True)
    return d


def harvest_status(task_key: str) -> dict[str, Any]:
    path = _harvest_dir(task_key) / "HARVEST.json"
    if not path.exists():
        return {
            "ok": False,
            "task_key": task_key,
            "complete": False,
            "missing": list(REQUIRED_BUCKETS),
            "message": "No harvest yet. Call liqa_jira_harvest_record after Atlassian pull.",
            "path": str(path),
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [b for b in REQUIRED_BUCKETS if not data.get("buckets", {}).get(b)]
    att_dir = _attachments_dir(task_key)
    files = sorted(p.name for p in att_dir.iterdir() if p.is_file()) if att_dir.exists() else []
    complete = len(missing) == 0 and (
        not data.get("attachments_expected") or len(files) >= int(data.get("attachments_expected") or 0)
    )
    # attachments bucket true + expected 0 is OK; if expected > 0 need files
    if data.get("buckets", {}).get("attachments") and int(data.get("attachments_expected") or 0) > 0:
        complete = complete and len(files) >= int(data["attachments_expected"])
    return {
        "ok": True,
        "task_key": task_key,
        "complete": complete and len(missing) == 0,
        "missing": missing,
        "attachments_on_disk": files,
        "attachments_expected": data.get("attachments_expected"),
        "sources": data.get("sources", []),
        "notes": data.get("notes", ""),
        "updated_at": data.get("updated_at"),
        "path": str(path),
        "law": "Do not start headed map until harvest.complete is true.",
    }


def record_harvest(
    task_key: str,
    *,
    sources: list[str] | None = None,
    buckets: dict[str, bool] | None = None,
    attachments_expected: int = 0,
    attachment_names: list[str] | None = None,
    notes: str = "",
    merge: bool = True,
) -> dict[str, Any]:
    path = _harvest_dir(task_key) / "HARVEST.json"
    prev: dict[str, Any] = {}
    if merge and path.exists():
        prev = json.loads(path.read_text(encoding="utf-8"))
    bucket_state = dict(prev.get("buckets") or {})
    for k in REQUIRED_BUCKETS:
        bucket_state.setdefault(k, False)
    if buckets:
        for k, v in buckets.items():
            if k in REQUIRED_BUCKETS:
                bucket_state[k] = bool(v)
    src = list(prev.get("sources") or [])
    for s in sources or []:
        if s and s not in src:
            src.append(s)
    names = list(prev.get("attachment_names") or [])
    for n in attachment_names or []:
        if n and n not in names:
            names.append(n)
    expected = max(int(prev.get("attachments_expected") or 0), int(attachments_expected or 0), len(names))
    payload = {
        "task_key": task_key,
        "buckets": bucket_state,
        "sources": src,
        "attachments_expected": expected,
        "attachment_names": names,
        "notes": notes or prev.get("notes", ""),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "required_buckets": list(REQUIRED_BUCKETS),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md = _harvest_dir(task_key) / "HARVEST.md"
    lines = [
        f"# Jira harvest — {task_key}",
        "",
        f"Updated: {payload['updated_at']}",
        "",
        "## Sources",
    ]
    lines.extend([f"- {s}" for s in src] if src else ["- (none)"])
    lines.extend(
        [
            "",
            "## Buckets",
        ]
    )
    lines.extend([f"- [{'x' if bucket_state[b] else ' '}] {b}" for b in REQUIRED_BUCKETS])
    lines.extend(
        [
            "",
            f"Attachments expected: {expected}",
            f"Attachment names: {', '.join(names) if names else '(none)'}",
            "",
            notes,
            "",
            "## Law",
            "MUST pull assigned KEY + linked Cloners/Relates/Test + feature/epic/parent + ALL attachments",
            "into knowledgeBase/<KEY>/jira-attachments/ BEFORE headed map.",
        ]
    )
    md.write_text("\n".join(lines), encoding="utf-8")
    st = harvest_status(task_key)
    st["recorded"] = True
    st["md"] = str(md)
    return st


def checklist_for_agent() -> dict[str, Any]:
    return {
        "ok": True,
        "mandatory_before_headed_map": [
            "getJiraIssue(*all) for assigned/clone KEY",
            "Follow issuelinks: Cloners, Relates, Test (is tested by / tests)",
            "Open feature/epic/parent (e.g. PF-50130) even if attachments are empty on QA clone",
            "Download EVERY attachment (PDF/PNG/msg) to knowledgeBase/<KEY>/jira-attachments/",
            "Extract PDF text to knowledgeBase/<KEY>/*.extracted.md",
            "Save comments + description into UserStories/<KEY>/",
            "Clone existing Xray into ExistingTestCases/<KEY>/ (read-only)",
            "Call liqa_jira_harvest_record then liqa_jira_harvest_status until complete=true",
        ],
        "tool": "liqa_jira_harvest_record / liqa_jira_harvest_status",
        "folder": "knowledgeBase/<KEY>/jira-attachments/",
    }
