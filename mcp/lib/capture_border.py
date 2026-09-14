"""
Shared LIVE capture border — visible on the REAL desktop while agent controls.

When HumanAgent / desktop tools run, a thick colored frame wraps the screen
so the human can SEE that capture/control is active (not only on saved PNGs).

Also annotates saved screenshots with the same border + mouse marker.

Automation: stop_live_border() ALWAYS destroys the overlay HWND (cross-process),
registers atexit on start, and exposes force_stop_live_border() for hooks.
"""
from __future__ import annotations

import atexit
import threading
import time
from contextlib import contextmanager
from typing import Any, Iterator

# Visual identity
BORDER_RGB = (0, 220, 90)       # vivid green — "capturing now"
BORDER_HEX = "#00DC5A"
CURSOR_RGB = (255, 40, 40)      # red mouse marker on captures
RING_RGB = (255, 220, 0)        # yellow ring
BORDER_WIDTH = 16
CURSOR_R = 28
OVERLAY_TITLE = "HUMANAGENT-CAPTURE-BORDER"

_stop = threading.Event()
_thread: threading.Thread | None = None
_active = False
_atexit_registered = False


def is_active() -> bool:
    return _active and not _stop.is_set()


def _destroy_overlay_windows() -> int:
    """Force-close overlay HWND(s) even from another process. Returns count closed."""
    closed = 0
    try:
        import win32con
        import win32gui
    except Exception:
        win32gui = None  # type: ignore
        win32con = None  # type: ignore

    if win32gui is not None:
        targets: list[int] = []

        def _enum(hwnd: int, _extra: object) -> None:
            try:
                title = win32gui.GetWindowText(hwnd) or ""
            except Exception:
                return
            if title == OVERLAY_TITLE or "HUMANAGENT-CAPTURE-BORDER" in title:
                targets.append(hwnd)

        try:
            win32gui.EnumWindows(_enum, None)
        except Exception:
            pass
        hwnd = win32gui.FindWindow(None, OVERLAY_TITLE)
        if hwnd:
            targets.append(hwnd)
        for hwnd in dict.fromkeys(targets):
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                time.sleep(0.05)
                if win32gui.IsWindow(hwnd):
                    win32gui.DestroyWindow(hwnd)
                closed += 1
            except Exception:
                pass
        return closed

    # ctypes fallback (no pywin32)
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    WM_CLOSE = 0x0010
    SW_HIDE = 0
    targets2: list[int] = []
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def cb(hwnd: int, _lparam: int) -> bool:
        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, 512)
        t = buf.value or ""
        if t == OVERLAY_TITLE or "HUMANAGENT-CAPTURE-BORDER" in t:
            targets2.append(hwnd)
        return True

    user32.EnumWindows(EnumWindowsProc(cb), 0)
    hwnd = user32.FindWindowW(None, OVERLAY_TITLE)
    if hwnd:
        targets2.append(hwnd)
    for h in dict.fromkeys(targets2):
        user32.ShowWindow(h, SW_HIDE)
        user32.PostMessageW(h, WM_CLOSE, 0, 0)
        time.sleep(0.05)
        if user32.IsWindow(h):
            user32.DestroyWindow(h)
        closed += 1
    return closed


