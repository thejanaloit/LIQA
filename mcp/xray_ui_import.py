"""Xray Manual-step UI RPA importer (no Xray API keys required).

Uses headed Playwright + persistent Chrome profile / CDP so the user stays logged
into Jira. At end of every Sigiri pack run, call:

  liqa_xray_ui_import_csv / liqa_xray_ui_import_pack / liqa_xray_ui_import_registry
  liqa_xray_end_of_run_upload  (auto on phase 7 / learn_cycle)

=============================================================================
PROVEN METHOD (lolcgroupdev Xray Cloud 16.x — locked 2026-09-15)
=============================================================================
Never use Jira issue Attachments file inputs. Never treat pre-existing aio
steps as success before clicking Import Steps.

1) Prefer CDP Chrome: LIQA_CHROME_CDP=http://127.0.0.1:9333
   (scripts/start-xray-chrome-cdp.ps1). Else Playwright profile
   workspace/.../.chrome-xray-ui-import
2) Login: secrets/jira-ui-login.json {email,password} auto-fill;
   never invent OTP / MFA — wait for human if needed.
3) Open /browse/{KEY} → scroll → Xray all-in-one iframe → Test details
4) Empty state: button Import. Filled state: icon menu right of Add Step.
5) Click leaf menuitem text exactly "From csv..." (role=menuitem)
6) Wait for dialog iframe src containing manual-steps-import
7) Set files on #xray-csv-file (name=csvFile, accept=.csv) ONLY
8) Optional replace: click visible label "Reset Current Test Steps"
   (input[name=Clear Steps] is often invisible to Playwright — click label)
9) Next → Map Fields react-selects → Action* / Data / Expected Result
   (options include Call Test — never map those for Manual CSVs)
10) Validate (must say no problems) → click Import Steps → wait until
    manual-steps-import iframe is GONE → then verify Expected Result in aio
11) Do NOT press Escape while the import dialog is open (closes whole dialog)

CSV columns: Action,Data,Expected Result (Sigiri PF-59194 gold).
=============================================================================
"""
from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from paths import REPO_ROOT, WORKSPACE

try:
    import sigiri_xray_contract as sigiri
except ImportError:  # pragma: no cover
    sigiri = None  # type: ignore

JIRA_SITE = "https://lolcgroupdev.atlassian.net"
PROFILE_DIR = WORKSPACE / ".chrome-xray-ui-import"
REPORT_DIR = WORKSPACE / "reports" / "xray-ui-import"

# Machine-readable contract for agents / MCP tools
PROVEN_UI_METHOD = {
    "id": "xray_csv_wizard_action_star",
    "version": "2026-09-15-v1",
    "gold_test": "PF-59194",
    "csv_columns": ["Action", "Data", "Expected Result"],
    "file_input": "#xray-csv-file",
    "dialog_url_substr": "manual-steps-import",
    "menu_item": "From csv...",
    "step_field_map": ["Action*", "Data", "Expected Result"],
    "never": [
        "Jira Attachments input[type=file]",
        "Escape while import dialog open",
        "success before Import Steps click + dialog close",
        "map Call Test for Manual packs",
    ],
    "reset_label": "Reset Current Test Steps",
    "reset_input_name": "Clear Steps",
    "cdp_env": "LIQA_CHROME_CDP",
    "login_secret": "secrets/jira-ui-login.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_steps(csv_path: str | Path) -> dict[str, Any]:
    path = Path(csv_path)
    if not path.exists():
        alt = WORKSPACE / str(csv_path)
        path = alt if alt.exists() else path
    if not path.exists():
        return {"ok": False, "error": f"CSV not found: {csv_path}"}
    steps: list[dict[str, str]] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            steps.append(
                {
                    "Action": (row.get("Action") or "").strip(),
                    "Data": (row.get("Data") or "").strip(),
                    "Expected Result": (
                        row.get("Expected Result") or row.get("Result") or ""
                    ).strip(),
                }
            )
    steps = [s for s in steps if s["Action"] and s["Expected Result"]]
    if sigiri is not None:
        gate = sigiri.validate_steps(steps)
        if not gate.get("ok"):
            return {"ok": False, "blocked": True, "error": "Sigiri guard failed", "reasons": gate.get("reasons")}
        steps = gate["steps"]
    return {"ok": True, "path": str(path.resolve()), "steps": steps, "count": len(steps)}


def _browse_url(issue_key: str) -> str:
    return f"{JIRA_SITE}/browse/{issue_key.strip().upper()}"


def _is_login_wall(page) -> bool:
    url = (page.url or "").lower()
    if "id.atlassian.com" in url or "auth.atlassian.com" in url:
        return True
    if "login" in url and "atlassian" in url:
        return True
    try:
        if page.get_by_text("Log in to continue", exact=False).count() > 0:
            return True
        if page.get_by_text("Log in with", exact=False).count() > 0:
            return True
        if page.locator("input[type='password']").count() > 0 and "browse" not in url:
            return True
    except Exception:
        pass
    return False


def _looks_like_jira_issue(page, issue_key: str = "") -> bool:
    """True only when a real browse page is usable (avoids blank false-positive)."""
    url = (page.url or "").lower()
    if "id.atlassian.com" in url or "auth.atlassian.com" in url:
        return False
    if "/browse/" not in url:
        return False
    if _is_login_wall(page):
        return False
    try:
        body = page.locator("body").inner_text(timeout=3000) or ""
    except Exception:
        body = ""
    if len(body.strip()) < 80:
        return False
    key = (issue_key or "").upper()
    # Prefer hard key match — blank SPA shells must not pass
    if key:
        return key in body.upper()
    markers = ("Manual", "Add Step", "Description", "Activity")
    return any(m.lower() in body.lower() for m in markers)


def _launch_browser(playwright, *, headed: bool = True, slow_mo_ms: int = 50):
    """Prefer CDP attach to owner Chrome; else persistent Playwright profile."""
    import os

    cdp = (os.environ.get("LIQA_CHROME_CDP") or "").strip()
    if cdp:
        browser = playwright.chromium.connect_over_cdp(cdp)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        return {"mode": "cdp", "browser": browser, "context": context, "page": page, "close_browser": False}

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        channel="chrome",
        headless=not headed,
        slow_mo=slow_mo_ms,
        args=["--disable-blink-features=AutomationControlled"],
        viewport={"width": 1400, "height": 900},
    )
    page = context.pages[0] if context.pages else context.new_page()
    return {"mode": "persistent", "browser": None, "context": context, "page": page, "close_browser": True}


