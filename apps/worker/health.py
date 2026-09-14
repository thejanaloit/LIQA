"""Headed-readiness. Fail closed if this box cannot be watched."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

_CACHE: dict[str, Any] = {"t": 0.0, "v": None}
_TTL_SEC = 8.0

_MANUAL_CANDIDATES = [
    Path(os.environ["MANUAL_QA_HOME"]) / "mcp" if os.environ.get("MANUAL_QA_HOME") else None,
    Path(os.environ["LIQA_HOME"]) / "mcp" if os.environ.get("LIQA_HOME") else None,
    Path(__file__).resolve().parents[2] / "mcp",  # E:\LIQA\mcp
    Path(r"E:\ManualQA-Agent") / "mcp",
    Path(r"E:\QAFusionX\manualQA") / "mcp",
]
for _cand in _MANUAL_CANDIDATES:
    if _cand and _cand.is_dir() and (_cand / "device_core.py").exists():
        if str(_cand) not in sys.path:
            sys.path.insert(0, str(_cand))
        break


def _ps(cmd: str) -> str:
    r = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
        capture_output=True,
        text=True,
        timeout=20,
        encoding="utf-8",
        errors="replace",
    )
    return (r.stdout or "").strip()


def headed_health() -> dict[str, Any]:
    now = time.time()
    cached = _CACHE.get("v")
    if cached is not None and (now - float(_CACHE.get("t") or 0)) < _TTL_SEC:
        return cached
    reasons: list[str] = []
    if os.environ.get("LIQA_HEADED", os.environ.get("QAFUSIONX_HEADED", "1")) == "0":
        reasons.append("headed=0 is rejected")
    if os.environ.get("HUMANIZE_HEADLESS", "").lower() in ("1", "true", "yes"):
        reasons.append("HUMANIZE_HEADLESS is rejected")

    session_id = os.environ.get("SESSIONNAME", "")
    if session_id.upper() in ("SERVICES", "S-0"):
        reasons.append("Session 0 / SERVICES — no interactive desktop")

    logonui = _ps(
        "Get-Process LogonUI -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"
    )
    if logonui:
        reasons.append("LogonUI running — screen is locked or at login")

    dev: dict[str, Any] = {}
    try:
        from device_core import device_status

        dev = device_status()
        size = dev.get("screen_size") or {}
        if int(size.get("width") or 0) < 800 or int(size.get("height") or 0) < 600:
            reasons.append("Display too small or missing — not a headed desktop")
        if int(dev.get("window_count") or 0) < 1:
            reasons.append("No visible windows — desktop session is dead")
    except Exception as e:
        reasons.append(f"device_status failed: {e}")
        dev = {"error": str(e), "hint": "Install ManualQA mcp or set MANUAL_QA_HOME"}

    browsers = _ps(
        r"@('chrome','msedge') | ForEach-Object { Get-Command $_ -ErrorAction SilentlyContinue } | "
        r"Select-Object -ExpandProperty Source"
    )
    chrome_ok = bool(browsers)
    if not chrome_ok:
        for prog in (
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ):
            if Path(prog).exists():
                chrome_ok = True
                browsers = prog
                break
    # Also treat a running chrome/msedge process as present
    if not chrome_ok:
        running = _ps(
            "Get-Process chrome,msedge -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty ProcessName"
        )
        if running:
            chrome_ok = True
            browsers = f"running:{running}"
    warnings: list[str] = []
    if not chrome_ok:
        warnings.append("Chrome/Edge not on PATH — browser jobs will fail until a headed browser is installed")
    elif "running:" in str(browsers) or (browsers and "Program Files" in str(browsers)):
        # installed but maybe not on PATH — OK for headed work
        pass

    out = {
        "ok": not reasons,
        "product": "LIQA",
        "component": "worker",
        "mode": "headed",
        "hybrid": False,
        "headless_allowed": False,
        "session": session_id,
        "browser_on_path": chrome_ok,
        "device": dev,
        "reasons": reasons,
        "warnings": warnings,
    }
    _CACHE["t"] = time.time()
    _CACHE["v"] = out
    return out
