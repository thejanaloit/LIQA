#!/usr/bin/env python3
"""End-of-run RPA: upload every Sigiri Manual-step CSV into Jira Xray via headed Chrome.

No Xray API keys required. Proven method: Import → From csv... → #xray-csv-file
→ map Action*/Data/Expected Result → Validate → Import Steps (see README-xray-ui-rpa.md).

Uses CDP (LIQA_CHROME_CDP) or persistent profile:
  workspace/default-run/.chrome-xray-ui-import

Usage:
  py -3 scripts/xray_ui_upload_end_of_run.py login
  py -3 scripts/xray_ui_upload_end_of_run.py upload
  py -3 scripts/xray_ui_upload_end_of_run.py upload --registry path/to/jira-created.json
  py -3 scripts/xray_ui_upload_end_of_run.py pack P01 PF-59477
  py -3 scripts/xray_ui_upload_end_of_run.py pack P01 PF-59477 --force-reset
  py -3 scripts/xray_ui_upload_end_of_run.py csv PF-59477 path/to/steps.csv --force-reset
  py -3 scripts/xray_ui_upload_end_of_run.py method
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MCP = ROOT / "mcp"
if str(MCP) not in sys.path:
    sys.path.insert(0, str(MCP))

import xray_ui_import as ui  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="LIQA Xray UI RPA end-of-run uploader")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("method", help="Print locked PROVEN_UI_METHOD contract")

    p_login = sub.add_parser("login", help="One-time Jira login in persistent Chrome")
    p_login.add_argument("--wait", type=int, default=600)
    p_login.add_argument("--probe", default="PF-59477")

    p_up = sub.add_parser("upload", help="Upload all packs from jira-created.json")
    p_up.add_argument("--registry", default="")
    p_up.add_argument("--headless", action="store_true")
    p_up.add_argument(
        "--force-reset",
        action="store_true",
        help="Reset Current Test Steps before import",
    )

    p_pack = sub.add_parser("pack", help="Upload one pack")
    p_pack.add_argument("pack_id")
    p_pack.add_argument("issue_key")
    p_pack.add_argument("--story", default="PF-58380")
    p_pack.add_argument("--force-reset", action="store_true")

    p_one = sub.add_parser("csv", help="Upload one CSV into an issue")
    p_one.add_argument("issue_key")
    p_one.add_argument("csv_path")
    p_one.add_argument("--force-reset", action="store_true")

    args = ap.parse_args()
    if args.cmd == "method":
        r = ui.proven_method()
    elif args.cmd == "login":
        r = ui.ensure_jira_login(wait_seconds=args.wait, probe_issue=args.probe)
    elif args.cmd == "upload":
        r = ui.end_of_run_upload_registry(
            args.registry,
            headed=not args.headless,
            force_reset=bool(args.force_reset),
        )
    elif args.cmd == "pack":
        r = ui.import_pack_ui(
            args.story,
            args.pack_id,
            args.issue_key,
            headed=True,
            force_reset=bool(args.force_reset),
        )
    else:
        r = ui.import_issue_ui(
            args.issue_key,
            args.csv_path,
            headed=True,
            force_reset=bool(args.force_reset),
        )

    print(json.dumps(r, indent=2))
    if r.get("needs_login"):
        print(
            "\n>>> Log in in the Chrome window that opened, then re-run the same command.",
            file=sys.stderr,
        )
        return 2
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