def _collect_frames(page) -> list:
    frames = [page.main_frame] + list(page.frames)
    # unique by name/url
    seen = set()
    out = []
    for fr in frames:
        key = (fr.name, fr.url)
        if key in seen:
            continue
        seen.add(key)
        out.append(fr)
    return out


def _frame_has_text(frame, text: str) -> bool:
    try:
        return frame.get_by_text(text, exact=False).count() > 0
    except Exception:
        return False


def _find_xray_frame(page):
    # Prefer the Xray all-in-one webpanel iframe (Manual steps live here)
    deadline = time.time() + 25
    while time.time() < deadline:
        for fr in _collect_frames(page):
            u = (fr.url or "").lower()
            if "all-in-one" in u or "manual-steps" in u or "test/test" in u:
                return fr
            try:
                if _frame_has_text(fr, "Add Step") or _frame_has_text(fr, "Import"):
                    if "xray" in u or "getxray" in u or "all-in-one" in u:
                        return fr
            except Exception:
                continue
        page.wait_for_timeout(500)
    for fr in _collect_frames(page):
        u = (fr.url or "").lower()
        if "xray" in u or "xpandit" in u or "getxray" in u:
            return fr
    return page.main_frame


def _click_text(frame, labels: list[str], timeout: int = 4000) -> bool:
    for label in labels:
        try:
            loc = frame.get_by_role("button", name=label)
            if loc.count() > 0:
                loc.first.click(timeout=timeout)
                return True
        except Exception:
            pass
        try:
            loc = frame.get_by_text(label, exact=True)
            if loc.count() > 0:
                loc.first.click(timeout=timeout)
                return True
        except Exception:
            pass
        try:
            loc = frame.locator(f"button:has-text('{label}'), a:has-text('{label}'), [role='button']:has-text('{label}')")
            if loc.count() > 0:
                loc.first.click(timeout=timeout)
                return True
        except Exception:
            pass
    return False


def _load_jira_ui_creds() -> dict[str, str] | None:
    """Load gitignored Jira UI password (never log the secret)."""
    candidates = [
        WORKSPACE / "secrets" / "jira-ui-login.json",
        REPO_ROOT / "secrets" / "jira-ui-login.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            email = (data.get("email") or "").strip()
            password = data.get("password") or ""
            if email and password:
                return {"email": email, "password": password, "path": str(path)}
        except Exception:
            continue
    return None


def _mfa_blocking(page) -> bool:
    try:
        texts = [
            "Enter the code",
            "Authentication code",
            "Verify your identity",
            "two-step",
            "2-step",
            "One-time",
            "Authenticator",
        ]
        body = (page.locator("body").inner_text(timeout=2000) or "").lower()
        return any(t.lower() in body for t in texts)
    except Exception:
        return False


def _auto_login_atlassian(page, *, wait_seconds: int = 120) -> dict[str, Any]:
    """Fill Atlassian login from secrets/jira-ui-login.json. Never invents OTP."""
    creds = _load_jira_ui_creds()
    if not creds:
        return {"ok": False, "error": "no secrets/jira-ui-login.json"}
    out: dict[str, Any] = {"ok": False, "email": creds["email"], "used_secret": True}
    try:
        # Email / username
        for sel in [
            "input[type='email']",
            "input#username",
            "input[name='username']",
            "input[autocomplete='username']",
        ]:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.fill(creds["email"])
                break
        # Continue
        _click_text(page.main_frame, ["Continue", "Next"], timeout=3000)
        page.wait_for_timeout(1500)
        # Password
        for sel in [
            "input[type='password']",
            "input#password",
            "input[name='password']",
        ]:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.fill(creds["password"])
                break
        _click_text(page.main_frame, ["Log in", "Log In", "Sign in", "Continue"], timeout=4000)
        page.wait_for_timeout(2500)
        if _mfa_blocking(page):
            out["needs_mfa"] = True
            out["error"] = "MFA/OTP required — enter code yourself in the Chrome window (agent will not invent OTP)"
            deadline = time.time() + max(60, wait_seconds)
            while time.time() < deadline:
                page.wait_for_timeout(2000)
                if not _mfa_blocking(page) and not _is_login_wall(page):
                    out["ok"] = True
                    out["mfa_completed_by_human"] = True
                    return out
            return out
        if not _is_login_wall(page):
            out["ok"] = True
        else:
            out["error"] = "login wall still present after password submit"
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)
    return out


