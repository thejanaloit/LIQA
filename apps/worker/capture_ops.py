"""Capture ops: rotation, disk, active monitor, PII, lock as security event."""
from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("LIQA_CAPTURE_ROOT", Path(__file__).resolve().parents[2] / "captures"))
ROOT.mkdir(parents=True, exist_ok=True)
MAX_MB = int(os.environ.get("LIQA_CAPTURE_MAX_MB", "2048"))
PII = ROOT / "README.txt"
if not PII.exists():
    PII.write_text(
        "PII may be in these PNGs. Gitignored. Wipe with scripts/wipe.ps1. Bank SKU: stay on Worker.\n",
        encoding="utf-8",
    )


def disk_ok() -> dict[str, Any]:
    usage = shutil.disk_usage(str(ROOT))
    free_mb = usage.free // (1024 * 1024)
    return {"ok": free_mb > 256, "free_mb": free_mb, "path": str(ROOT)}


def rotate(keep_hours: int = 72) -> dict[str, Any]:
    cutoff = time.time() - keep_hours * 3600
    removed = 0
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".mp4"}:
            try:
                if p.stat().st_mtime < cutoff:
                    p.unlink()
                    removed += 1
            except OSError:
                pass
    size = sum(f.stat().st_size for f in ROOT.rglob("*") if f.is_file())
    if size > MAX_MB * 1024 * 1024:
        files = sorted((f for f in ROOT.rglob("*") if f.is_file()), key=lambda x: x.stat().st_mtime)
        while files and size > MAX_MB * 1024 * 1024:
            f = files.pop(0)
            size -= f.stat().st_size
            f.unlink(missing_ok=True)
            removed += 1
    return {"ok": True, "removed": removed, "disk": disk_ok()}


def active_monitor(device: dict[str, Any]) -> dict[str, Any]:
    mons = device.get("monitors") or []
    cur = device.get("cursor") or {}
    x, y = int(cur.get("x") or 0), int(cur.get("y") or 0)
    for m in mons:
        l, t = int(m.get("left") or 0), int(m.get("top") or 0)
        if l <= x < l + int(m.get("width") or 0) and t <= y < t + int(m.get("height") or 0):
            return {"ok": True, "monitor": m, "rule": "cursor_monitor"}
    return {"ok": True, "monitor": mons[0] if mons else None, "rule": "primary_fallback"}
