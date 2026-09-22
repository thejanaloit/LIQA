"""Jira bug-proof attachment RPA (headed Playwright — no API token required).

Filenames in a bug description are NOT proof. Binary PNGs MUST land in the
Jira **Attachments** panel. REST `/attachments` often fails XSRF without an
API token, so this module uses the same Chrome profile / CDP path as Xray UI
import and sets `input[type=file]` on the issue view.

=============================================================================
PROVEN METHOD (lolcgroupdev — locked 2026-09-22)
=============================================================================
1) Prefer CDP Chrome: LIQA_CHROME_CDP=http://127.0.0.1:9333
   Else Playwright profile workspace/.../.chrome-xray-ui-import
2) Login: secrets/jira-ui-login.json; never invent OTP / MFA
3) Open /browse/{BUG_KEY}
4) Prefer existing input[type=file] on the issue view (often hidden but present)
5) Else click Attach / Add attachment / meatball → Attach files
6) set_input_files(paths) — wait until REST lists the filenames
7) Skip filenames already attached (idempotent)
8) Write reports/jira-attachment-log.json + optional Activity comment text
9) Auto-hook: liqa_complete_phase(7) / liqa_learn_cycle → end_of_run_attach_proofs

Pack layout (preferred):
  outputs/<STORY>/jira-attach-pack-<BUG_KEY>/*.png

Also discovers:
  reports/proof/<STORY>/*cropped*.png when mapped via
  reports/jira-attach-manifest.json → { "PF-59783": ["path1.png", ...] }
=============================================================================
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from paths import WORKSPACE

try:
    import xray_ui_import as ui
except ImportError:  # pragma: no cover
    ui = None  # type: ignore

JIRA_SITE = "https://lolcgroupdev.atlassian.net"
CLOUD_ID = "50681345-b1f0-46ba-875b-dde9c72f71c5"
REPORT_DIR = WORKSPACE / "reports"
LOG_PATH = REPORT_DIR / "jira-attachment-log.json"
MANIFEST_PATH = REPORT_DIR / "jira-attach-manifest.json"

PROVEN_ATTACH_METHOD = {
    "id": "jira_issue_file_input_set_files",
    "version": "2026-09-22-v1",
    "file_input": "input[type=file]",
    "verify": "GET /rest/api/3/issue/{key}?fields=attachment",
    "never": [
        "filename-only lists in description as substitute for Attachments",
        "REST attach without API token when XSRF fails (use UI)",
        "closing Chrome mid-run between bugs",
    ],
    "pack_glob": "outputs/*/jira-attach-pack-<BUG_KEY>/*.png",
    "cdp_env": "LIQA_CHROME_CDP",
    "login_secret": "secrets/jira-ui-login.json",
    "hook": "liqa_complete_phase(7) + liqa_learn_cycle",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _issue_on_page(page, issue: str) -> bool:
    url = (page.url or "").lower()
    return issue.lower() in url and "id.atlassian.com" not in url


def list_attachment_names(context, issue: str) -> list[str]:
    """Read attachment filenames via session cookies (Playwright request)."""
    for base in [JIRA_SITE, f"https://api.atlassian.com/ex/jira/{CLOUD_ID}"]:
        try:
            resp = context.request.get(
                f"{base}/rest/api/3/issue/{issue}?fields=attachment",
                headers={"Accept": "application/json"},
            )
            if resp.ok:
                data = resp.json()
                return [
                    str(a.get("filename") or "")
                    for a in data.get("fields", {}).get("attachment", [])
                    if a.get("filename")
                ]
        except Exception:
            continue
    return []


def _ui_attach(page, files: list[Path], log: list[dict]) -> None:
    """Set files on the first available file input on the issue view."""
    for sel in [
        '[data-testid="issue-view-attachments.common.add-attachment"]',
        'button:has-text("Attach")',
        '[aria-label*="Attach"]',
        'button:has-text("Add attachment")',
        '[data-testid*="attachment"] button',
    ]:
        loc = page.locator(sel)
        log.append({"sel": sel, "count": loc.count()})
        if loc.count() > 0:
            try:
                loc.first.click(timeout=4000)
                page.wait_for_timeout(1000)
                log.append({"clicked": sel})
            except Exception as e:  # noqa: BLE001
                log.append({"click_err": str(e)[:120]})

    for label in ("Attach files", "Attach", "Add attachment"):
        try:
            btn = page.get_by_role("button", name=label)
            if btn.count() > 0:
                btn.first.click(timeout=3000)
                page.wait_for_timeout(700)
                log.append({"clicked_role": label})
        except Exception:
            pass

    inputs = page.locator("input[type=file]")
    log.append({"file_inputs": inputs.count()})
    if inputs.count() == 0:
        for more in (
            '[data-testid="issue-meatball-menu.ui.dropdown-trigger.button"]',
            'button[aria-label="Actions"]',
            'button[aria-label="More actions"]',
        ):
            loc = page.locator(more)
            if loc.count() > 0:
                try:
                    loc.first.click(timeout=3000)
                    page.wait_for_timeout(600)
                    log.append({"opened_more": more})
                except Exception as e:  # noqa: BLE001
                    log.append({"more_err": str(e)[:100]})
        try:
            page.get_by_text("Attach files", exact=False).first.click(timeout=3000)
            page.wait_for_timeout(700)
            log.append({"clicked_text": "Attach files"})
        except Exception as e:  # noqa: BLE001
            log.append({"attach_text_err": str(e)[:100]})
        inputs = page.locator("input[type=file]")
        log.append({"file_inputs_after": inputs.count()})

    if inputs.count() == 0:
        raise RuntimeError("no input[type=file] on issue view — cannot attach")

    paths = [str(f.resolve()) for f in files]
    inputs.first.set_input_files(paths)
    page.wait_for_timeout(12_000)
    log.append({"ui_set_files": [f.name for f in files]})

    # Nudge Attachments panel into view so the UI shows thumbnails
    for text in ("Attachments", "Attached", "attachment"):
        try:
            loc = page.get_by_text(text, exact=False)
            if loc.count() > 0:
                loc.first.scroll_into_view_if_needed(timeout=2000)
                log.append({"scrolled_to": text})
                break
        except Exception:
            pass


def discover_attach_jobs(story_key: str = "") -> list[dict[str, Any]]:
    """Find bug KEY → PNG packs under outputs/ and optional manifest."""
    jobs: list[dict[str, Any]] = []
    seen: set[str] = set()

    roots: list[Path] = []
    if story_key:
        roots = [WORKSPACE / "outputs" / story_key.upper()]
    else:
        roots = [WORKSPACE / "outputs"]

    for root in roots:
        if not root.exists():
            continue
        for pack in sorted(root.glob("**/jira-attach-pack-*")):
            if not pack.is_dir():
                continue
            m = re.search(r"jira-attach-pack-([A-Z]+-\d+)", pack.name, re.I)
            if not m:
                continue
            key = m.group(1).upper()
            files = sorted(pack.glob("*.png")) + sorted(pack.glob("*.jpg"))
            if not files:
                continue
            if key in seen:
                continue
            seen.add(key)
            jobs.append({"issue": key, "files": [str(f) for f in files], "pack": str(pack)})

    if MANIFEST_PATH.exists():
        try:
            data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        for key, paths in (data or {}).items():
            key_u = str(key).upper()
            if story_key and story_key.upper() not in key_u and story_key.upper() not in str(paths):
                # still allow explicit bug keys in manifest
                pass
            file_paths = []
            for p in paths if isinstance(paths, list) else []:
                fp = Path(p)
                if not fp.is_absolute():
                    fp = WORKSPACE / fp
                if fp.exists() and fp.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
                    file_paths.append(str(fp))
            if file_paths and key_u not in seen:
                seen.add(key_u)
                jobs.append({"issue": key_u, "files": file_paths, "pack": "manifest"})

    return jobs


def attach_files_to_issue(
    issue_key: str,
    files: list[str],
    *,
    headed: bool = True,
    skip_existing: bool = True,
) -> dict[str, Any]:
    """Attach PNG/JPG proofs to one Jira bug via headed UI RPA."""
    if ui is None:
        return {"ok": False, "error": "xray_ui_import missing — browser launch unavailable"}

    issue = (issue_key or "").strip().upper()
    paths = [Path(f) for f in files if Path(f).exists()]
    if not issue:
        return {"ok": False, "error": "issue_key required"}
    if not paths:
        return {"ok": False, "error": "no existing files to attach", "requested": files}

    from playwright.sync_api import sync_playwright

    log: list[dict] = []
    result: dict[str, Any] = {
        "ok": False,
        "issue": issue,
        "contract": PROVEN_ATTACH_METHOD["id"],
        "at": _now(),
    }

    with sync_playwright() as p:
        launched = ui._launch_browser(p, headed=headed, slow_mo_ms=40)
        context = launched["context"]
        page = launched["page"]
        try:
            page.goto(f"{JIRA_SITE}/browse/{issue}", wait_until="domcontentloaded", timeout=90_000)
            page.wait_for_timeout(2500)
            if ui._is_login_wall(page) or "id.atlassian.com" in (page.url or "").lower():
                auto = ui._auto_login_atlassian(page, wait_seconds=240)
                log.append({"login": {k: auto.get(k) for k in ("ok", "needs_mfa", "error") if k in auto}})
                deadline = time.time() + 180
                while time.time() < deadline and not _issue_on_page(page, issue):
                    page.wait_for_timeout(2000)
                page.goto(f"{JIRA_SITE}/browse/{issue}", wait_until="domcontentloaded", timeout=90_000)
                page.wait_for_timeout(2500)

            if not _issue_on_page(page, issue):
                result["error"] = "not_on_issue"
                result["url"] = page.url
                result["log"] = log
                return result

            existing = list_attachment_names(context, issue)
            result["before"] = existing
            to_upload = paths
            if skip_existing:
                have = {n.lower() for n in existing}
                to_upload = [f for f in paths if f.name.lower() not in have]
            result["skipped_existing"] = [f.name for f in paths if f not in to_upload]

            if not to_upload:
                result["ok"] = True
                result["attachments"] = existing
                result["skipped"] = True
                result["reason"] = "all filenames already attached"
                result["log"] = log
                return result

            _ui_attach(page, to_upload, log)
            names = list_attachment_names(context, issue)
            if len(names) < len(existing) + 1:
                page.reload(wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                _ui_attach(page, to_upload, log)
                page.wait_for_timeout(8000)
                names = list_attachment_names(context, issue)

            missing = [f.name for f in to_upload if f.name not in names]
            result["ok"] = len(missing) == 0
            result["attachments"] = names
            result["uploaded"] = [f.name for f in to_upload if f.name in names]
            result["missing"] = missing
            result["log"] = log
            result["comment_hint"] = (
                f"LIQA proof attachments are on {issue} — open the Attachments panel. "
                f"Files: {', '.join(result['uploaded'] or names)}"
            )
            return result
        finally:
            if launched.get("close_browser"):
                context.close()


def attach_jobs(
    jobs: list[dict[str, Any]],
    *,
    headed: bool = True,
    skip_existing: bool = True,
) -> dict[str, Any]:
    """Attach multiple bug packs in one headed Chrome session."""
    if ui is None:
        return {"ok": False, "error": "xray_ui_import missing"}
    if not jobs:
        return {
            "ok": True,
            "skipped": True,
            "reason": "no attach jobs discovered",
            "contract": PROVEN_ATTACH_METHOD["id"],
            "at": _now(),
        }

    from playwright.sync_api import sync_playwright

    log: list[dict] = []
    results: dict[str, Any] = {}

    with sync_playwright() as p:
        launched = ui._launch_browser(p, headed=headed, slow_mo_ms=40)
        context = launched["context"]
        page = launched["page"]
        try:
            for job in jobs:
                issue = str(job.get("issue") or "").upper()
                paths = [Path(f) for f in (job.get("files") or []) if Path(f).exists()]
                if not issue or not paths:
                    results[issue or "?"] = {"ok": False, "error": "empty job"}
                    continue

                page.goto(f"{JIRA_SITE}/browse/{issue}", wait_until="domcontentloaded", timeout=90_000)
                page.wait_for_timeout(2500)
                if ui._is_login_wall(page) or "id.atlassian.com" in (page.url or "").lower():
                    auto = ui._auto_login_atlassian(page, wait_seconds=240)
                    log.append({"login": {k: auto.get(k) for k in ("ok", "needs_mfa", "error") if k in auto}})
                    deadline = time.time() + 180
                    while time.time() < deadline and not _issue_on_page(page, issue):
                        page.wait_for_timeout(2000)
                    page.goto(f"{JIRA_SITE}/browse/{issue}", wait_until="domcontentloaded", timeout=90_000)
                    page.wait_for_timeout(2500)

                log.append({"issue": issue, "url": page.url})
                if not _issue_on_page(page, issue):
                    results[issue] = {"ok": False, "error": "not_on_issue", "url": page.url}
                    continue

                existing = list_attachment_names(context, issue)
                to_upload = paths
                if skip_existing:
                    have = {n.lower() for n in existing}
                    to_upload = [f for f in paths if f.name.lower() not in have]

                if not to_upload:
                    results[issue] = {
                        "ok": True,
                        "skipped": True,
                        "attachments": existing,
                        "reason": "all filenames already attached",
                    }
                    continue

                try:
                    _ui_attach(page, to_upload, log)
                except Exception as e:  # noqa: BLE001
                    results[issue] = {"ok": False, "error": str(e), "before": existing}
                    continue

                names = list_attachment_names(context, issue)
                if len([f for f in to_upload if f.name in names]) < len(to_upload):
                    page.reload(wait_until="domcontentloaded")
                    page.wait_for_timeout(2000)
                    try:
                        _ui_attach(page, to_upload, log)
                        page.wait_for_timeout(8000)
                    except Exception as e:  # noqa: BLE001
                        log.append({"retry_err": str(e)[:120]})
                    names = list_attachment_names(context, issue)

                missing = [f.name for f in to_upload if f.name not in names]
                results[issue] = {
                    "ok": len(missing) == 0,
                    "attachments": names,
                    "uploaded": [f.name for f in to_upload if f.name in names],
                    "missing": missing,
                    "expected": [f.name for f in paths],
                    "comment_hint": (
                        f"LIQA proofs on {issue} — open Attachments panel: "
                        + ", ".join(f.name for f in to_upload)
                    ),
                }
        finally:
            if launched.get("close_browser"):
                context.close()

    out = {
        "ok": all(v.get("ok") for v in results.values()) if results else True,
        "results": results,
        "log": log,
        "contract": PROVEN_ATTACH_METHOD["id"],
        "hook": "manual_or_end_of_run",
        "at": _now(),
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def end_of_run_attach_proofs(
    story_key: str = "",
    *,
    headed: bool = True,
    skip_if_none: bool = True,
    skip_existing: bool = True,
) -> dict[str, Any]:
    """Mandatory end-of-run: attach all discovered bug-proof packs.

    Called automatically from liqa_complete_phase(7) and liqa_learn_cycle.
    """
    jobs = discover_attach_jobs(story_key=story_key)
    if not jobs:
        out = {
            "ok": True if skip_if_none else False,
            "skipped": True,
            "reason": "no jira-attach-pack-* or manifest entries",
            "contract": PROVEN_ATTACH_METHOD["id"],
            "hint": "Put PNGs in outputs/<STORY>/jira-attach-pack-<BUG_KEY>/ before phase 7",
            "at": _now(),
        }
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        (REPORT_DIR / "jira-attach-end-of-run-last.json").write_text(
            json.dumps(out, indent=2), encoding="utf-8"
        )
        return out

    result = attach_jobs(jobs, headed=headed, skip_existing=skip_existing)
    result["hook"] = "end_of_run"
    result["jobs_discovered"] = len(jobs)
    (REPORT_DIR / "jira-attach-end-of-run-last.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result


def proven_method() -> dict[str, Any]:
    return {"ok": True, **PROVEN_ATTACH_METHOD}