def _open_test_details(page, frame) -> None:
    for fr in (frame, page.main_frame):
        for label in ("Test details", "Test Details", "Manual Test Steps", "Manual"):
            try:
                loc = fr.get_by_role("tab", name=label)
                if loc.count() > 0:
                    loc.first.click(timeout=3000)
                    page.wait_for_timeout(1000)
                    return
            except Exception:
                pass
            try:
                loc = fr.get_by_text(label, exact=False)
                if loc.count() > 0:
                    loc.first.click(timeout=3000)
                    page.wait_for_timeout(1000)
                    return
            except Exception:
                pass


def _attachment_toast(page) -> bool:
    try:
        t = (page.locator("body").inner_text(timeout=1500) or "").lower()
        return "added attachment" in t
    except Exception:
        return False


def _count_manual_steps_visible(frame) -> int:
    try:
        # rows often have Action cells / step numbers
        n = frame.locator("[data-testid*='step'], .steps-table tr, table tr").count()
        return int(n)
    except Exception:
        return 0


def _xray_aio_frame(page):
    deadline = time.time() + 30
    while time.time() < deadline:
        for fr in page.frames:
            if "all-in-one" in (fr.url or ""):
                return fr
        page.wait_for_timeout(500)
    return None


def _open_import_menu(frame, page) -> bool:
    """Open Import menu: empty-state visible Import button, else icon next to Add Step."""
    try:
        body = frame.locator("body").inner_text(timeout=4000) or ""
    except Exception:
        body = ""
    try:
        if "There are no steps defined" in body or "Create or import test steps" in body:
            try:
                frame.get_by_role("button", name="Import").first.click(timeout=4000)
            except Exception:
                frame.get_by_text("Import", exact=True).first.click(timeout=4000)
            page.wait_for_timeout(700)
            return True
        add = frame.get_by_role("button", name="Add Step")
        box = add.bounding_box()
        if not box:
            # last resort: visible Import
            frame.get_by_text("Import", exact=True).first.click(timeout=3000)
            page.wait_for_timeout(700)
            return True
        icons = frame.locator("button")
        for i in range(icons.count()):
            bb = icons.nth(i).bounding_box()
            if not bb:
                continue
            if abs(bb["y"] - box["y"]) < 10 and bb["x"] > box["x"] + 8 and bb["width"] <= 50:
                icons.nth(i).click(timeout=3000)
                page.wait_for_timeout(700)
                return True
        frame.get_by_text("Import", exact=True).first.click(timeout=3000)
        page.wait_for_timeout(700)
        return True
    except Exception:
        return False


def _click_from_csv(frame, page) -> bool:
    """Click leaf 'From csv...' menuitem (not a parent that swallows all labels)."""
    try:
        hit = frame.evaluate(
            """() => {
              for (const el of document.querySelectorAll('*')) {
                const own = Array.from(el.childNodes)
                  .filter(n => n.nodeType === 3)
                  .map(n => (n.textContent || '').trim())
                  .filter(Boolean)
                  .join(' ');
                if (/^From csv/i.test(own)) {
                  (el.closest('[role=menuitem]') || el).click();
                  return true;
                }
              }
              return false;
            }"""
        )
        if hit:
            return True
    except Exception:
        pass
    for lab in ("From csv...", "From csv", "From CSV...", "From CSV"):
        for root in (frame, page):
            try:
                root.get_by_text(lab, exact=False).first.click(timeout=2500)
                return True
            except Exception:
                continue
    return False


def _wait_frame(page, needle: str, timeout_ms: int = 30000):
    deadline = time.time() + (timeout_ms / 1000.0)
    while time.time() < deadline:
        for fr in page.frames:
            if needle in (fr.url or ""):
                return fr
        page.wait_for_timeout(300)
    return None


def _close_react_select_menu(imp) -> None:
    """Blur/close react-select without Escape (Esc closes the whole AUI dialog)."""
    try:
        imp.evaluate(
            """() => {
              const a = document.activeElement;
              if (a && a.blur) a.blur();
              document.body.click();
            }"""
        )
    except Exception:
        pass
    time.sleep(0.15)