def start_live_border(label: str = "HumanAgent CAPTURING") -> None:
    """Show green frame on the physical screen for the whole control session."""
    global _thread, _active, _atexit_registered
    if _active and _thread and _thread.is_alive():
        return
    _stop.clear()
    _active = True
    if not _atexit_registered:
        atexit.register(force_stop_live_border)
        _atexit_registered = True

    def _run() -> None:
        global _active
        try:
            import tkinter as tk
            import win32api
            import win32con
            import win32gui
        except Exception as e:
            print(f"[capture_border] overlay unavailable: {e}", flush=True)
            _active = False
            return

        try:
            import pyautogui

            sw, sh = pyautogui.size()
        except Exception:
            sw, sh = 1920, 1080

        root = tk.Tk()
        root.title(OVERLAY_TITLE)
        root.geometry(f"{sw}x{sh}+0+0")
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-transparentcolor", "magenta")
        root.configure(bg="magenta")
        canvas = tk.Canvas(root, width=sw, height=sh, bg="magenta", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        bw = BORDER_WIDTH
        # Full-screen green frame (click-through)
        canvas.create_rectangle(0, 0, sw, bw, fill=BORDER_HEX, outline="")
        canvas.create_rectangle(0, sh - bw, sw, sh, fill=BORDER_HEX, outline="")
        canvas.create_rectangle(0, 0, bw, sh, fill=BORDER_HEX, outline="")
        canvas.create_rectangle(sw - bw, 0, sw, sh, fill=BORDER_HEX, outline="")
        # Top badge — visually obvious
        canvas.create_rectangle(bw, bw, 640, bw + 44, fill=BORDER_HEX, outline="")
        canvas.create_text(
            24,
            bw + 22,
            anchor="w",
            text=f"● LIVE CAPTURE  |  {label}",
            fill="black",
            font=("Segoe UI", 13, "bold"),
        )
        # Bottom-right badge
        canvas.create_rectangle(sw - 320, sh - bw - 36, sw - bw, sh - bw, fill=BORDER_HEX, outline="")
        canvas.create_text(
            sw - 300,
            sh - bw - 18,
            anchor="w",
            text="HumanAgent ON",
            fill="black",
            font=("Segoe UI", 11, "bold"),
        )

        cursor_ids: list[int] = []

        def tick() -> None:
            if _stop.is_set():
                try:
                    root.destroy()
                except Exception:
                    pass
                return
            for i in cursor_ids:
                canvas.delete(i)
            cursor_ids.clear()
            try:
                x, y = win32api.GetCursorPos()
            except Exception:
                x, y = sw // 2, sh // 2
            r = CURSOR_R
            cursor_ids.append(
                canvas.create_oval(x - r - 5, y - r - 5, x + r + 5, y + r + 5, outline="#FFDC00", width=5)
            )
            cursor_ids.append(
                canvas.create_oval(x - r, y - r, x + r, y + r, outline="#FF2828", width=4)
            )
            cursor_ids.append(canvas.create_line(x - r - 10, y, x + r + 10, y, fill="#FF2828", width=3))
            cursor_ids.append(canvas.create_line(x, y - r - 10, x, y + r + 10, fill="#FF2828", width=3))
            root.after(33, tick)

        root.update()
        hwnd = win32gui.FindWindow(None, OVERLAY_TITLE)
        if hwnd:
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(
                hwnd,
                win32con.GWL_EXSTYLE,
                style
                | win32con.WS_EX_LAYERED
                | win32con.WS_EX_TRANSPARENT
                | win32con.WS_EX_TOPMOST
                | win32con.WS_EX_TOOLWINDOW,
            )
        tick()
        try:
            root.mainloop()
        finally:
            _active = False
            # belt-and-suspenders if mainloop exits without stop flag
            try:
                _destroy_overlay_windows()
            except Exception:
                pass

    _thread = threading.Thread(target=_run, daemon=True, name="HumanAgentCaptureBorder")
    _thread.start()
    time.sleep(0.7)


def stop_live_border() -> None:
    """Signal in-process overlay thread to exit, then force-destroy any leftover HWND."""
    global _active
    _stop.set()
    _active = False
    time.sleep(0.35)
    _destroy_overlay_windows()


def force_stop_live_border() -> dict[str, Any]:
    """Idempotent cleanup for hooks / CLI / MCP — safe from any process."""
    stop_live_border()
    closed = _destroy_overlay_windows()
    return {"ok": True, "closed": closed, "overlay": OVERLAY_TITLE}


@contextmanager
def live_capture_session(label: str = "HumanAgent CAPTURING") -> Iterator[None]:
    """Use around any live GUI control block — always removes frame on exit."""
    start_live_border(label)
    try:
        yield
    finally:
        force_stop_live_border()


def annotate_capture(img: Any, label: str, tool: str = "HumanAgent") -> Any:
    """Draw border + mouse marker onto a PIL Image (saved proof)."""
    from PIL import ImageDraw
    import pyautogui

    out = img.copy().convert("RGB")
    d = ImageDraw.Draw(out)
    w, h = out.size
    for i in range(BORDER_WIDTH):
        d.rectangle([i, i, w - 1 - i, h - 1 - i], outline=BORDER_RGB)
    d.rectangle([0, 0, 620, 44], fill=BORDER_RGB)
    d.text((14, 12), f"● LIVE CAPTURE | {tool} | {label}", fill=(0, 0, 0))
    x, y = pyautogui.position()
    x, y = max(0, min(w - 1, x)), max(0, min(h - 1, y))
    r = CURSOR_R
    d.ellipse([x - r - 6, y - r - 6, x + r + 6, y + r + 6], outline=RING_RGB, width=5)
    d.ellipse([x - r, y - r, x + r, y + r], outline=CURSOR_RGB, width=4)
    d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=CURSOR_RGB)
    d.line([x - r - 10, y, x + r + 10, y], fill=CURSOR_RGB, width=3)
    d.line([x, y - r - 10, x, y + r + 10], fill=CURSOR_RGB, width=3)
    d.text((x + r + 10, y - 10), "MOUSE", fill=CURSOR_RGB)
    # bottom strip
    d.rectangle([0, h - 28, w, h], fill=BORDER_RGB)
    d.text((14, h - 22), "CAPTURING — green frame = agent control active", fill=(0, 0, 0))
    return out


if __name__ == "__main__":
    import json
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "stop").lower()
    if cmd in ("stop", "force", "off", "end"):
        print(json.dumps(force_stop_live_border()))
        raise SystemExit(0)
    if cmd == "start":
        start_live_border(sys.argv[2] if len(sys.argv) > 2 else "HumanAgent CAPTURING")
        print(json.dumps({"ok": True, "started": True}))
        raise SystemExit(0)
    print(json.dumps({"ok": False, "error": "use: stop|start"}))
    raise SystemExit(2)
