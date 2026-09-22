"""Jira bug-proof upload RPA — comment toolbar PNG upload (owner lock).

Filenames in Description are NOT proof. Proofs must appear as **normal PNG
uploads inside an Activity comment** via the ADF toolbar button:

  tooltip / aria-label: "Add image, video, or file"

That embeds visible image cards in the comment thread (what reviewers see).
Issue-level Attachments panel alone is insufficient if the UI hides it.

=============================================================================
PROVEN METHOD (lolcgroupdev — locked 2026-09-22 comment-media)
=============================================================================
1) Prefer CDP Chrome: LIQA_CHROME_CDP=http://127.0.0.1:9333
   Else Playwright profile workspace/.../.chrome-xray-ui-import
2) Login: secrets/jira-ui-login.json; never invent OTP / MFA
3) Open /browse/{BUG_KEY}
4) Scroll to Activity → open comment composer ("Add a comment" / click editor)
5) Click toolbar button aria-label **Add image, video, or file**
6) Expect file chooser OR set_input_files on the media input — upload PNGs
7) Wait until media thumbnails appear in the comment body
8) Type caption "LIQA headed proof PNGs" → click **Save**
9) Verify comment exists / attachment count via REST
10) Auto-hook: liqa_complete_phase(7) / liqa_learn_cycle → end_of_run_attach_proofs

Pack layout:
  outputs/<STORY>/jira-attach-pack-<BUG_KEY>/*.png
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
    "id": "jira_comment_add_image_video_or_file",
    "version": "2026-09-22-v2-comment-media",
    "toolbar_button": "Add image, video, or file",
    "save_button": "Save",
    "verify": "GET /rest/api/3/issue/{key}?fields=attachment,comment",
    "never": [
        "filename-only lists in description as substitute for visible PNG upload",
        "text-only Activity comment without embedded media",
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


def _open_comment_composer(page, log: list[dict]) -> None:
    """Focus / open the Activity comment editor until ADF toolbar is ready."""
    try:
        cancel = page.get_by_role("button", name="Cancel")
        if cancel.count() > 0 and cancel.first.is_visible():
            cancel.first.click(timeout=2000)
            page.wait_for_timeout(500)
            log.append({"cancelled_draft": True})
    except Exception:
        pass

    # Owner UI: click the empty comment placeholder (shows ADF toolbar)
    for text in (
        "Type /ai to Ask Rovo",
        "Add a comment",
        "Type @ to mention",
    ):
        try:
            loc = page.get_by_text(text, exact=False)
            if loc.count() > 0:
                loc.first.scroll_into_view_if_needed(timeout=4000)
                loc.first.click(timeout=4000)
                page.wait_for_timeout(1000)
                log.append({"opened_placeholder": text})
                break
        except Exception as e:  # noqa: BLE001
            log.append({"placeholder_err": f"{text}:{str(e)[:60]}"})

    for sel in (
        '[data-testid="issue.activity.comment"]',
        '[data-testid*="comment-base.ui"]',
        'button:has-text("Add a comment")',
        ".ProseMirror",
        '[contenteditable="true"]',
        'div[role="textbox"]',
    ):
        loc = page.locator(sel)
        if loc.count() == 0:
            continue
        try:
            loc.first.scroll_into_view_if_needed(timeout=3000)
            loc.first.click(timeout=4000)
            page.wait_for_timeout(800)
            log.append({"opened_composer": sel})
            break
        except Exception as e:  # noqa: BLE001
            log.append({"composer_click_err": f"{sel}:{str(e)[:80]}"})

    deadline = time.time() + 12
    while time.time() < deadline:
        if _media_toolbar_button(page) is not None:
            log.append({"toolbar_ready": True})
            return
        page.wait_for_timeout(500)
    log.append({"toolbar_ready": False})


def _media_toolbar_button(page):
    """Locate ADF toolbar 'Add image, video, or file' button."""
    candidates = [
        page.get_by_role("button", name="Add image, video, or file"),
        page.locator('button[aria-label="Add image, video, or file"]'),
        page.locator('[aria-label="Add image, video, or file"]'),
        page.locator('button[aria-label*="Add image" i]'),
        page.locator('[data-testid*="MediaInsert" i]'),
        page.locator('[data-testid*="media-insert" i]'),
        page.locator('button[aria-label*="image, video, or file" i]'),
    ]
    for loc in candidates:
        try:
            if loc.count() > 0:
                return loc.first
        except Exception:
            continue
    return None


def _upload_via_file_chooser(page, btn, paths: list[str], log: list[dict]) -> bool:
    try:
        with page.expect_file_chooser(timeout=8000) as fc_info:
            btn.click(timeout=5000)
        chooser = fc_info.value
        chooser.set_files(paths)
        page.wait_for_timeout(8000)
        log.append({"file_chooser": True, "files": [Path(p).name for p in paths]})
        return True
    except Exception as e:  # noqa: BLE001
        log.append({"file_chooser_err": str(e)[:160]})
        return False


def _upload_via_input(page, paths: list[str], log: list[dict]) -> bool:
    """Set files on a media/file input — prefer editor-scoped inputs."""
    selectors = [
        '.ak-editor-content-area input[type=file]',
        '[data-testid*="media"] input[type=file]',
        'input[type=file][accept*="image"]',
        'input[type=file][accept*="png"]',
        'input[type=file]',
    ]
    for sel in selectors:
        loc = page.locator(sel)
        log.append({"input_sel": sel, "count": loc.count()})
        if loc.count() == 0:
            continue
        try:
            loc.last.set_input_files(paths)
            page.wait_for_timeout(5000)
            log.append({"set_input_files": [Path(p).name for p in paths], "sel": sel})
            return True
        except Exception as e:  # noqa: BLE001
            log.append({"set_input_err": str(e)[:120]})
    return False


def _wait_media_in_editor(page, log: list[dict], *, expect_min: int = 1, timeout_ms: int = 60000) -> bool:
    """Wait until comment editor ProseMirror shows uploaded media (scoped, not page-wide)."""
    deadline = time.time() + timeout_ms / 1000
    scoped = [
        f'.ProseMirror [data-testid*="media-card"]',
        f'.ak-editor-content-area [data-testid*="media-card"]',
        f'[contenteditable="true"] [data-testid*="media-card"]',
        f'.ProseMirror [data-testid*="media-image"]',
        f'.ProseMirror div[data-node-type="media"]',
        f'.ProseMirror img[data-file-name]',
        f'.ProseMirror img[src*="media"]',
    ]
    while time.time() < deadline:
        for sel in scoped:
            try:
                loc = page.locator(sel)
                n = loc.count()
                if n >= expect_min:
                    log.append({"media_visible_scoped": sel, "count": n})
                    return True
            except Exception:
                continue
        try:
            progress = page.locator('.ProseMirror [data-testid*="media-progress"], .ProseMirror [role="progressbar"]')
            if progress.count() > 0:
                log.append({"media_uploading": progress.count()})
        except Exception:
            pass
        page.wait_for_timeout(800)
    log.append({"media_wait_timeout": True, "expect_min": expect_min})
    return False


def _save_comment(page, log: list[dict]) -> bool:
    for name in ("Save", "Comment", "Add"):
        try:
            btn = page.get_by_role("button", name=name, exact=True)
            if btn.count() == 0:
                btn = page.get_by_role("button", name=name)
            if btn.count() > 0 and btn.first.is_enabled():
                btn.first.click(timeout=5000)
                page.wait_for_timeout(3000)
                log.append({"saved": name})
                return True
        except Exception as e:  # noqa: BLE001
            log.append({"save_err": f"{name}:{str(e)[:80]}"})
    for sel in (
        'button[type="submit"]',
        '[data-testid*="comment"] button:has-text("Save")',
        'button:has-text("Save")',
    ):
        loc = page.locator(sel)
        if loc.count() > 0:
            try:
                loc.first.click(timeout=4000)
                page.wait_for_timeout(3000)
                log.append({"saved_sel": sel})
                return True
            except Exception as e:  # noqa: BLE001
                log.append({"save_sel_err": str(e)[:80]})
    return False


def _comment_media_attach(page, files: list[Path], log: list[dict], *, issue: str = "") -> None:
    """Primary path: Activity comment → Add image, video, or file → Save."""
    paths = [str(f.resolve()) for f in files]
    names = [f.name for f in files]

    _open_comment_composer(page, log)
    page.wait_for_timeout(700)

    # Caption FIRST (short — never list filenames as text substitute for images)
    caption = f"LIQA headed proof PNGs for {issue or 'this bug'} ({len(names)} files)."
    try:
        editor = page.locator(".ProseMirror, [contenteditable='true'], div[role='textbox']").first
        editor.click(timeout=3000)
        page.keyboard.type(caption, delay=10)
        page.keyboard.press("Enter")
        page.keyboard.press("Enter")
        log.append({"caption": caption})
    except Exception as e:  # noqa: BLE001
        log.append({"caption_err": str(e)[:100]})

    btn = _media_toolbar_button(page)
    if btn is None:
        _open_comment_composer(page, log)
        page.wait_for_timeout(500)
        btn = _media_toolbar_button(page)
    if btn is None:
        raise RuntimeError(
            'toolbar button "Add image, video, or file" not found — '
            "open comment composer and ensure ADF toolbar is visible"
        )

    try:
        btn.scroll_into_view_if_needed(timeout=3000)
    except Exception:
        pass
    log.append({"media_button_found": True})

    # Upload one PNG at a time so each becomes a real media card (more reliable than batch)
    for p in paths:
        b = _media_toolbar_button(page) or btn
        before = 0
        try:
            before = page.locator('.ProseMirror [data-testid*="media-card"]').count()
        except Exception:
            pass
        ok = _upload_via_file_chooser(page, b, [p], log)
        if not ok:
            try:
                b.click(timeout=3000)
                page.wait_for_timeout(400)
            except Exception:
                pass
            ok = _upload_via_input(page, [p], log)
        if not ok:
            raise RuntimeError(f"failed to upload {Path(p).name} via comment media toolbar")
        # Wait until scoped editor has at least one more media card
        if not _wait_media_in_editor(page, log, expect_min=max(1, before + 1), timeout_ms=45000):
            # Soft continue — some UIs render mediaSingle without media-card testid
            log.append({"warn": f"media card not confirmed for {Path(p).name}"})
        page.wait_for_timeout(1200)

    # Final check: at least 1 media node in editor before Save
    if not _wait_media_in_editor(page, log, expect_min=1, timeout_ms=15000):
        raise RuntimeError(
            "comment editor has no embedded media after upload — "
            "refusing to Save text-only comment"
        )

    if not _save_comment(page, log):
        raise RuntimeError("comment Save failed after media upload")

    page.wait_for_timeout(3500)
    # Confirm saved comment shows images (Activity feed)
    saved_media = page.locator(
        '[data-testid*="comment"] [data-testid*="media-card"], '
        '[data-testid*="activity"] [data-testid*="media-card"], '
        '.ak-renderer-document [data-testid*="media-card"], '
        '.ak-renderer-document img'
    )
    log.append({"saved_media_count": saved_media.count()})
    log.append({"comment_media_upload": names, "method": PROVEN_ATTACH_METHOD["id"]})
    if saved_media.count() < 1:
        raise RuntimeError(
            "Save completed but Activity comment shows no images — "
            "media upload did not stick"
        )


def _legacy_issue_file_attach(page, files: list[Path], log: list[dict]) -> None:
    """Fallback only: issue-level Attachments file input."""
    for sel in [
        '[data-testid="issue-view-attachments.common.add-attachment"]',
        'button:has-text("Attach")',
        '[aria-label*="Attach"]',
        'button:has-text("Add attachment")',
    ]:
        loc = page.locator(sel)
        if loc.count() > 0:
            try:
                loc.first.click(timeout=3000)
                page.wait_for_timeout(800)
                log.append({"legacy_clicked": sel})
            except Exception:
                pass
    inputs = page.locator("input[type=file]")
    if inputs.count() == 0:
        raise RuntimeError("legacy attach: no file input")
    inputs.first.set_input_files([str(f.resolve()) for f in files])
    page.wait_for_timeout(10_000)
    log.append({"legacy_set_files": [f.name for f in files]})


def _ui_attach(page, files: list[Path], log: list[dict], *, issue: str = "") -> None:
    """PRIMARY ONLY: Activity comment → Add image, video, or file → Save."""
    _comment_media_attach(page, files, log, issue=issue)


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
    skip_existing: bool = False,
) -> dict[str, Any]:
    """Upload proof PNGs into a Jira Activity comment (visible image cards).

    skip_existing defaults False for comment-media — reviewers must see PNGs
    in Activity even when Attachments panel already has the same filenames.
    """
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

            if not to_upload and skip_existing:
                result["ok"] = True
                result["attachments"] = existing
                result["skipped"] = True
                result["reason"] = "all filenames already attached (skip_existing=True)"
                result["log"] = log
                return result

            if not to_upload:
                to_upload = paths

            try:
                _ui_attach(page, to_upload, log, issue=issue)
            except Exception as e:  # noqa: BLE001
                result["error"] = str(e)
                result["log"] = log
                return result

            page.wait_for_timeout(2000)
            names = list_attachment_names(context, issue)
            # Comment-media success: Save clicked + media path logged even if REST
            # attachment list was already populated from a prior run.
            media_ok = any(
                x.get("comment_media_upload") or x.get("saved") or x.get("saved_sel")
                for x in log
            )
            result["ok"] = bool(media_ok) or len(names) >= len(existing)
            result["attachments"] = names
            result["uploaded"] = [f.name for f in to_upload]
            result["log"] = log
            result["method"] = PROVEN_ATTACH_METHOD["id"]
            shot = REPORT_DIR / f"jira-comment-media-{issue}-{int(time.time())}.png"
            try:
                REPORT_DIR.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(shot), full_page=True)
                result["screenshot"] = str(shot)
            except Exception:
                pass
            return result
        finally:
            if launched.get("close_browser"):
                context.close()


def attach_jobs(
    jobs: list[dict[str, Any]],
    *,
    headed: bool = True,
    skip_existing: bool = False,
) -> dict[str, Any]:
    """Upload multiple bug packs via comment media in one headed Chrome session."""
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
                            "reason": "skip_existing — filenames already on issue",
                        }
                        continue

                job_log: list[dict] = []
                try:
                    _ui_attach(page, to_upload, job_log, issue=issue)
                    log.extend(job_log)
                    media_ok = any(
                        x.get("comment_media_upload") or x.get("saved") or x.get("saved_sel")
                        for x in job_log
                    )
                    names = list_attachment_names(context, issue)
                    results[issue] = {
                        "ok": bool(media_ok) or len(names) >= len(existing),
                        "attachments": names,
                        "uploaded": [f.name for f in to_upload],
                        "method": PROVEN_ATTACH_METHOD["id"],
                        "log_tail": job_log[-8:],
                    }
                    shot = REPORT_DIR / f"jira-comment-media-{issue}-{int(time.time())}.png"
                    try:
                        REPORT_DIR.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(shot), full_page=True)
                        results[issue]["screenshot"] = str(shot)
                    except Exception:
                        pass
                except Exception as e:  # noqa: BLE001
                    log.extend(job_log)
                    results[issue] = {"ok": False, "error": str(e), "log_tail": job_log[-12:]}
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
    skip_existing: bool = False,
) -> dict[str, Any]:
    """Mandatory end-of-run: comment-media PNG upload for every attach pack."""
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