def _map_step_fields(imp) -> dict[str, Any]:
    """Map CSV columns → Action* / Data / Expected Result via react-select options."""
    ids = imp.evaluate(
        """() => Array.from(document.querySelectorAll('input[id^=react-select-][id$=-input]'))
          .map(e => e.id)"""
    )
    if not ids or len(ids) < 3:
        ids = ["react-select-2-input", "react-select-3-input", "react-select-4-input"]
    targets = ["Action", "Data", "Expected Result"]
    mapped: list[str] = []
    for i, wanted in enumerate(targets):
        _close_react_select_menu(imp)
        imp.evaluate(
            """(id) => {
              const input = document.getElementById(id);
              if (!input) return false;
              const control = input.closest('[class*=control]');
              const indicator = control && control.querySelector('[class*=indicatorContainer]');
              (indicator || control || input).dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
              (indicator || control || input).click();
              return true;
            }""",
            ids[i],
        )
        time.sleep(0.45)
        opts = imp.evaluate(
            """() => Array.from(document.querySelectorAll('[id*=-option-]'))
              .map(e => ({id: e.id, t: (e.textContent || '').trim()}))
              .filter(o => o.t)"""
        )
        candidates = [wanted, wanted + "*", wanted.rstrip("*")]
        chosen = None
        for cand in candidates:
            for o in opts or []:
                if o.get("t") == cand:
                    chosen = o
                    break
            if chosen:
                break
        if not chosen:
            for o in opts or []:
                t = (o.get("t") or "").lower()
                if wanted.lower() in t and "call test" not in t and "don't map" not in t:
                    chosen = o
                    break
        if not chosen:
            return {"ok": False, "error": f"no Step Field option for {wanted}", "opts": opts}
        imp.evaluate(
            """(oid) => {
              const el = document.getElementById(oid);
              if (!el) return false;
              el.dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
              el.click();
              return true;
            }""",
            chosen["id"],
        )
        mapped.append(chosen["t"])
        time.sleep(0.35)
        _close_react_select_menu(imp)
    body = ""
    try:
        body = imp.locator("body").inner_text(timeout=3000) or ""
    except Exception:
        pass
    if "Don't map this field" in body:
        return {"ok": False, "error": "mapping incomplete", "mapped": mapped}
    return {"ok": True, "mapped": mapped}


def _aio_has_steps(aio) -> bool:
    try:
        body = aio.locator("body").inner_text(timeout=3000) or ""
    except Exception:
        return False
    return ("Expected Result" in body) and ("There are no steps defined" not in body)


def _aio_step_count_hint(aio) -> int | None:
    """Best-effort count of Manual steps from aio body text (for logs)."""
    try:
        body = aio.locator("body").inner_text(timeout=3000) or ""
    except Exception:
        return None
    # Xray often shows "N Steps" or numbered Action rows — keep soft
    import re

    m = re.search(r"(\d+)\s+Steps?", body, re.I)
    if m:
        return int(m.group(1))
    return None


def _toggle_reset_current_steps(imp) -> dict[str, Any]:
    """Enable 'Reset Current Test Steps' in the CSV import dialog.

    The checkbox input[name='Clear Steps'] is often invisible to Playwright.
    Click the visible label text instead (proven on Xray Cloud 16.x).
    """
    try:
        lab = imp.get_by_text("Reset Current Test Steps", exact=False).first
        if lab.count():
            lab.click(timeout=4000)
            return {"ok": True, "via": "label_text"}
    except Exception as e:
        label_err = str(e)
    else:
        label_err = ""
    try:
        # Fallback: force-check the hidden input
        ok = imp.evaluate(
            """() => {
              const input = document.querySelector('input[name="Clear Steps"], input[name="clearSteps"]');
              if (!input) return false;
              if (!input.checked) {
                input.checked = true;
                input.dispatchEvent(new Event('change', {bubbles: true}));
                input.dispatchEvent(new Event('input', {bubbles: true}));
              }
              const label = input.closest('label') || document.querySelector('label[for="' + input.id + '"]');
              if (label) label.click();
              return !!input.checked;
            }"""
        )
        if ok:
            return {"ok": True, "via": "hidden_input_force"}
    except Exception as e:
        return {"ok": False, "error": f"label={label_err}; input={e}"}
    return {"ok": False, "error": label_err or "reset toggle failed"}


