"""Playbooks: shop, social, qa, os — predicted extras, not the only architecture."""
from __future__ import annotations

from typing import Any


def shop(task: str) -> list[str]:
    return [
        "Search box fill + Enter (not only sponsored row).",
        "Open top N listings. Read rating count vs average.",
        "Read 3 recent 1-star and 3 5-star reviews.",
        "Check delivery to the address in the task.",
        "Size/color only if the user named one. Out of stock → next candidate.",
        "Cart review screenshot before pay.",
        "Payment page = human_gate unless test-card is in vault.",
        "Stop if checkout wants a new account the user did not request.",
        "Order confirmation PNG + plain English why this SKU.",
    ]


def social(task: str) -> list[str]:
    return [
        "Follow the Create vs Log in button that is on screen.",
        "Cookie consent click_text if visible.",
        "Birthday/gender only if the user supplied them.",
        "Gmail verification: same session, click visible subject, copy visible digits only.",
        "Google phone prompt → gate immediately.",
        "Compose post from the user's text only. Proof PNG of the live post.",
        "Logout only if asked. Refuse create-accounts-for-N-emails.",
    ]


def manual_qa(task: str) -> list[str]:
    return [
        "ManualQA 10 steps. Maker then checker in the SAME Chrome process.",
        "Logout/login inside the same window. Never close mid-job.",
        "Do not edit/delete existing Xray tests. New tests only if licensed.",
        "Book1 + proof PNGs. 20 approaches before REAL_BUG.",
    ]


def os_generic(task: str) -> list[str]:
    return [
        "Any window named in the task: Explorer, Notepad, Excel UI, PDF in Edge, Start Menu.",
        "New tab via UI click, not chrome.tabs API. Address bar forbidden after entry URL.",
        "Print / UAC / SmartScreen / BitLocker = human_gate.",
        "Map every new window. Close extra popups only if X is OCR-visible.",
    ]


def for_kind(kind: str, task: str) -> list[str]:
    return {"shop_and_order": shop, "social_account": social, "manual_qa": manual_qa}.get(kind, os_generic)(task)
