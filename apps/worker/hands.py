"""LIQA Hands — Eyes→Brain→Hands on the real desktop. Never guess x/y."""
from __future__ import annotations

import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

_SHOT_LOCK = threading.Lock()

_MANUAL_CANDIDATES = [
    Path(os.environ["MANUAL_QA_HOME"]) / "mcp" if os.environ.get("MANUAL_QA_HOME") else None,
    Path(os.environ["LIQA_HOME"]) / "mcp" if os.environ.get("LIQA_HOME") else None,
    Path(__file__).resolve().parents[2] / "mcp",
    Path(r"E:\ManualQA-Agent") / "mcp",
    Path(r"E:\QAFusionX\manualQA") / "mcp",
]
for _cand in _MANUAL_CANDIDATES:
    if _cand and _cand.is_dir() and (_cand / "device_core.py").exists():
        if str(_cand) not in sys.path:
            sys.path.insert(0, str(_cand))
        break


def _core():
    import device_core as dc

    return dc


def _png_only(label: str) -> dict[str, Any]:
    """Eyes PNG without Tesseract — live poll and later honesty rounds must not hang."""
    from PIL import Image

    root = Path(__file__).resolve().parents[2] / "captures"
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{label}.png"
    img = None
    method = "unknown"
    try:
        import mss

        with mss.mss() as sct:
            mon = sct.monitors[0]
            shot = sct.grab(mon)
            img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
            method = "mss_fast"
    except Exception:
        from PIL import ImageGrab

        img = ImageGrab.grab(all_screens=True)
        method = "imagegrab_fast"
    img.save(path)
    return {
        "path": str(path),
        "method": method,
        "size": [img.width, img.height],
        "ocr_preview": "",
        "ocr_available": False,
        "ocr_skipped": True,
    }


def screenshot(label: str = "liqa", *, ocr: bool = True, wait: bool = True) -> dict[str, Any]:
    got = _SHOT_LOCK.acquire() if wait else _SHOT_LOCK.acquire(timeout=0.15)
    if not got:
        return {
            "ok": True,
            "action": "screenshot",
            "capture": {"path": None, "ocr_preview": "", "busy": True},
            "law": "EYES first — do not click without this PNG",
        }
    try:
        cap: dict[str, Any]
        if not ocr:
            cap = _png_only(label)
        else:
            holder: dict[str, Any] = {}
            err: list[BaseException] = []

            def _run() -> None:
                try:
                    holder["cap"] = _core().capture_desktop(label)
                except BaseException as e:
                    err.append(e)

            th = threading.Thread(target=_run, daemon=True)
            th.start()
            th.join(12)
            if th.is_alive():
                cap = {"path": None, "ocr_preview": "", "ocr_timeout": True}
            elif err:
                cap = {"path": None, "ocr_preview": "", "error": str(err[0])}
            else:
                cap = holder.get("cap") or {"path": None, "ocr_preview": ""}
        return {"ok": True, "action": "screenshot", "capture": cap, "law": "EYES first — do not click without this PNG"}
    finally:
        _SHOT_LOCK.release()


def click_xy(x: int, y: int, *, only_if_seen: bool = True) -> dict[str, Any]:
    if only_if_seen:
        st = _core().device_status()
        w = int((st.get("screen_size") or {}).get("width") or 0)
        h = int((st.get("screen_size") or {}).get("height") or 0)
        if x < 0 or y < 0 or x > w or y > h:
            return {"ok": False, "reason": "coords_off_screen", "ask_user": True}
    return {"ok": True, "action": "click", "result": _core().click_at(int(x), int(y))}


def click_text(text: str) -> dict[str, Any]:
    r = _core().click_text(text)
    if not r.get("ok") and r.get("reason") == "text_not_found_on_screen":
        r["ask_user"] = True
        r["honesty"] = "Control not visible on latest capture — will not guess."
    return r