def _try_import_csv(
    page,
    frame,
    csv_path: Path,
    *,
    force_reset: bool = False,
) -> dict[str, Any]:
    """Import Manual steps via Xray UI wizard (not Attachments).

    Proven path (Xray Cloud 16.x) — see module PROVEN_UI_METHOD:
      Import → From csv... → #xray-csv-file → [Reset Current Test Steps]
      → Next → map Action*/Data/Expected Result → Validate → Import Steps
      → wait dialog gone → verify aio
    """
    _open_test_details(page, frame)
    page.mouse.wheel(0, 1800)
    page.wait_for_timeout(1500)
    aio = _xray_aio_frame(page) or _find_xray_frame(page)
    errors: list[str] = []
    had_steps_before = False

    try:
        try:
            aio.get_by_text("Dismiss", exact=True).first.click(timeout=1500)
        except Exception:
            pass
        had_steps_before = _aio_has_steps(aio)
        if had_steps_before and not force_reset:
            return {
                "ok": True,
                "method": "already_has_steps",
                "path": str(csv_path),
                "hint": "pass force_reset=True to replace existing Manual steps",
                "step_count_hint": _aio_step_count_hint(aio),
            }
        if not _open_import_menu(aio, page):
            raise RuntimeError("Import menu not opened")
        if not _click_from_csv(aio, page):
            raise RuntimeError("From csv... menu item not found")

        try:
            page.wait_for_selector(
                "iframe[src*='manual-steps-import'], section[role=dialog] iframe[src*='manual-steps-import']",
                timeout=25000,
            )
        except Exception as e:
            raise RuntimeError(f"manual-steps-import dialog iframe missing: {e}") from e
        page.wait_for_timeout(1500)
        imp = _wait_frame(page, "manual-steps-import", 25000)
        if not imp:
            raise RuntimeError("Playwright frame for manual-steps-import not found")

        # Wait for dedicated CSV input (never use Jira Attachments file input)
        file_ok = False
        for _ in range(40):
            try:
                if imp.locator("#xray-csv-file").count() > 0:
                    file_ok = True
                    break
            except Exception:
                imp = _wait_frame(page, "manual-steps-import", 5000) or imp
            page.wait_for_timeout(300)
        if not file_ok:
            raise RuntimeError("#xray-csv-file missing in import dialog")

        imp.locator("#xray-csv-file").first.set_input_files(str(csv_path))
        page.wait_for_timeout(1000)

        reset_info: dict[str, Any] | None = None
        if force_reset or had_steps_before:
            reset_info = _toggle_reset_current_steps(imp)
            page.wait_for_timeout(400)
            if not reset_info.get("ok") and force_reset:
                raise RuntimeError(f"force_reset requested but toggle failed: {reset_info}")

        try:
            imp.get_by_role("button", name="Next").first.click(timeout=8000)
        except Exception:
            imp.locator("#next, button:has-text('Next')").first.click(timeout=5000)
        page.wait_for_timeout(2000)
        imp = _wait_frame(page, "manual-steps-import", 15000) or imp

        mapped = _map_step_fields(imp)
        if not mapped.get("ok"):
            errors.append(str(mapped))
            raise RuntimeError(f"Step Field mapping failed: {mapped.get('error')}")

        try:
            imp.locator("#validate").click(timeout=4000)
        except Exception:
            imp.get_by_role("button", name="Validate").first.click(timeout=4000)
        page.wait_for_timeout(2500)
        imp = _wait_frame(page, "manual-steps-import", 15000) or imp
        try:
            vbody = imp.locator("body").inner_text(timeout=4000) or ""
        except Exception:
            vbody = ""
        if "error(s)" in vbody.lower() or "Call Test" in vbody:
            raise RuntimeError(f"Validate failed: {vbody[:300]}")

        # Click Import Steps BEFORE trusting aio (pre-existing steps would false-pass)
        clicked = False
        for _ in range(25):
            cur = _wait_frame(page, "manual-steps-import", 1000)
            if not cur:
                break
            try:
                b = cur.get_by_role("button", name="Import Steps")
                if b.count() and b.first.is_enabled():
                    b.first.click(timeout=2000)
                    clicked = True
                    break
            except Exception:
                try:
                    cur.locator("#import").click(timeout=800)
                    clicked = True
                    break
                except Exception:
                    pass
            page.wait_for_timeout(350)
        if not clicked:
            raise RuntimeError("Import Steps button not clicked")

        for _ in range(50):
            if not _wait_frame(page, "manual-steps-import", 400):
                break
            page.wait_for_timeout(250)
        page.wait_for_timeout(2000)

        aio = _xray_aio_frame(page) or aio
        if _aio_has_steps(aio):
            out: dict[str, Any] = {
                "ok": True,
                "method": "xray_csv_wizard_action_star",
                "path": str(csv_path),
                "mapped": mapped.get("mapped"),
                "force_reset": bool(force_reset),
                "had_steps_before": had_steps_before,
                "step_count_hint": _aio_step_count_hint(aio),
                "contract": PROVEN_UI_METHOD["id"],
            }
            if reset_info is not None:
                out["reset"] = reset_info
            return out

        if _attachment_toast(page) and not _aio_has_steps(aio):
            errors.append("attachment toast without visible steps")
            return {"ok": False, "error": "CSV became attachment", "errors": errors}
        raise RuntimeError("steps not visible after Import Steps")
    except Exception as e:
        errors.append(f"xray_from_csv: {e}")

    return {"ok": False, "error": "Xray From CSV import failed", "errors": errors}


def _fill_step_fields(frame, action: str, data: str, expected: str) -> bool:
    """Best-effort fill of Action / Data / Expected Result editors."""
    # Common patterns: contenteditable, textarea, input near labels
    pairs = [
        ("Action", action),
        ("Data", data or ""),
        ("Expected Result", expected),
        ("Expected result", expected),
        ("Result", expected),
    ]
    filled = 0
    for label, value in pairs:
        try:
            # label-associated field
            field = frame.get_by_label(label, exact=False)
            if field.count() > 0:
                field.first.fill(value)
                filled += 1
                continue
        except Exception:
            pass
        try:
            # placeholder
            field = frame.get_by_placeholder(label, exact=False)
            if field.count() > 0:
                field.first.fill(value)
                filled += 1
                continue
        except Exception:
            pass
        try:
            # nearest contenteditable after text
            row = frame.locator(f"text={label}").first.locator("xpath=ancestor::*[self::tr or self::div][1]")
            edit = row.locator("[contenteditable='true'], textarea, input").first
            if edit.count() > 0:
                edit.fill(value)
                filled += 1
                continue
        except Exception:
            pass

    # Fallback: fill last N empty contenteditables / textareas in order
    if filled < 2:
        try:
            editors = frame.locator("[contenteditable='true'], textarea")
            count = editors.count()
            # take last up to 3 visible empty-ish editors
            vals = [action, data or "", expected]
            idx = 0
            for i in range(count):
                if idx >= 3:
                    break
                el = editors.nth(i)
                try:
                    if not el.is_visible():
                        continue
                    el.click(timeout=1000)
                    el.fill(vals[idx])
                    idx += 1
                    filled += 1
                except Exception:
                    continue
        except Exception:
            pass
    return filled >= 2


