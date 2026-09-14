"""Human Gate — structured pause for SMS / Google 2FA / CAPTCHA.

Agent owns UI until a typed blocker; human completes phone/SMS/2FA;
agent resumes on frame change, digit detection, or timeout.
Never intercept SMS or bypass 2FA — phone stays with the human.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Literal

GateKind = Literal["sms_otp", "google_2fa", "captcha", "phone_call", "password", "other"]
ResumeWhen = Literal["manual_ack", "frame_change", "digits_n", "timeout"]

try:
    from paths import CAPTURE_ROOT
except ImportError:
    CAPTURE_ROOT = Path(__file__).resolve().parents[1] / "captures"

GATE_DIR = CAPTURE_ROOT / "human-gate"
GATE_STATE = GATE_DIR / "active_gate.json"
GATE_ACK = GATE_DIR / "ACK"


def _ensure_dir() -> None:
    GATE_DIR.mkdir(parents=True, exist_ok=True)


def _clipboard_text() -> str:
    try:
        import subprocess

        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        return (r.stdout or "").strip()
    except Exception:
        return ""


def _ocr_digits(shot_path: str | None, min_len: int = 4, max_len: int = 8) -> list[str]:
    if not shot_path:
        return []
    try:
        import pytesseract
        from PIL import Image

        text = pytesseract.image_to_string(Image.open(shot_path))
    except Exception:
        return []
    found = re.findall(rf"\b\d{{{min_len},{max_len}}}\b", text or "")
    return found


def human_gate(
    kind: str = "other",
    prompt: str = "Human action required",
    timeout_sec: int = 180,
    resume_when: str = "manual_ack",
    digits: int = 6,
    poll_sec: float = 2.0,
) -> dict[str, Any]:
    """
    Pause agent loop for a human-only step.

    resume_when:
      - manual_ack: wait until ACK file exists or timeout
      - frame_change: wait until desktop pixels change
      - digits_n: wait until clipboard/OCR shows `digits` consecutive digits
      - timeout: sleep only
    """
    _ensure_dir()
    if GATE_ACK.exists():
        try:
            GATE_ACK.unlink()
        except OSError:
            pass

    shot = None
    try:
        from device_core import capture_desktop, start_presence, wait_frame_change

        cap = capture_desktop(f"gate_{kind}")
        shot = cap.get("path") if isinstance(cap, dict) else None
        try:
            start_presence(f"WAITING ON YOU: {kind}")
        except TypeError:
            start_presence()
        except Exception:
            pass
    except Exception:
        capture_desktop = None  # type: ignore
        wait_frame_change = None  # type: ignore

    state = {
        "ok": True,
        "status": "waiting",
        "kind": kind,
        "prompt": prompt,
        "timeout_sec": timeout_sec,
        "resume_when": resume_when,
        "digits": digits,
        "screenshot": shot,
        "ack_path": str(GATE_ACK),
        "instruction": (
            f"HUMAN GATE [{kind}]: {prompt}. "
            f"Complete on your phone/screen. "
            f"Optional: create empty file {GATE_ACK} to resume early. "
            "Agent will NOT intercept SMS or bypass 2FA."
        ),
        "started_at": time.time(),
    }
    GATE_STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")

    deadline = time.time() + max(5, min(int(timeout_sec), 900))
    resumed_by = "timeout"
    otp_candidates: list[str] = []

    if resume_when == "timeout":
        time.sleep(max(1, min(int(timeout_sec), 900)))
        resumed_by = "timeout"
    elif resume_when == "frame_change" and wait_frame_change is not None:
        try:
            wait_frame_change(timeout_sec=float(timeout_sec))
            resumed_by = "frame_change"
        except Exception:
            time.sleep(min(30, int(timeout_sec)))
            resumed_by = "frame_change_fallback_sleep"
    else:
        while time.time() < deadline:
            if GATE_ACK.exists():
                resumed_by = "manual_ack"
                break
            if resume_when == "digits_n":
                clip = _clipboard_text()
                m = re.search(rf"\b(\d{{{digits}}})\b", clip)
                if m:
                    otp_candidates.append(m.group(1))
                    resumed_by = "clipboard_digits"
                    break
                # re-capture lightly
                try:
                    from device_core import capture_desktop as cap2

                    c2 = cap2(f"gate_poll_{kind}")
                    p2 = c2.get("path") if isinstance(c2, dict) else None
                    otp_candidates = _ocr_digits(p2, min_len=digits, max_len=digits)
                    if otp_candidates:
                        resumed_by = "ocr_digits"
                        break
                except Exception:
                    pass
            time.sleep(max(0.5, float(poll_sec)))

    ended = time.time()
    result = {
        **state,
        "status": "resumed" if resumed_by != "timeout" else "timeout",
        "resumed_by": resumed_by,
        "elapsed_sec": round(ended - state["started_at"], 2),
        "otp_candidates": otp_candidates[:5],
        "ended_at": ended,
    }
    GATE_STATE.write_text(json.dumps(result, indent=2), encoding="utf-8")
    try:
        from device_core import stop_presence_overlay

        stop_presence_overlay()
    except Exception:
        pass
    return result


def await_otp_field(
    digits: int = 6,
    timeout_sec: int = 120,
    poll_sec: float = 1.5,
    also_clipboard: bool = True,
) -> dict[str, Any]:
    """Poll desktop OCR (+ clipboard) until an OTP of length `digits` appears."""
    _ensure_dir()
    deadline = time.time() + max(5, min(int(timeout_sec), 600))
    last_shot = None
    while time.time() < deadline:
        if also_clipboard:
            clip = _clipboard_text()
            m = re.search(rf"\b(\d{{{digits}}})\b", clip)
            if m:
                return {
                    "ok": True,
                    "otp": m.group(1),
                    "source": "clipboard",
                    "screenshot": last_shot,
                }
        try:
            from device_core import capture_desktop

            cap = capture_desktop("otp_poll")
            last_shot = cap.get("path") if isinstance(cap, dict) else None
            found = _ocr_digits(last_shot, min_len=digits, max_len=digits)
            if found:
                return {
                    "ok": True,
                    "otp": found[0],
                    "source": "ocr",
                    "all": found[:5],
                    "screenshot": last_shot,
                }
        except Exception as e:
            err = str(e)
        else:
            err = None
        time.sleep(max(0.4, float(poll_sec)))
    return {
        "ok": False,
        "reason": "timeout",
        "digits": digits,
        "screenshot": last_shot,
        "hint": "Human: type OTP or copy digits to clipboard, then retry",
    }


def ack_gate() -> dict[str, Any]:
    """Human/agent helper: create ACK so human_gate(manual_ack) resumes."""
    _ensure_dir()
    GATE_ACK.write_text("ok\n", encoding="utf-8")
    return {"ok": True, "ack_path": str(GATE_ACK)}
