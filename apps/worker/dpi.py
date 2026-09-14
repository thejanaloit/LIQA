"""DPI ScalePlan — map brain coords to physical pixels (computer-use pattern)."""
from __future__ import annotations

from typing import Any


def scale_plan(screen_w: int, screen_h: int, brain_w: int = 1288, brain_h: int = 711) -> dict[str, Any]:
    if screen_w <= 0 or screen_h <= 0:
        return {"ok": False, "reason": "bad_screen"}
    sx = screen_w / float(brain_w)
    sy = screen_h / float(brain_h)
    return {"ok": True, "screen": {"w": screen_w, "h": screen_h}, "brain": {"w": brain_w, "h": brain_h}, "sx": sx, "sy": sy}


def to_screen(x: int, y: int, plan: dict[str, Any]) -> tuple[int, int]:
    return int(x * plan["sx"]), int(y * plan["sy"])


def downscale_box(w: int, h: int, max_w: int = 1288, max_h: int = 711) -> tuple[int, int]:
    if w <= max_w and h <= max_h:
        return w, h
    r = min(max_w / w, max_h / h)
    return max(1, int(w * r)), max(1, int(h * r))