def _try_add_steps(frame, steps: list[dict[str, str]], limit: int = 0) -> dict[str, Any]:
    added = 0
    failures: list[dict[str, Any]] = []
    use = steps if not limit else steps[:limit]
    for i, s in enumerate(use, start=1):
        if not _click_text(frame, ["Add Step", "Add step", "+ Add Step"], timeout=5000):
            if i == 1:
                return {"ok": False, "error": "Add Step button not found", "added": 0}
            break
        time.sleep(0.4)
        ok = _fill_step_fields(frame, s["Action"], s.get("Data") or "", s["Expected Result"])
        if not ok:
            failures.append({"step": i, "error": "could not fill fields", "action": s["Action"][:80]})
            # try Escape to close partial dialog
            try:
                frame.page.keyboard.press("Escape")
            except Exception:
                pass
            continue
        # Save / Create / checkmark
        saved = _click_text(
            frame,
            ["Create", "Save", "Add", "Confirm", "Update", "Done", "OK"],
            timeout=3000,
        )
        if not saved:
            try:
                frame.page.keyboard.press("Enter")
                saved = True
            except Exception:
                saved = False
        if saved:
            added += 1
        else:
            failures.append({"step": i, "error": "save not confirmed", "action": s["Action"][:80]})
        time.sleep(0.25)
    return {
        "ok": added > 0 and len(failures) == 0,
        "method": "add_step_loop",
        "added": added,
        "requested": len(use),
        "failures": failures,
    }


def proven_method() -> dict[str, Any]:
    """Return the locked Sigiri/Xray UI CSV import contract (for agents + docs)."""
    return {
        "ok": True,
        "method": PROVEN_UI_METHOD,
        "tools": [
            "liqa_xray_ui_import_csv",
            "liqa_xray_ui_import_pack",
            "liqa_xray_ui_import_registry",
            "liqa_xray_end_of_run_upload",
            "liqa_xray_ui_method",
        ],
        "docs": [
            "scripts/README-xray-ui-rpa.md",
            "skills/SIGIRI-MANUAL-STEPS-GUARD.md",
            "artifacts/xray-gold-pf59194/",
        ],
        "rule": "Never use Attachments. Never Esc in dialog. Click Import Steps then wait dialog close. force_reset replaces wrong steps.",
    }