def type_text(text: str, *, interval: float = 0.05, is_secret: bool = False) -> dict[str, Any]:
    gui = _core()._import_gui()
    gui.typewrite(text, interval=max(0.02, interval))
    shown = "<redacted>" if is_secret else text[:80]
    return {"ok": True, "action": "type", "typed": shown, "secret": is_secret}


def hotkey(*keys: str) -> dict[str, Any]:
    gui = _core()._import_gui()
    gui.hotkey(*keys)
    return {"ok": True, "action": "hotkey", "keys": list(keys)}


def wait_frame(timeout_sec: float = 15.0) -> dict[str, Any]:
    return {"ok": True, "action": "wait_frame", "result": _core().wait_frame_change(timeout_sec=timeout_sec)}


def wait_analyzable(seconds: float = 1.2) -> dict[str, Any]:
    time.sleep(max(0.3, seconds))
    return {"ok": True, "action": "wait_analyzable", "slept": seconds}


def presence(name: str = "LIQA Worker") -> dict[str, Any]:
    try:
        return {"ok": True, "action": "presence", "result": _core().start_presence(name)}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


def status() -> dict[str, Any]:
    return _core().device_status()


def focus_window(title_substring: str) -> dict[str, Any]:
    try:
        return _core().focus_window(title_substring)
    except Exception as e:
        return {"ok": False, "reason": str(e), "ask_user": True}


def scroll(clicks: int = -3) -> dict[str, Any]:
    gui = _core()._import_gui()
    gui.scroll(int(clicks))
    return wait_analyzable(0.4) | {"ok": True, "action": "scroll", "clicks": clicks}


def drag(x1: int, y1: int, x2: int, y2: int) -> dict[str, Any]:
    gui = _core()._import_gui()
    _core().move_mouse(x1, y1)
    gui.dragTo(x2, y2, duration=0.6)
    return {"ok": True, "action": "drag", "from": [x1, y1], "to": [x2, y2]}


def right_click_text(text: str) -> dict[str, Any]:
    r = _core().click_text(text)
    if not r.get("ok"):
        r["ask_user"] = True
        return r
    gui = _core()._import_gui()
    gui.click(button="right")
    return {"ok": True, "action": "right_click", "matched": r}


def double_click_xy(x: int, y: int) -> dict[str, Any]:
    return {"ok": True, "action": "double_click", "result": _core().click_at(int(x), int(y), clicks=2)}


def hotkey_guarded(*keys: str) -> dict[str, Any]:
    k = [str(x).lower() for x in keys]
    if "ctrl" in k and "l" in k:
        return {"ok": False, "reason": "Ctrl+L forbidden after entry URL — mouse clicks only"}
    return hotkey(*keys)


def type_ime(text: str, *, sinhala: bool = False) -> dict[str, Any]:
    return type_text(text, interval=0.08 if sinhala else 0.05)


def start_menu_search(query: str) -> dict[str, Any]:
    hotkey("win")
    time.sleep(0.4)
    t = type_text(query)
    time.sleep(0.3)
    hotkey("enter")
    return {"ok": True, "action": "start_menu", "query": query, "typed": t}


def alt_tab() -> dict[str, Any]:
    return hotkey("alt", "tab") | {"note": "last resort app switch"}


def ignore_printscreen() -> dict[str, Any]:
    return {"ok": True, "action": "ignore_printscreen", "note": "Do not treat PrtSc as a Hands command."}


def calibrate() -> dict[str, Any]:
    st = status()
    w = int((st.get("screen_size") or {}).get("width") or 0)
    h = int((st.get("screen_size") or {}).get("height") or 0)
    if w < 800 or h < 600:
        return {"ok": False, "reason": "display_too_small"}
    points = [(40, 40), (w - 40, 40), (40, h - 40), (w - 40, h - 40), (w // 2, h // 2)]
    moves = [_core().move_mouse(x, y, duration_sec=0.35) for x, y in points]
    return {"ok": True, "action": "calibrate", "points": points, "moves": moves, "screen": {"w": w, "h": h}}
