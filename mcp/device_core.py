"""
Full Windows device control core for theja-humanize MCP.
Inspired by flowdevs-io/Recursive-Control + LOFIN desktop control + QAFusionX bezier mouse.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from paths import CAPTURE_ROOT, KNOWLEDGE_ROOT, REPO_ROOT, LIB_ROOT

# CAPTURE_ROOT from paths


_BEZIER = False
try:
    from lib.bezier_mouse import human_move_to as _bezier_move
    _BEZIER = True
except Exception:
    _bezier_move = None  # type: ignore


def _import_gui():
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.15
    return pyautogui


def _import_win32():
    import win32con
    import win32gui
    return win32con, win32gui


def _ocr_ready() -> bool:
    try:
        import pytesseract
        for cand in (r"C:\Program Files\Tesseract-OCR\tesseract.exe", r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"):
            if Path(cand).exists():
                pytesseract.pytesseract.tesseract_cmd = cand
                return True
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def cursor_position() -> dict[str, int]:
    p = _import_gui().position()
    return {"x": int(p.x), "y": int(p.y)}


def list_monitors() -> list[dict[str, Any]]:
    try:
        import mss
        with mss.mss() as sct:
            out = []
            for i, mon in enumerate(sct.monitors):
                if i == 0:
                    continue
                out.append({"index": i, "left": mon["left"], "top": mon["top"], "width": mon["width"], "height": mon["height"]})
            if out:
                return out
    except Exception:
        pass
    w, h = _import_gui().size()
    return [{"index": 1, "left": 0, "top": 0, "width": w, "height": h}]


def list_windows(limit: int = 60) -> list[dict[str, Any]]:
    _, win32gui = _import_win32()
    out: list[dict[str, Any]] = []

    def enum(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd)
        if not title or len(title.strip()) < 2:
            return
        try:
            rect = win32gui.GetWindowRect(hwnd)
        except Exception:
            return
        out.append({"hwnd": int(hwnd), "title": title, "rect": list(rect)})

    win32gui.EnumWindows(enum, None)
    fg = foreground_hwnd()
    for w in out:
        w["foreground"] = w["hwnd"] == fg
    out.sort(key=lambda x: (not x["foreground"], x["title"].lower()))
    return out[:limit]


def foreground_hwnd() -> int | None:
    _, win32gui = _import_win32()
    try:
        return int(win32gui.GetForegroundWindow())
    except Exception:
        return None


def foreground_title() -> str:
    _, win32gui = _import_win32()
    try:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())
    except Exception:
        return ""


def find_window(title_substring: str) -> dict[str, Any] | None:
    s = title_substring.lower()
    for w in list_windows(200):
        if s in w["title"].lower():
            return w
    return None


def focus_window(title_substring: str) -> dict[str, Any]:
    win32con, win32gui = _import_win32()
    w = find_window(title_substring)
    if not w:
        return {"ok": False, "reason": "window_not_found", "query": title_substring}
    try:
        hwnd = w["hwnd"]
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.35)
        return {"ok": True, "window": w, "foreground_now": foreground_title()}
    except Exception as e:
        return {"ok": False, "reason": str(e), "window": w}


def _annotate(img, stem: str):
    try:
        ha = LIB_ROOT
        if str(ha) not in sys.path:
            sys.path.insert(0, str(ha))
        from capture_border import annotate_capture
        return annotate_capture(img, stem, tool="HumanizeDevice")
    except Exception:
        return img


def capture_desktop(
    label: str = "capture",
    monitor_index: int | None = None,
    *,
    ocr: bool = False,
    enumerate_windows: bool = True,
) -> dict[str, Any]:
    CAPTURE_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = CAPTURE_ROOT / f"device_{stamp}_{label}.png"
    img = None
    capture_method = "unknown"
    bounds = None

    try:
        import mss
        from PIL import Image
        with mss.mss() as sct:
            if monitor_index is not None and 0 < monitor_index < len(sct.monitors):
                mon = sct.monitors[monitor_index]
            else:
                mon = sct.monitors[0]
            bounds = {"left": mon["left"], "top": mon["top"], "width": mon["width"], "height": mon["height"]}
            shot = sct.grab(mon)
            img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
            capture_method = "mss_all_monitors" if monitor_index is None else f"mss_monitor_{monitor_index}"
    except Exception:
        pass

    if img is None:
        from PIL import ImageGrab
        img = ImageGrab.grab(all_screens=True)
        capture_method = "imagegrab_all_screens"
        bounds = {"left": 0, "top": 0, "width": img.width, "height": img.height}

    img = _annotate(img, path.stem)
    img.save(path)
    frame_hash = hashlib.sha256(path.read_bytes()).hexdigest()[:16]

    ocr_preview = ""
    ocr_targets: list[dict[str, Any]] = []
    if ocr and _ocr_ready():
        try:
            import pytesseract
            small = img.resize((max(1, img.width // 2), max(1, img.height // 2)))
            ocr_preview = pytesseract.image_to_string(small)[:1200]
            data = pytesseract.image_to_data(small, output_type=pytesseract.Output.DICT)
            scale = 2.0
            for i, word in enumerate(data.get("text", [])):
                w = (word or "").strip()
                if len(w) < 3:
                    continue
                conf = int(float(data["conf"][i])) if data["conf"][i] != "-1" else 0
                if conf < 40:
                    continue
                x = int(data["left"][i] * scale)
                y = int(data["top"][i] * scale)
                ww = int(data["width"][i] * scale)
                hh = int(data["height"][i] * scale)
                ocr_targets.append({"text": w, "confidence": conf, "bbox": [x, y, x + ww, y + hh], "center": [x + ww // 2, y + hh // 2]})
            seen: set[str] = set()
            deduped = []
            for t in sorted(ocr_targets, key=lambda z: -z["confidence"]):
                key = t["text"].lower()
                if key in seen:
                    continue
                seen.add(key)
                deduped.append(t)
            ocr_targets = deduped[:80]
        except Exception as e:
            ocr_preview = f"ocr_error:{e}"

    return {
        "path": str(path),
        "method": capture_method,
        "size": [img.width, img.height],
        "bounds": bounds,
        "frame_hash": frame_hash,
        "cursor": cursor_position(),
        "foreground": foreground_title(),
        "windows": [w["title"] for w in list_windows(25)] if enumerate_windows else [],
        "monitors": list_monitors() if enumerate_windows else [],
        "ocr_preview": ocr_preview,
        "ocr_targets": ocr_targets,
        "ocr_available": _ocr_ready(),
    }


def _grab_screen_image():
    try:
        import mss
        from PIL import Image
        with mss.mss() as sct:
            mon = sct.monitors[0]
            shot = sct.grab(mon)
            return Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
    except Exception:
        from PIL import ImageGrab
        return ImageGrab.grab(all_screens=True)


def wait_frame_change(timeout_sec: float = 8.0, poll_ms: int = 250) -> dict[str, Any]:
    """Hash-only poll — no OCR, no 37 PNG writes. That was the headed-loop stall."""
    first_img = _grab_screen_image()
    h0 = hashlib.sha256(first_img.tobytes()).hexdigest()[:16]
    CAPTURE_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    before = CAPTURE_ROOT / f"device_{stamp}_wait_before.png"
    first_img.save(before)
    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        time.sleep(max(0.08, poll_ms / 1000.0))
        cur = _grab_screen_image()
        if hashlib.sha256(cur.tobytes()).hexdigest()[:16] != h0:
            after = CAPTURE_ROOT / f"device_{datetime.now().strftime('%Y%m%d_%H%M%S')}_wait_after.png"
            cur.save(after)
            return {
                "ok": True,
                "changed": True,
                "before": str(before),
                "after": str(after),
                "elapsed_sec": round(time.time() - t0, 2),
            }
    after = CAPTURE_ROOT / f"device_{datetime.now().strftime('%Y%m%d_%H%M%S')}_wait_timeout.png"
    _grab_screen_image().save(after)
    return {
        "ok": False,
        "changed": False,
        "before": str(before),
        "after": str(after),
        "elapsed_sec": round(time.time() - t0, 2),
        "reason": "timeout_no_frame_change",
    }


def move_mouse(x: int, y: int, duration_sec: float = 0.85) -> dict[str, Any]:
    if _BEZIER and _bezier_move:
        _bezier_move(x, y, duration_sec=duration_sec)
        method = "bezier"
    else:
        _import_gui().moveTo(x, y, duration=duration_sec)
        method = "linear"
    return {"ok": True, "x": x, "y": y, "method": method, "cursor_after": cursor_position()}


def type_text(text: str, *, interval: float = 0.03, enter: bool = False) -> dict[str, Any]:
    """Type with visible key delay via pyautogui. Never logs secrets — caller must not pass passwords into chat."""
    if text is None:
        return {"ok": False, "error": "text required"}
    pyautogui = _import_gui()
    pyautogui.write(str(text), interval=max(0.0, float(interval)))
    if enter:
        pyautogui.press("enter")
    return {
        "ok": True,
        "chars": len(str(text)),
        "enter": bool(enter),
        "interval": float(interval),
        "cursor_after": cursor_position(),
        "foreground": foreground_title(),
    }


def hotkey(keys: str | list[str]) -> dict[str, Any]:
    """Press a hotkey combo. keys may be 'ctrl+c' or ['ctrl','c']."""
    if isinstance(keys, str):
        parts = [p.strip() for p in keys.replace("-", "+").split("+") if p.strip()]
    else:
        parts = [str(p).strip() for p in keys if str(p).strip()]
    if not parts:
        return {"ok": False, "error": "keys required e.g. ctrl+s or alt+tab"}
    pyautogui = _import_gui()
    pyautogui.hotkey(*parts)
    return {
        "ok": True,
        "keys": parts,
        "hotkey": "+".join(parts),
        "cursor_after": cursor_position(),
        "foreground": foreground_title(),
    }


def click_at(x: int, y: int, *, button: str = "left", clicks: int = 1, duration_sec: float = 0.85) -> dict[str, Any]:
    pyautogui = _import_gui()
    if _BEZIER and _bezier_move:
        _bezier_move(x, y, duration_sec=duration_sec)
        time.sleep(random.uniform(0.06, 0.16))
        pyautogui.click(x, y, clicks=clicks, button=button)
        method = "bezier_move+click"
    else:
        pyautogui.moveTo(x, y, duration=duration_sec)
        pyautogui.click(clicks=clicks, button=button)
        method = "linear"
    return {"ok": True, "x": x, "y": y, "button": button, "clicks": clicks, "method": method, "cursor_after": cursor_position()}


def click_text(text: str, *, partial: bool = True, min_confidence: int = 45) -> dict[str, Any]:
    cap = capture_desktop("click_text_scan", ocr=True)
    if not cap.get("ocr_available"):
        return {"ok": False, "reason": "ocr_not_available", "hint": "Install Tesseract OCR", "screenshot": cap["path"]}
    needle = text.lower().strip()
    matches = []
    for t in cap.get("ocr_targets", []):
        hay = t["text"].lower()
        if (partial and needle in hay) or (not partial and hay == needle):
            matches.append(t)
    matches = [m for m in matches if m.get("confidence", 0) >= min_confidence]
    if not matches:
        return {"ok": False, "reason": "text_not_found_on_screen", "query": text, "screenshot": cap["path"], "ocr_preview": cap.get("ocr_preview", "")[:400]}
    best = max(matches, key=lambda m: m["confidence"])
    cx, cy = best["center"]
    return {"ok": True, "matched": best, "screenshot_before": cap["path"], "click": click_at(cx, cy)}


def click_window_center(title_substring: str) -> dict[str, Any]:
    focus = focus_window(title_substring)
    if not focus.get("ok"):
        return focus
    rect = focus["window"]["rect"]
    cx = (rect[0] + rect[2]) // 2
    cy = (rect[1] + rect[3]) // 2
    return {"ok": True, "window": focus["window"], "click": click_at(cx, cy)}


def device_status() -> dict[str, Any]:
    w, h = _import_gui().size()
    return {
        "platform": "windows",
        "screen_size": {"width": w, "height": h},
        "cursor": cursor_position(),
        "foreground": foreground_title(),
        "monitors": list_monitors(),
        "window_count": len(list_windows(500)),
        "bezier_mouse": bool(_BEZIER),
        "ocr_available": _ocr_ready(),
        "capture_root": str(CAPTURE_ROOT),
        "knowledge_refs": load_knowledge_refs(),
    }


def recursive_control_step(intent: str = "", *, wait_change: bool = False) -> dict[str, Any]:
    cap = capture_desktop("recursive_step")
    payload = {
        "law": "EYES first — read screenshot + ocr_targets; never blind x/y",
        "intent": intent,
        "capture": cap,
        "device": {"cursor": cap["cursor"], "foreground": cap["foreground"], "windows": list_windows(30)},
        "suggested_actions": [],
    }
    if intent:
        for t in cap.get("ocr_targets", []):
            if any(k in t["text"].lower() for k in intent.lower().split() if len(k) > 2):
                payload["suggested_actions"].append({"type": "click_text", "target": t["text"], "center": t["center"]})
    if wait_change:
        payload["frame_wait"] = wait_frame_change()
    return payload


def run_powershell(command: str, timeout_sec: int = 60) -> dict[str, Any]:
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command], capture_output=True, text=True, timeout=timeout_sec, encoding="utf-8", errors="replace")
        return {"ok": r.returncode == 0, "returncode": r.returncode, "stdout": (r.stdout or "")[-8000:], "stderr": (r.stderr or "")[-2000:]}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


def run_cmd(command: str, timeout_sec: int = 60) -> dict[str, Any]:
    try:
        r = subprocess.run(["cmd", "/c", command], capture_output=True, text=True, timeout=timeout_sec, encoding="utf-8", errors="replace")
        return {"ok": r.returncode == 0, "returncode": r.returncode, "stdout": (r.stdout or "")[-8000:], "stderr": (r.stderr or "")[-2000:]}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


def load_knowledge_refs() -> list[dict[str, str]]:
    refs = [
        {"name": "Recursive-Control", "url": "https://github.com/flowdevs-io/Recursive-Control", "notes": "Mouse/Keyboard/ScreenCapture/WindowSelection/CMD/PowerShell plugins"},
        {"name": "LOFIN Desktop Control", "path": r"E:\LOFIN-Classical-Dev\03-Desktop-Control\full_screen_brain_control.py"},
        {"name": "QAFusionX Bezier Mouse", "path": r"C:\Users\ThejanaD\QAFusionX\scripts\human_bezier_mouse.py"},
    ]
    doc = KNOWLEDGE_ROOT / "INDEX.json"
    if doc.exists():
        try:
            extra = json.loads(doc.read_text(encoding="utf-8"))
            if isinstance(extra, list):
                refs.extend(extra)
        except Exception:
            pass
    return refs


# --- vendored frame watch + viewport calib ---
_frame_watcher = None

def get_frame_watcher(dest: Path | None = None):
    global _frame_watcher
    from lib.frame_watch import FrameWatcher
    if _frame_watcher is None:
        d = dest or (CAPTURE_ROOT / "frame_watch")
        _frame_watcher = FrameWatcher(d)
    return _frame_watcher


def load_viewport_calib():
    from lib.viewport_store import ViewportCalib
    return ViewportCalib.load()


def save_viewport_calib(origin_x: float, origin_y: float, inner_w: float = 0, inner_h: float = 0, notes: str = ""):
    from lib.viewport_store import ViewportCalib
    c = ViewportCalib(origin_x=origin_x, origin_y=origin_y, inner_w=inner_w, inner_h=inner_h, notes=notes)
    c.save()
    return c


def viewport_click(vx: float, vy: float) -> dict[str, Any]:
    calib = load_viewport_calib()
    if calib is None:
        return {"ok": False, "reason": "viewport_not_calibrated", "hint": "humanize_calibrate_viewport first"}
    sx, sy = calib.to_screen(vx, vy)
    return {"ok": True, "viewport": [vx, vy], "screen": [sx, sy], "click": click_at(sx, sy)}


def device_loop_step(intent: str = "", tag: str = "loop") -> dict[str, Any]:
    """Full EYES->payload for agent brain: capture + windows + OCR + frame delta + calib status."""
    cap = capture_desktop(tag)
    fw = get_frame_watcher()
    fw.capture(tag=tag)
    calib = load_viewport_calib()
    return {
        "law": "EYES->BRAIN->HANDS. Read capture path. Never blind click.",
        "intent": intent,
        "capture": cap,
        "windows": list_windows(35),
        "viewport_calib": {"loaded": calib is not None, "origin": [calib.origin_x, calib.origin_y] if calib else None},
        "frame_changes": len(fw.changes),
        "suggested_actions": [
            {"type": "click_text", "target": t["text"], "center": t["center"]}
            for t in cap.get("ocr_targets", [])[:12]
        ],
    }


def start_presence(name: str = "Theja Humanize Agent") -> dict[str, Any]:
    try:
        from lib.presence import PresenceConfig, start_presence, presence_detail, presence_status
        start_presence(PresenceConfig(name=name, initials="TH"))
        presence_status("watching")
        presence_detail("Full device control active")
        return {"ok": True, "presence": name}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def stop_presence_overlay() -> dict[str, Any]:
    try:
        from lib.presence import stop_presence
        stop_presence()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