def import_issue_ui(
    issue_key: str,
    csv_path: str,
    *,
    headed: bool = True,
    add_step_fallback: bool = True,
    add_step_limit: int = 0,
    slow_mo_ms: int = 50,
    force_reset: bool = False,
) -> dict[str, Any]:
    """Open Jira Test issue and import Manual steps via UI RPA (PROVEN_UI_METHOD)."""
    loaded = _load_steps(csv_path)
    if not loaded.get("ok"):
        return loaded

    key = issue_key.strip().upper()
    url = _browse_url(key)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"ok": False, "error": "playwright not installed — pip install playwright && playwright install chrome"}

    result: dict[str, Any] = {
        "ok": False,
        "issue_key": key,
        "url": url,
        "csv": loaded["path"],
        "step_count": loaded["count"],
        "profile": str(PROFILE_DIR),
        "at": _now(),
    }

    with sync_playwright() as p:
        launched = _launch_browser(p, headed=headed, slow_mo_ms=slow_mo_ms)
        context = launched["context"]
        page = launched["page"]
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(4000)

            if _is_login_wall(page) or not _looks_like_jira_issue(page, key):
                result.update(
                    {
                        "ok": False,
                        "needs_login": True,
                        "error": "Jira login wall — attempting secrets auto-login, else wait for human MFA.",
                        "profile": str(PROFILE_DIR),
                        "browser_mode": launched["mode"],
                        "wait_seconds": 600,
                    }
                )
                auto = _auto_login_atlassian(page, wait_seconds=180)
                result["auto_login"] = {
                    k: auto.get(k)
                    for k in ("ok", "email", "needs_mfa", "error", "mfa_completed_by_human", "used_secret")
                    if k in auto
                }
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=90_000)
                    page.wait_for_timeout(3000)
                except Exception:
                    pass
                # Keep window open (MFA / leftover login) up to 10 min — no aggressive re-nav on id.atlassian
                deadline = time.time() + 600
                while time.time() < deadline:
                    if _looks_like_jira_issue(page, key):
                        result["needs_login"] = False
                        result["error"] = None
                        result["login_completed_in_session"] = True
                        break
                    curl = (page.url or "").lower()
                    if "id.atlassian.com" in curl or "auth.atlassian.com" in curl or "login" in curl:
                        if _is_login_wall(page) and not (result.get("auto_login") or {}).get("ok"):
                            auto2 = _auto_login_atlassian(page, wait_seconds=60)
                            result["auto_login"] = {
                                k: auto2.get(k)
                                for k in ("ok", "email", "needs_mfa", "error", "mfa_completed_by_human", "used_secret")
                                if k in auto2
                            }
                        page.wait_for_timeout(2500)
                        continue
                    page.wait_for_timeout(2000)
                    if "/browse/" not in curl:
                        try:
                            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
                        except Exception:
                            pass
                else:
                    if launched["close_browser"]:
                        context.close()
                    return result
                if result.get("needs_login"):
                    if launched["close_browser"]:
                        context.close()
                    return result

            # Scroll toward Manual / Test details until Xray all-in-one iframe loads
            aio = None
            for _ in range(12):
                try:
                    page.get_by_text("Test details", exact=False).first.click(timeout=2000)
                except Exception:
                    pass
                page.mouse.wheel(0, 1600)
                page.wait_for_timeout(800)
                aio = _xray_aio_frame(page)
                if aio is not None:
                    break
            if aio is None:
                result["error"] = "Xray all-in-one iframe not loaded"
                shot = REPORT_DIR / f"{key}-no-aio-{int(time.time())}.png"
                try:
                    page.screenshot(path=str(shot), full_page=True)
                    result["screenshot"] = str(shot)
                except Exception:
                    pass
                if launched.get("close_browser"):
                    context.close()
                report = REPORT_DIR / f"{key}-last.json"
                report.write_text(json.dumps(result, indent=2), encoding="utf-8")
                result["report"] = str(report)
                return result

            frame = aio
            result["frame_url"] = getattr(frame, "url", "")
            result["browser_mode"] = launched["mode"]

            # 1) Import CSV (Xray From CSV only — never Attachments)
            imp = _try_import_csv(
                page,
                frame,
                Path(loaded["path"]),
                force_reset=bool(force_reset),
            )
            result["import_attempt"] = imp
            result["contract"] = PROVEN_UI_METHOD["id"]
            if imp.get("ok"):
                page.wait_for_timeout(2500)
                result["ok"] = True
                result["method"] = imp.get("method")
                if imp.get("mapped"):
                    result["mapped"] = imp.get("mapped")
                if imp.get("reset"):
                    result["reset"] = imp.get("reset")
            elif add_step_fallback:
                # 2) Add Step loop only inside aio
                add = _try_add_steps(frame, loaded["steps"], limit=add_step_limit)
                result["add_step_attempt"] = add
                result["ok"] = bool(add.get("ok"))
                result["method"] = add.get("method")
                result["added"] = add.get("added")
                if not result["ok"]:
                    result["error"] = add.get("error") or imp.get("error") or "UI import and Add Step both failed"
            else:
                result["error"] = imp.get("error") or "Import failed"
                if _attachment_toast(page):
                    result["error"] = "CSV landed as Jira attachment — not Manual steps"

            shot = REPORT_DIR / f"{key}-{int(time.time())}.png"
            try:
                page.screenshot(path=str(shot), full_page=True)
                result["screenshot"] = str(shot)
            except Exception:
                pass
        finally:
            if launched.get("close_browser"):
                context.close()

    report = REPORT_DIR / f"{key}-last.json"
    report.write_text(json.dumps(result, indent=2), encoding="utf-8")
    result["report"] = str(report)
    return result


def import_pack_ui(story_key: str, pack_id: str, issue_key: str, **kwargs: Any) -> dict[str, Any]:
    safe = "".join(c for c in story_key if c.isalnum() or c in "-_") or "STORY"
    pid = "".join(c for c in pack_id if c.isalnum() or c in "-_") or "P01"
    csv_path = WORKSPACE / "NewTestCases" / safe / "sigiri-manual" / pid / f"{pid}-steps.csv"
    # Prefer exact owner twin for P00 if present
    if pid == "P00":
        twin = csv_path.with_name("P00-owner-exact-120.csv")
        if twin.exists():
            csv_path = twin
    if not csv_path.exists():
        return {"ok": False, "error": f"pack CSV missing: {csv_path}"}
    return import_issue_ui(issue_key, str(csv_path), **kwargs)


def import_registry_ui(registry_json_path: str = "", **kwargs: Any) -> dict[str, Any]:
    path = Path(registry_json_path) if registry_json_path else (
        WORKSPACE / "NewTestCases" / "PF-58380" / "sigiri-manual" / "jira-created.json"
    )
    if not path.exists():
        return {"ok": False, "error": f"registry not found: {path}"}
    reg = json.loads(path.read_text(encoding="utf-8"))
    results = []
    for t in reg.get("tests") or []:
        key = t.get("key")
        pack = t.get("pack")
        story = reg.get("story") or "PF-58380"
        if not key or not pack:
            continue
        r = import_pack_ui(story, pack, key, **kwargs)
        results.append(
            {
                "key": key,
                "pack": pack,
                "ok": r.get("ok"),
                "method": r.get("method"),
                "error": r.get("error"),
                "needs_login": r.get("needs_login"),
                "screenshot": r.get("screenshot"),
            }
        )
        # stop early if login required
        if r.get("needs_login"):
            break
    ok_all = bool(results) and all(x.get("ok") for x in results)
    out = {"ok": ok_all, "registry": str(path), "results": results, "at": _now()}
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "registry-last.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def maybe_ui_import_after_run(issue_key: str, csv_path: str) -> dict[str, Any]:
    """End-of-run hook: try API first if keys exist, else UI RPA."""
    try:
        import xray_import as api
        st = api.credentials_status()
        if st.get("ok"):
            r = api.import_csv(issue_key, csv_path, replace=True)
            if r.get("ok"):
                return {"ok": True, "channel": "xray_api", **r}
            # fall through to UI
            api_err = r
        else:
            api_err = st
    except Exception as e:  # noqa: BLE001
        api_err = {"ok": False, "error": str(e)}
    ui = import_issue_ui(issue_key, csv_path)
    ui["channel"] = "ui_rpa"
    ui["api_fallback_from"] = api_err
    return ui


