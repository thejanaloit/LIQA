"""Natural-language intent → predicted steps. EN + SI keywords. Honest gates."""
from __future__ import annotations

import re
from typing import Any

import playbooks
import policy

CAPTCHA_VISIBLE = ("i'm not a robot", "im not a robot", "i am not a robot", "මම රොබෝවෙක් නෙවෙයි")
CAPTCHA_HARD = ("select all images", "unusual traffic", "verify you are human", "hcaptcha", "recaptcha challenge")
MFA_SMS = ("enter the code we sent", "sms code", "text message")
MFA_GOOGLE = ("google prompt", "2-step verification", "tap yes on your phone")
SMARTSCREEN = ("windows protected your pc", "smartscreen")
UAC = ("user account control", "do you want to allow this app")
PHONE = ("we will call you", "phone call verification")

SI_SHOP = ("ඇණවුම", "ගාන", "කඩේ", "මිලදී")
SI_FB = ("ෆේස්බුක්", "ෆේස් බුක්")
SI_QA = ("පරීක්ෂණ", "යූඒටී")


def restatement(task: str) -> dict[str, str]:
    raw = (task or "").strip()
    return {
        "en": raw,
        "si": raw,
        "plain": raw if raw else "Target unclear — ask the user.",
    }


def classify_blocker(ocr_or_title: str) -> str | None:
    t = (ocr_or_title or "").lower()
    if any(k in t for k in MFA_GOOGLE):
        return "google_2fa"
    if any(k in t for k in MFA_SMS):
        return "sms_otp"
    if any(k in t for k in PHONE):
        return "phone_call"
    if any(k in t for k in SMARTSCREEN):
        return "smartscreen"
    if any(k in t for k in UAC):
        return "uac"
    if "bitlocker" in t:
        return "bitlocker"
    if any(k in t for k in CAPTCHA_HARD):
        return "hard_captcha"
    if any(k in t for k in CAPTCHA_VISIBLE):
        return "checkbox_captcha"
    if "captcha" in t:
        return "hard_captcha"
    if "printer" in t and "print" in t:
        return "printer"
    return None


def parse_address(task: str) -> str | None:
    m = re.search(r"\bto\s+(.+)$", task or "", re.I)
    if m:
        return m.group(1).strip()[:200]
    m = re.search(r"(කරන්න|යවන්න)\s+(.+)$", task or "")
    return m.group(2).strip()[:200] if m else None


def predict(task: str) -> dict[str, Any]:
    pol = policy.check_task(task)
    raw = (task or "").strip()
    low = raw.lower()
    steps = [{"id": i, "manualqa": i, "do": d} for i, d in enumerate(
        [
            "Restate the task. Stop if target is unclear.",
            "List credentials. Never invent passwords or OTPs.",
            "Gather what success looks like.",
            "Read prior knowledge / existing tests (read-only).",
            "Preflight: headed desktop, one browser, entry URL once.",
            "Map the live UI first (no pass/fail yet).",
            "Write the live plan: next visible control only.",
            "Eyes PNG → Brain → Hands Bezier+type → wait frame.",
            "Save proof PNGs and a plain-English debrief.",
            "Honesty: 20 approaches before REAL BUG; 3 re-checks; learn.",
        ],
        start=1,
    )]
    kind = "general_pc"
    if any(w in low for w in ("order", "buy", "shop", "amazon", "daraz", "cart", "checkout", "reviews")) or any(w in raw for w in SI_SHOP):
        kind = "shop_and_order"
    elif any(w in low for w in ("facebook", "fb ", "instagram", "twitter", "x.com")) or any(w in raw for w in SI_FB):
        kind = "social_account"
    elif re.search(r"\b(jira|uat|maker|checker)\b", low) or "test case" in low or re.search(r"(^|[^a-z])qa([^a-z]|$)", low) or any(w in raw for w in SI_QA):
        kind = "manual_qa"
    extras = playbooks.for_kind(kind, raw)
    next3 = extras[:3] if extras else ["Screenshot", "Find the named control", "Ask if missing"]
    unclear = (not pol.get("ok") and pol.get("gate") == "unclear") or len(raw) < 4
    return {
        "ok": pol.get("ok") and not unclear,
        "task": raw,
        "restate": restatement(raw),
        "kind": "unclear" if unclear else kind,
        "core_loop": "manualqa_10",
        "predicted": extras,
        "next3": next3,
        "address": parse_address(raw),
        "steps": steps,
        "policy": pol,
        "ask_user": unclear or not pol.get("ok"),
        "honesty": {
            "checkbox_captcha": "If I'm not a robot is visible on the latest PNG, click it.",
            "hard_captcha_sms_google": "Pause. Notify human. Resume on ACK.",
            "invisible_control": "Ask the user. Never guess x/y.",
            "not_a_bot_farm": "Own PC + own credentials only.",
        },
    }


def looks_like_email(text: str) -> bool:
    return bool(re.search(r"[^@\s]+@[^@\s]+\.[^@\s]+", text or ""))
