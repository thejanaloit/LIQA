"""Sigiri / TestCrafters Xray Manual Test contract (PF-59194 gold).

LOCKED owner law (2026-09-15):
- Split the user story into path parts first.
- Write Manual steps only as Action | Data | Expected Result.
- Match Sigiri simplicity — not even a decimal of difference.
- Guard rejects any other format before Jira upload.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from paths import REPO_ROOT, WORKSPACE

CONTRACT_VERSION = "2026-09-15-sigiri-pf59194-owner-export-v2"
GOLD_ISSUE = "PF-59194"
GOLD_STORY = "PF-55248"
GOLD_CSV = REPO_ROOT / "artifacts" / "xray-gold-pf59194" / "PF-59194-steps.csv"
GOLD_OWNER_EXPORT = REPO_ROOT / "artifacts" / "xray-gold-pf59194" / "PF-59194-(2)-owner-export.csv"

STEP_COLUMNS = ("Action", "Data", "Expected Result")
# Owner export has NO Attachments column — match exactly
CSV_COLUMNS = ("Action", "Data", "Expected Result")

# Forbidden on FusionX PF Manual steps / titles
FORBIDDEN_TITLE_PATTERNS = [
    re.compile(r"^\[.+\]\[.+\]\[FP\]", re.I),
    re.compile(r"^Title:\s*\[", re.I),
    re.compile(r"\[[^\]]+\]\[[^\]]+\]\[[^\]]+\]\[FP\]", re.I),
    re.compile(r"Validate that\b", re.I),
]
FORBIDDEN_ACTION_PATTERNS = [
    re.compile(r"\bplease\b", re.I),
    re.compile(r"\bkindly\b", re.I),
    re.compile(r"\bas an AI\b", re.I),
    re.compile(r"\bverify that the system under test\b", re.I),
    re.compile(r"\bensure that\b", re.I),
]
MAX_ACTION_CHARS = 220
MAX_EXPECTED_CHARS = 220
MAX_DATA_CHARS = 120


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def laws() -> dict[str, Any]:
    return {
        "ok": True,
        "contract_version": CONTRACT_VERSION,
        "gold_issue": GOLD_ISSUE,
        "gold_story": GOLD_STORY,
        "gold_csv": str(GOLD_CSV) if GOLD_CSV.exists() else None,
        "step_columns": list(STEP_COLUMNS),
        "laws": [
            "ENGLISH lock: convert Sinhala owner doctrine to English before executing.",
            "Read the user story; split into path parts (UI journeys) before writing any step.",
            "Each Manual step MUST be exactly: Action | Data | Expected Result.",
            "Data is usually empty or None — never invent fluff.",
            "Language: short, direct, Sigiri-simple (see PF-59194).",
            "Not even a decimal difference from PF-59194 structure.",
            "PF titles use pipe taxonomy; do NOT use [Module][Sub][FP] - Validate that… on PF.",
            "Xray Test summary equals Story summary (PF-59194 shell) OR path-part pipe title.",
            "Link: Test → Story with link type Test (tests / is tested by).",
            "ADD NEW Xray only — never edit/delete existing Sigiri tests.",
            "Guard: liqa_xray_validate_steps must pass before Jira create/upload.",
            "Agency orchestrator + specialists may draft; guard still blocks non-Sigiri output.",
        ],
        "anti_patterns": [
            "Long narrative Actions",
            "Bracket FP titles on FusionX PF",
            "Missing Expected Result",
            "Conversational fillers (please/kindly)",
            "Uploading without path split",
        ],
        "example_steps": [
            {
                "Action": "Log in as a user with Receipt Reallocation access",
                "Data": "",
                "Expected Result": "User is logged in successfully",
            },
            {
                "Action": "Navigate to 'Transaction Management' > 'Receipt Reallocation'",
                "Data": "",
                "Expected Result": "The Receipt Reallocation screen is displayed with available options",
            },
        ],
    }


def _norm_data(value: Any) -> str:
    if value is None:
        return ""
    s = str(value).strip()
    if s.lower() in {"none", "n/a", "na", "-"}:
        return ""
    return s


def _norm_step(raw: dict[str, Any]) -> dict[str, str]:
    action = str(
        raw.get("Action")
        or raw.get("action")
        or raw.get("step")
        or ""
    ).strip()
    data = _norm_data(raw.get("Data") if "Data" in raw else raw.get("data"))
    expected = str(
        raw.get("Expected Result")
        or raw.get("expected_result")
        or raw.get("Expected")
        or raw.get("expected")
        or ""
    ).strip()
    return {"Action": action, "Data": data, "Expected Result": expected}


def load_gold_steps(limit: int = 0) -> dict[str, Any]:
    if not GOLD_CSV.exists():
        return {"ok": False, "error": f"gold csv missing: {GOLD_CSV}"}
    steps: list[dict[str, str]] = []
    with GOLD_CSV.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            steps.append(_norm_step(row))
            if limit and len(steps) >= limit:
                break
    # Repair CSV rows where Expected was split into next Action (Sigiri export quirk)
    repaired: list[dict[str, str]] = []
    for s in steps:
        if (
            repaired
            and not s["Expected Result"]
            and s["Action"].lower().startswith(("system displays", "validation message"))
        ):
            prev = repaired[-1]
            if not prev["Expected Result"]:
                prev["Expected Result"] = s["Action"]
            else:
                prev["Expected Result"] = f"{prev['Expected Result']}; {s['Action']}"
            continue
        if not s["Expected Result"] and s["Action"]:
            # orphan expected — treat Action as observation expected if prior action exists
            if repaired and repaired[-1]["Expected Result"]:
                s = {
                    "Action": repaired[-1]["Action"],
                    "Data": "",
                    "Expected Result": s["Action"],
                }
                repaired[-1] = s
                continue
        repaired.append(s)
    steps = [s for s in repaired if s["Action"] and s["Expected Result"]]
    return {
        "ok": True,
        "count": len(steps),
        "steps": steps,
        "path": str(GOLD_CSV),
        "contract_version": CONTRACT_VERSION,
    }


def split_story_paths(
    story_key: str,
    story_text: str,
    paths_json: str = "",
) -> dict[str, Any]:
    """Identify path parts from story text (or accept explicit JSON list)."""
    safe = "".join(c for c in story_key if c.isalnum() or c in "-_") or "STORY"
    paths: list[dict[str, Any]] = []
    if paths_json.strip():
        try:
            parsed = json.loads(paths_json)
            if isinstance(parsed, list):
                for i, item in enumerate(parsed, start=1):
                    if isinstance(item, str):
                        paths.append({"id": f"P{i:02d}", "name": item.strip(), "hint": ""})
                    elif isinstance(item, dict):
                        paths.append(
                            {
                                "id": str(item.get("id") or f"P{i:02d}"),
                                "name": str(item.get("name") or item.get("path") or f"Path {i}").strip(),
                                "hint": str(item.get("hint") or item.get("notes") or "").strip(),
                            }
                        )
        except json.JSONDecodeError as e:
            return {"ok": False, "error": f"paths_json invalid: {e}"}

    if not paths:
        text = (story_text or "").lower()
        # Heuristic path discovery for Lending receipt / common modules
        candidates = [
            ("Login / Access", ["login", "access", "permission", "privilege"]),
            ("Receipt Reallocation — Create", ["reallocation", "create new", "contract"]),
            ("Receipt Reallocation — Excess / toggles", ["excess", "toggle", "transfer all"]),
            ("Receipt Reallocation — Pending / Auth", ["pending", "approve", "reject", "return", "checker"]),
            ("Account Inquiry — Receipt Details", ["account inquiry", "receipt details", "allocation status"]),
            ("Refund / Reversal", ["refund", "reversal"]),
            ("Validation / Negative", ["validation", "mandatory", "invalid", "error"]),
            ("Audit / GL / Session", ["audit", "gl", "session", "timeout"]),
        ]
        for name, keys in candidates:
            if any(k in text for k in keys) or not story_text.strip():
                paths.append({"id": f"P{len(paths)+1:02d}", "name": name, "hint": ", ".join(keys)})
        if not paths:
            paths = [
                {"id": "P01", "name": "Happy path", "hint": "primary AC journey"},
                {"id": "P02", "name": "Negative / validation", "hint": "errors and blocks"},
                {"id": "P03", "name": "Access / roles", "hint": "RBAC maker-checker"},
            ]

    dest = WORKSPACE / "NewTestCases" / safe / "paths"
    dest.mkdir(parents=True, exist_ok=True)
    payload = {
        "story_key": safe,
        "contract_version": CONTRACT_VERSION,
        "paths": paths,
        "at": _now(),
        "rule": "Write Manual steps per path in Action|Data|Expected Result only (PF-59194).",
    }
    path = dest / "path-split.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md = dest / "path-split.md"
    lines = [
        f"# Path split — {safe}",
        "",
        f"Contract: `{CONTRACT_VERSION}`",
        "",
        "| ID | Path | Hint |",
        "|----|------|------|",
    ]
    for p in paths:
        lines.append(f"| {p['id']} | {p['name']} | {p.get('hint','')} |")
    lines.append("")
    lines.append("Next: draft Manual steps per path → `liqa_xray_validate_steps` → Jira ADD NEW only.")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"ok": True, "story_key": safe, "paths": paths, "path": str(path), "md": str(md)}


def validate_steps(steps: list[dict[str, Any]] | str, require_min: int = 1) -> dict[str, Any]:
    if isinstance(steps, str):
        try:
            steps = json.loads(steps)
        except json.JSONDecodeError as e:
            return {"ok": False, "stop_upload": True, "error": f"steps JSON invalid: {e}", "reasons": []}

    if not isinstance(steps, list):
        return {"ok": False, "stop_upload": True, "error": "steps must be a list", "reasons": []}

    reasons: list[str] = []
    normalized: list[dict[str, str]] = []
    for i, raw in enumerate(steps, start=1):
        if not isinstance(raw, dict):
            reasons.append(f"step {i}: not an object")
            continue
        s = _norm_step(raw)
        normalized.append(s)
        if not s["Action"]:
            reasons.append(f"step {i}: Action empty")
        if not s["Expected Result"]:
            reasons.append(f"step {i}: Expected Result empty")
        if len(s["Action"]) > MAX_ACTION_CHARS:
            reasons.append(f"step {i}: Action too long (>{MAX_ACTION_CHARS}) — Sigiri-simple only")
        if len(s["Expected Result"]) > MAX_EXPECTED_CHARS:
            reasons.append(f"step {i}: Expected Result too long (>{MAX_EXPECTED_CHARS})")
        if len(s["Data"]) > MAX_DATA_CHARS:
            reasons.append(f"step {i}: Data too long")
        for pat in FORBIDDEN_ACTION_PATTERNS:
            # Only Action — Expected Result may quote UI text ("Please select a contract…")
            if pat.search(s["Action"]):
                reasons.append(f"step {i}: forbidden filler language ({pat.pattern})")
        if "\n\n" in s["Action"] or "\n\n" in s["Expected Result"]:
            reasons.append(f"step {i}: multi-paragraph not allowed")

    if len(normalized) < require_min:
        reasons.append(f"need at least {require_min} step(s), got {len(normalized)}")

    ok = len(reasons) == 0
    return {
        "ok": ok,
        "stop_upload": not ok,
        "contract_version": CONTRACT_VERSION,
        "step_count": len(normalized),
        "steps": normalized,
        "reasons": reasons,
        "columns": list(STEP_COLUMNS),
        "message": "Sigiri Manual steps OK — may upload ADD NEW."
        if ok
        else "BLOCKED: fix steps to PF-59194 Action|Data|Expected Result before Jira.",
    }


def validate_title(summary: str, *, allow_qa_agent_prefix: bool = True) -> dict[str, Any]:
    s = (summary or "").strip()
    reasons: list[str] = []
    if not s:
        reasons.append("summary empty")
    for pat in FORBIDDEN_TITLE_PATTERNS:
        if pat.search(s):
            reasons.append("bracket [Module][FP] title forbidden on FusionX PF — use pipe taxonomy")
    if allow_qa_agent_prefix and s.upper().startswith("QA AGENT"):
        pass
    elif "|" not in s and "Testcase" not in s and "Validate" in s:
        reasons.append("prefer Sigiri pipe title or path-part Manual test title")
    return {
        "ok": len(reasons) == 0,
        "summary": s,
        "reasons": reasons,
        "contract_version": CONTRACT_VERSION,
    }


def build_manual_pack(
    story_key: str,
    path_id: str,
    path_name: str,
    steps_json: str,
    summary: str = "",
) -> dict[str, Any]:
    """Validate + write CSV/MD pack ready for Xray Manual Import / Atlassian create."""
    safe = "".join(c for c in story_key if c.isalnum() or c in "-_") or "STORY"
    pid = "".join(c for c in path_id if c.isalnum() or c in "-_") or "P01"
    v = validate_steps(steps_json)
    if not v.get("ok"):
        return {**v, "ok": False}

    title_check = validate_title(summary) if summary else {"ok": True, "summary": "", "reasons": []}
    if summary and not title_check.get("ok"):
        return {
            "ok": False,
            "stop_upload": True,
            "error": "summary failed Sigiri title guard",
            "reasons": title_check.get("reasons", []),
        }

    steps: list[dict[str, str]] = v["steps"]
    dest = WORKSPACE / "NewTestCases" / safe / "sigiri-manual" / pid
    dest.mkdir(parents=True, exist_ok=True)
    csv_path = dest / f"{pid}-steps.csv"
    md_path = dest / f"{pid}-steps.md"
    meta_path = dest / f"{pid}-meta.json"

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(CSV_COLUMNS))
        w.writeheader()
        for s in steps:
            w.writerow(
                {
                    "Action": s["Action"],
                    "Data": s.get("Data") or "",
                    "Expected Result": s["Expected Result"],
                }
            )

    lines = [
        f"# {pid} — {path_name}",
        "",
        f"Story: {safe}",
        f"Contract: `{CONTRACT_VERSION}`",
        f"Gold: {GOLD_ISSUE}",
        "",
        "| # | Action | Data | Expected Result |",
        "|---|--------|------|-----------------|",
    ]
    for i, s in enumerate(steps, start=1):
        data = s["Data"] or ""
        lines.append(
            f"| {i} | {s['Action']} | {data} | {s['Expected Result']} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    meta = {
        "story_key": safe,
        "path_id": pid,
        "path_name": path_name,
        "summary": summary
        or f"Lending Module | {path_name} | Testcase writing and execution",
        "step_count": len(steps),
        "csv": str(csv_path),
        "md": str(md_path),
        "contract_version": CONTRACT_VERSION,
        "upload_guard": "passed",
        "at": _now(),
        "jira_hint": [
            "Create issuetype=Test (ADD NEW only).",
            "Summary: pipe taxonomy (or equal Story summary for shell Test).",
            "Link type Test → Story (tests / is tested by).",
            "Import CSV into Xray Manual steps (Action,Data,Expected Result) — same as PF-59194.",
            "Do not put novels in Description.",
        ],
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return {"ok": True, "stop_upload": False, **meta, "steps": steps}


def gate_save_new_testcase(content: str) -> dict[str, Any]:
    """Block non-Sigiri packs when content looks like a Manual step table."""
    lower = content.lower()
    if "action" in lower and "expected" in lower:
        # extract naive rows "| n | action | data | expected |"
        rows = []
        for line in content.splitlines():
            if re.match(r"^\|\s*\d+\s*\|", line.strip()):
                parts = [p.strip() for p in line.strip().strip("|").split("|")]
                if len(parts) >= 4:
                    rows.append(
                        {
                            "Action": parts[1],
                            "Data": parts[2],
                            "Expected Result": parts[3],
                        }
                    )
        if rows:
            return validate_steps(rows)
    # Allow freeform drafts but flag if bracket FP title present
    for pat in FORBIDDEN_TITLE_PATTERNS:
        if pat.search(content):
            return {
                "ok": False,
                "stop_upload": True,
                "reasons": ["bracket FP title detected — rewrite to Sigiri pipe + Manual steps"],
                "contract_version": CONTRACT_VERSION,
            }
    return {"ok": True, "stop_upload": False, "note": "no Manual table detected — draft allowed", "contract_version": CONTRACT_VERSION}
