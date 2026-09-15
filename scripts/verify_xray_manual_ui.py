"""Verify Manual / Xray steps visible on a Test issue via CDP."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp"))

from playwright.sync_api import sync_playwright  # noqa: E402
import xray_ui_import as u  # noqa: E402

ISSUE = sys.argv[1] if len(sys.argv) > 1 else "PF-59477"


def main() -> int:
    with sync_playwright() as p:
        launched = u._launch_browser(p, headed=True)
        page = launched["page"]
        page.goto(u._browse_url(ISSUE), wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_timeout(5000)
        try:
            page.get_by_text("Accept", exact=False).first.click(timeout=2000)
        except Exception:
            pass
        for _ in range(10):
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(350)
        fr = u._find_xray_frame(page)
        counts = {}
        for label in ["Add Step", "Import", "Manual", "Action", "Expected Result", "Steps"]:
            try:
                counts[label] = fr.get_by_text(label, exact=False).count()
            except Exception:
                counts[label] = -1
        body = page.locator("body").inner_text(timeout=5000) or ""
        needles = [
            "Log in as a user with Receipt Reallocation",
            "Loan Origination and Management",
            "Create New",
            "Please select a contract before proceeding",
        ]
        found = {n: (n in body) for n in needles}
        shot = u.REPORT_DIR / f"{ISSUE}-verify.png"
        u.REPORT_DIR.mkdir(parents=True, exist_ok=True)
        try:
            page.screenshot(path=str(shot), full_page=False, timeout=10_000)
        except Exception as e:
            shot = f"screenshot_failed: {e}"
        out = {
            "issue": ISSUE,
            "url": page.url,
            "frame": getattr(fr, "url", ""),
            "counts": counts,
            "found_in_body": found,
            "screenshot": str(shot),
            "body_snip": body[body.lower().find("manual") : body.lower().find("manual") + 800] if "manual" in body.lower() else body[:500],
        }
        print(json.dumps(out, indent=2))
        if launched.get("close_browser"):
            launched["context"].close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
