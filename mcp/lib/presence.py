"""Teams-style remote-control presence — win32 overlay (no Tk / no Tcl_AsyncDelete).

Shows a floating badge near the cursor: name + watching|moving|typing|analyzing.
"""

from __future__ import annotations

import atexit
import threading
import time
from dataclasses import dataclass
from typing import Literal

Status = Literal["watching", "moving", "typing", "analyzing", "idle"]

OVERLAY_TITLE = "FUSIONX-QA-PRESENCE"
CLASS_NAME = "FusionXQaPresenceClass"


@dataclass
class PresenceConfig:
    name: str = "Aggressive QA Agent"
    initials: str = "QA"
    accent_rgb: tuple[int, int, int] = (225, 29, 72)  # #E11D48


class PresenceOverlay:
    def __init__(self, cfg: PresenceConfig | None = None) -> None:
        self.cfg = cfg or PresenceConfig()
        self._status: Status = "idle"
        self._detail: str = ""
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._active = False
        self._ready = threading.Event()
        self._hwnd = 0

    @property
    def active(self) -> bool:
        return self._active and not self._stop.is_set()

    def start(self) -> None:
        if self._thread and self._thread.is_alive() and self._active:
            return
        self._stop.clear()
        self._ready.clear()
        self._thread = threading.Thread(target=self._run, name="qa-presence", daemon=True)
        self._thread.start()
        self._ready.wait(timeout=3.0)
        atexit.register(_atexit_stop)

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread and thread.is_alive() and threading.current_thread() is not thread:
            thread.join(timeout=3.0)
        _destroy_hwnds()
        self._active = False
        self._thread = None
        self._hwnd = 0

    def set_status(self, status: Status) -> None:
        self._status = status

    def set_detail(self, detail: str) -> None:
        self._detail = (detail or "").strip()[:90]

    def _label(self) -> str:
        icon = {
            "watching": "watching screen",
            "moving": "moving cursor",
            "typing": "typing...",
            "analyzing": "analyzing frame",
            "idle": "idle",
        }.get(self._status, self._status)
        if self._detail:
            return f"{self.cfg.initials}  NOW: {self._detail}"
        return f"{self.cfg.initials}  {self.cfg.name}  |  {icon}"

    def _run(self) -> None:
        try:
            import win32api
            import win32con
            import win32gui
            import win32ui
        except Exception:
            self._ready.set()
            return

        wc = win32gui.WNDCLASS()
        hinst = win32api.GetModuleHandle(None)
        wc.hInstance = hinst
        wc.lpszClassName = CLASS_NAME
        wc.lpfnWndProc = win32gui.DefWindowProc
        try:
            win32gui.RegisterClass(wc)
        except Exception:
            pass

        width, height = 560, 40
        hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_TOPMOST
            | win32con.WS_EX_TOOLWINDOW
            | win32con.WS_EX_LAYERED
            | win32con.WS_EX_NOACTIVATE,
            CLASS_NAME,
            OVERLAY_TITLE,
            win32con.WS_POPUP,
            80,
            80,
            width,
            height,
            0,
            0,
            hinst,
            None,
        )
        self._hwnd = int(hwnd)
        # opaque-ish
        try:
            win32gui.SetLayeredWindowAttributes(hwnd, 0, 230, win32con.LWA_ALPHA)
        except Exception:
            pass
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
        self._active = True
        self._ready.set()

        accent = self.cfg.accent_rgb
        while not self._stop.is_set():
            try:
                x, y = win32api.GetCursorPos()
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOPMOST,
                    x + 18,
                    y + 22,
                    width,
                    height,
                    win32con.SWP_NOACTIVATE,
                )
                hdc = win32gui.GetDC(hwnd)
                # fill background
                brush = win32gui.CreateSolidBrush(win32api.RGB(15, 23, 42))
                win32gui.FillRect(hdc, (0, 0, width, height), brush)
                win32gui.DeleteObject(brush)
                # accent bar
                brush2 = win32gui.CreateSolidBrush(win32api.RGB(*accent))
                win32gui.FillRect(hdc, (0, 0, 8, height), brush2)
                win32gui.DeleteObject(brush2)
                # text
                win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
                win32gui.SetTextColor(hdc, win32api.RGB(248, 250, 252))
                win32gui.DrawText(
                    hdc,
                    "  " + self._label(),
                    -1,
                    (12, 6, width - 8, height - 4),
                    win32con.DT_LEFT | win32con.DT_VCENTER | win32con.DT_SINGLELINE,
                )
                win32gui.ReleaseDC(hwnd, hdc)
            except Exception:
                pass
            # pump a few messages so HWND stays healthy
            try:
                win32gui.PumpWaitingMessages()
            except Exception:
                pass
            time.sleep(0.05)

        try:
            if hwnd and win32gui.IsWindow(hwnd):
                win32gui.DestroyWindow(hwnd)
        except Exception:
            pass
        self._active = False
        self._hwnd = 0


_GLOBAL: PresenceOverlay | None = None


def _destroy_hwnds() -> None:
    try:
        import win32con
        import win32gui

        targets: list[int] = []

        def _enum(hwnd: int, _extra: object) -> None:
            try:
                title = win32gui.GetWindowText(hwnd) or ""
            except Exception:
                return
            if title == OVERLAY_TITLE:
                targets.append(hwnd)

        win32gui.EnumWindows(_enum, None)
        for hwnd in list(dict.fromkeys(targets)):
            try:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                win32gui.DestroyWindow(hwnd)
            except Exception:
                pass
    except Exception:
        return


def _atexit_stop() -> None:
    global _GLOBAL
    if _GLOBAL is None:
        return
    try:
        _GLOBAL._stop.set()
        _destroy_hwnds()
    except Exception:
        pass


def start_presence(cfg: PresenceConfig | None = None) -> PresenceOverlay:
    global _GLOBAL
    if _GLOBAL and _GLOBAL.active:
        return _GLOBAL
    _GLOBAL = PresenceOverlay(cfg)
    _GLOBAL.start()
    _GLOBAL.set_status("watching")
    return _GLOBAL


def stop_presence() -> None:
    global _GLOBAL
    if _GLOBAL:
        _GLOBAL.stop()
        _GLOBAL = None


def presence_status(status: Status) -> None:
    if _GLOBAL:
        _GLOBAL.set_status(status)


def presence_detail(detail: str) -> None:
    """Owner-visible line: what the agent is doing RIGHT NOW on the laptop."""
    if _GLOBAL:
        _GLOBAL.set_detail(detail)
