"""Jira/Confluence — OAuth stub + read-only Xray. Never edit/delete existing tests."""
from __future__ import annotations

import os
from typing import Any

OAUTH = {
    "authorizationUrl": "https://auth.atlassian.com/authorize",
    "tokenUrl": "https://auth.atlassian.com/oauth/token",
    "scopes": ["read:jira-work", "read:confluence-content.all"],
    "note": "Customer IdP. lolcgroupdev + generic Atlassian. Tokens stay on Worker in bank mode.",
}


def pull_assigned(jql: str = "assignee = currentUser() AND resolution = Unresolved") -> dict[str, Any]:
    if not os.environ.get("ATLASSIAN_TOKEN"):
        return {"ok": False, "reason": "ATLASSIAN_TOKEN missing — ask user. Do not invent issues.", "oauth": OAUTH, "jql": jql}
    return {"ok": False, "reason": "Use Atlassian MCP on this PC; do not scrape Jira HTML.", "jql": jql}


def pull_xray_readonly(issue_key: str) -> dict[str, Any]:
    return {
        "ok": True,
        "mode": "read_only",
        "issue": issue_key,
        "law": "Never edit or delete customer existing Xray tests. Create NEW only when licensed.",
    }


def confluence_urs(page_id: str) -> dict[str, Any]:
    return {"ok": False, "reason": "Fetch via Atlassian MCP. Never invent URS.", "pageId": page_id}


def create_new_test_allowed(licensed: bool) -> dict[str, Any]:
    if not licensed:
        return {"ok": False, "reason": "Create NEW tests only when licensed."}
    return {"ok": True, "mode": "create_new_only"}
