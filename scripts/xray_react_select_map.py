#!/usr/bin/env python3
"""Xray CSV import: map react-select Step Fields (Action*/Data/Expected Result) then Import Steps."""
from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9333"
OUT = Path(r"E:\LIQA\workspace\default-run\reports\xray-ui-import")
OUT.mkdir(parents=True, exist_ok=True)
ROOT = Path(r"E:\LIQA\workspace\default-run\NewTestCases\PF-58380\sigiri-manual")

CLICK_FROM_CSV = """() => {
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


def wait_frame(page, needle: str, timeout_s: float = 50):
    end = time.time() + timeout_s
    while time.time() < end:
        for f in page.frames:
            if needle in (f.url or ""):
                return f
        time.sleep(0.3)
    return None


def log(msg: str) -> None:
    print(msg.encode("ascii", "replace").decode("ascii"), flush=True)


def dismiss(page) -> None:
    for _ in range(3):
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        time.sleep(0.12)


def open_map(page, issue: str, csv_path: Path):
    dismiss(page)
    page.goto(
        f"https://lolcgroupdev.atlassian.net/browse/{issue}",
        wait_until="domcontentloaded",
        timeout=120000,
    )
    time.sleep(8)
    for _ in range(20):
        page.mouse.wheel(0, 1100)
        time.sleep(0.1)
    try:
        page.get_by_text("Test details", exact=False).first.click(timeout=5000)
    except Exception:
        pass
    aio = wait_frame(page, "all-in-one", 50)
    if not aio:
        raise RuntimeError("no aio")
    time.sleep(1.5)
    try:
        aio.get_by_text("Dismiss", exact=True).first.click(timeout=800)
    except Exception:
        pass
    body = aio.locator("body").inner_text(timeout=5000) or ""
    if "Expected Result" in body and "There are no steps defined" not in body:
        return aio, None, True

    aio.get_by_role("button", name="Import").first.click(timeout=8000)
    time.sleep(0.9)
    assert aio.evaluate(CLICK_FROM_CSV)
    page.wait_for_selector("iframe[src*='manual-steps-import']", timeout=30000)
    time.sleep(2)
    imp = wait_frame(page, "manual-steps-import", 30)
    assert imp
    end = time.time() + 25
    while time.time() < end:
        try:
            if imp.locator("#xray-csv-file").count():
                break
        except Exception:
            imp = wait_frame(page, "manual-steps-import", 5) or imp
        time.sleep(0.3)

    imp.locator("#xray-csv-file").first.set_input_files(str(csv_path))
    time.sleep(1.2)
    imp.get_by_role("button", name="Next").first.click(timeout=8000)
    time.sleep(2.5)
    return aio, wait_frame(page, "manual-steps-import", 20) or imp, False


def list_options(imp) -> list[dict]:
    return imp.evaluate(
        """() => Array.from(document.querySelectorAll('[id*=-option-]'))
          .map(e => ({id: e.id, t: (e.textContent || '').trim()}))
          .filter(o => o.t)"""
    )


def shown_value(imp, input_id: str) -> str:
    try:
        return imp.locator(f"#{input_id}").evaluate(
            """e => {
              const control = e.closest('[class*=control]');
              const root = control && control.parentElement;
              const v = root && root.querySelector('[class*=singleValue]');
              return v ? v.textContent.trim() : '';
            }"""
        )
    except Exception:
        return ""


def close_select_menu(imp) -> None:
    """Close react-select menu without Esc (Esc closes the whole AUI dialog)."""
    try:
        imp.evaluate(
            """() => {
              // blur any open react-select input
              const a = document.activeElement;
              if (a && a.blur) a.blur();
              document.body.click();
            }"""
        )
    except Exception:
        pass
    time.sleep(0.2)


def pick_option(imp, page, input_id: str, wanted: str) -> bool:
    """Open react-select for input_id and choose best matching option (JS clicks)."""
    close_select_menu(imp)
    opened = imp.evaluate(
        """(id) => {
          const input = document.getElementById(id);
          if (!input) return {ok:false, err:'no input'};
          const control = input.closest('[class*=control]');
          const indicator = control && control.querySelector('[class*=indicatorContainer]');
          (indicator || control || input).dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
          (indicator || control || input).click();
          return {ok:true};
        }""",
        input_id,
    )
    log(f"open {input_id} {opened}")
    time.sleep(0.5)
    opts = list_options(imp)
    log(f"{input_id} options={[o['t'] for o in opts]}")

    candidates = [
        wanted,
        wanted + "*",
        wanted.rstrip("*"),
        "Action*" if wanted.lower().startswith("action") else wanted,
    ]
    chosen = None
    for cand in candidates:
        for o in opts:
            if o["t"] == cand:
                chosen = o
                break
        if chosen:
            break
    if not chosen:
        for o in opts:
            t = o["t"].lower()
            if (
                wanted.lower() in t
                and "call test" not in t
                and "don't map" not in t
            ):
                chosen = o
                break
    if not chosen:
        log(f"no option for {wanted}")
        close_select_menu(imp)
        return False

    clicked = imp.evaluate(
        """(oid) => {
          const el = document.getElementById(oid);
          if (!el) return false;
          el.dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
          el.dispatchEvent(new MouseEvent('mouseup', {bubbles:true}));
          el.click();
          return true;
        }""",
        chosen["id"],
    )
    time.sleep(0.45)
    close_select_menu(imp)
    shown = shown_value(imp, input_id)
    ok = bool(clicked) and (
        shown.lower().startswith(wanted.lower().rstrip("*")) or shown == chosen["t"]
    )
    log(f"{input_id} chose={chosen['t']!r} shown={shown!r} ok={ok}")
    return ok


def map_fields(imp, page) -> bool:
    ids = imp.evaluate(
        """() => Array.from(document.querySelectorAll('input[id^=react-select-][id$=-input]'))
          .map(e => e.id)"""
    )
    if len(ids) < 3:
        ids = ["react-select-2-input", "react-select-3-input", "react-select-4-input"]
    log(f"inputs={ids}")
    targets = ["Action", "Data", "Expected Result"]
    ok_all = True
    for i, target in enumerate(targets):
        ok = pick_option(imp, page, ids[i], target)
        ok_all = ok_all and ok
    after = imp.locator("body").inner_text(timeout=4000) or ""
    (OUT / "map-verified.txt").write_text(after, encoding="utf-8")
    dont = after.count("Don't map this field")
    log(f"Dont map remaining={dont}")
    return ok_all and dont == 0


def validate_import(imp, page, aio) -> bool:
    try:
        imp.locator("#validate").click(timeout=4000)
    except Exception:
        imp.get_by_role("button", name="Validate").first.click(timeout=4000)
    log("Validate")
    time.sleep(2.5)
    imp = wait_frame(page, "manual-steps-import", 15) or imp
    body = imp.locator("body").inner_text(timeout=4000) or ""
    (OUT / "validate-result.txt").write_text(body, encoding="utf-8")
    log("validate: " + body[:220].replace("\n", " | "))
    if "error(s)" in body.lower() or "Call Test" in body:
        return False

    # Click Import Steps FIRST — do not treat pre-existing aio steps as success
    clicked = False
    for _ in range(25):
        cur = wait_frame(page, "manual-steps-import", 1)
        if not cur:
            break
        try:
            b = cur.get_by_role("button", name="Import Steps")
            if b.count() and b.first.is_enabled():
                b.first.click(timeout=2000)
                clicked = True
                log("Import Steps")
                break
        except Exception:
            pass
        try:
            cur.locator("#import").click(timeout=800)
            clicked = True
            log("Import #import")
            break
        except Exception:
            pass
        time.sleep(0.35)

    if not clicked:
        log("Import Steps button not clicked")
        return False

    # Wait for dialog iframe to close
    for _ in range(50):
        if not wait_frame(page, "manual-steps-import", 0.4):
            break
        time.sleep(0.25)
    time.sleep(2.0)

    aio2 = wait_frame(page, "all-in-one", 10) or aio
    try:
        ab = aio2.locator("body").inner_text(timeout=4000) or ""
    except Exception:
        ab = ""
    ok = ("Expected Result" in ab) and ("There are no steps defined" not in ab)
    log(f"post-import steps_ok={ok}")
    return ok


def upload_one(page, issue: str, csv_path: Path) -> dict:
    aio, imp, already = open_map(page, issue, csv_path)
    if already:
        return {"ok": True, "issue": issue, "skipped": True}
    if not map_fields(imp, page):
        page.screenshot(path=str(OUT / f"{issue}-mapfail.png"), full_page=True)
        return {"ok": False, "issue": issue, "error": "mapping incomplete"}
    ok = validate_import(imp, page, aio)
    page.screenshot(
        path=str(OUT / (f"{issue}-ok.png" if ok else f"{issue}-valfail.png")),
        full_page=True,
    )
    return {"ok": ok, "issue": issue, "method": "action-star-map"}


def main() -> int:
    mapping = [
        ("PF-59476", ROOT / "P00" / "P00-owner-exact-120.csv"),
        ("PF-59478", ROOT / "P02" / "P02-steps.csv"),
        ("PF-59479", ROOT / "P03" / "P03-steps.csv"),
        ("PF-59481", ROOT / "P04" / "P04-steps.csv"),
        ("PF-59480", ROOT / "P05" / "P05-steps.csv"),
    ]
    if not mapping[0][1].exists():
        mapping[0] = ("PF-59476", ROOT / "P00" / "P00-steps.csv")

    results = []
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(CDP)
        page = b.contexts[0].pages[0]
        for issue, csv_path in mapping:
            log(f"=== {issue} ===")
            try:
                r = upload_one(page, issue, csv_path)
            except Exception as e:
                r = {"ok": False, "issue": issue, "error": str(e)}
            results.append(r)
            log(json.dumps({k: r.get(k) for k in ("ok", "issue", "error", "skipped")}))
            dismiss(page)
            time.sleep(1.2)

    summary = {"all_ok": all(r.get("ok") for r in results), "results": results}
    (OUT / "batch-react-select.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log("all_ok=" + str(summary["all_ok"]))
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
