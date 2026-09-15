"""Verify Manual steps landed in Xray Test details for registry keys."""
from __future__ import annotations

import json
import re
import time

from playwright.sync_api import sync_playwright

KEYS = ["PF-59476", "PF-59477", "PF-59478", "PF-59479", "PF-59480", "PF-59481"]


def panel_body(page) -> str:
    for f in page.frames:
        try:
            hit = f.evaluate(
                """() => Array.from(document.querySelectorAll('button,[role=button],a'))
                  .some(el => /Add Step/i.test((el.innerText||el.getAttribute('aria-label')||'')))"""
            )
        except Exception:
            hit = False
        if not hit:
            continue
        try:
            return f.evaluate("() => document.body ? document.body.innerText : ''") or ""
        except Exception:
            return ""
    return ""


def main() -> int:
    out = {}
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
        page = b.contexts[0].pages[0]
        for key in KEYS:
            page.goto(
                f"https://lolcgroupdev.atlassian.net/browse/{key}",
                wait_until="domcontentloaded",
                timeout=90_000,
            )
            time.sleep(4)
            for _ in range(5):
                page.mouse.wheel(0, 1400)
                time.sleep(0.25)
            try:
                page.get_by_text("Test details", exact=False).first.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass
            time.sleep(2)
            body = panel_body(page)
            m = re.search(r"Action\s*\n\s*(.+)", body)
            out[key] = {
                "has_add_step": "Add Step" in body,
                "has_action": "Action" in body,
                "body_len": len(body),
                "approx_numbered": len(re.findall(r"(?m)^\s*\d+\s*$", body)),
                "first_action": (m.group(1).strip()[:90] if m else ""),
            }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