def ensure_jira_login(
    *,
    wait_seconds: int = 600,
    headed: bool = True,
    probe_issue: str = "PF-59477",
) -> dict[str, Any]:
    """Open persistent Chrome and wait until Jira session is usable (one-time login)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {
            "ok": False,
            "error": "playwright not installed — pip install playwright && playwright install chrome",
        }

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    url = _browse_url(probe_issue)
    result: dict[str, Any] = {
        "ok": False,
        "profile": str(PROFILE_DIR),
        "url": url,
        "wait_seconds": wait_seconds,
        "at": _now(),
    }

    with sync_playwright() as p:
        launched = _launch_browser(p, headed=headed, slow_mo_ms=50)
        context = launched["context"]
        page = launched["page"]
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=90_000)
            page.wait_for_timeout(3500)
            result["browser_mode"] = launched["mode"]
            if _looks_like_jira_issue(page, probe_issue):
                result["ok"] = True
                result["already_logged_in"] = True
            else:
                result["needs_login"] = True
                result["instruction"] = (
                    "Log in to Atlassian/Jira in the opened Chrome window. "
                    "OTP/MFA: enter yourself — agent will not invent codes. "
                    f"Waiting up to {wait_seconds}s until browse page loads."
                )
                result["hint"] = "Preferred: scripts/start-xray-chrome-cdp.ps1 then LIQA_CHROME_CDP=http://127.0.0.1:9333"
                deadline = time.time() + max(30, int(wait_seconds))
                while time.time() < deadline:
                    page.wait_for_timeout(2000)
                    if _looks_like_jira_issue(page, probe_issue):
                        result["ok"] = True
                        result["login_completed_in_session"] = True
                        break
                    if not _is_login_wall(page):
                        try:
                            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
                            page.wait_for_timeout(2000)
                        except Exception:
                            pass
                if not result.get("ok"):
                    result["error"] = "Login not completed within wait window"
            shot = REPORT_DIR / f"login-{int(time.time())}.png"
            try:
                page.screenshot(path=str(shot), full_page=True)
                result["screenshot"] = str(shot)
            except Exception:
                pass
        finally:
            if launched.get("close_browser"):
                context.close()

    (REPORT_DIR / "login-last.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def end_of_run_upload_registry(
    registry_json_path: str = "",
    *,
    headed: bool = True,
    skip_if_no_registry: bool = True,
    force_reset: bool = False,
) -> dict[str, Any]:
    """Mandatory end-of-run RPA upload for every Sigiri pack in jira-created.json.

    Called automatically when LIQA completes phase 7 or learn_cycle.
    Never requires Xray API keys — headed Chrome UI Import / Add Step only
    (API used only if keys already exist). See PROVEN_UI_METHOD.
    """
    path = Path(registry_json_path) if registry_json_path else (
        WORKSPACE / "NewTestCases" / "PF-58380" / "sigiri-manual" / "jira-created.json"
    )
    if not path.exists():
        # discover any jira-created.json under NewTestCases
        found = list((WORKSPACE / "NewTestCases").glob("**/sigiri-manual/jira-created.json"))
        if found:
            path = found[0]
        elif skip_if_no_registry:
            return {
                "ok": True,
                "skipped": True,
                "reason": "no jira-created.json — nothing to UI-upload",
                "at": _now(),
            }
        else:
            return {"ok": False, "error": f"registry not found: {path}"}

    # Prefer UI path always when no API keys (owner cannot create Xray keys)
    try:
        import xray_import as api

        st = api.credentials_status()
        if st.get("ok"):
            api_reg = api.import_registry(str(path))
            if api_reg.get("ok"):
                return {"ok": True, "channel": "xray_api", "registry": str(path), **api_reg}
            api_err = api_reg
        else:
            api_err = st
    except Exception as e:  # noqa: BLE001
        api_err = {"ok": False, "error": str(e)}

    ui = import_registry_ui(str(path), headed=headed, force_reset=bool(force_reset))
    ui["channel"] = "ui_rpa"
    ui["api_fallback_from"] = api_err
    ui["hook"] = "end_of_run"
    ui["contract"] = PROVEN_UI_METHOD["id"]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "end-of-run-last.json").write_text(json.dumps(ui, indent=2), encoding="utf-8")
    return ui
