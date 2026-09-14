"""Seamless human-like mouse movement on Windows (Bezier + tween + jitter)."""
from __future__ import annotations

import math
import random
import time
from typing import Iterable, Tuple

import pyautogui
import pytweening

Point = Tuple[float, float]

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


def _bezier_points(p0: Point, p1: Point, p2: Point, p3: Point, n: int) -> Iterable[Point]:
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        yield (x, y)


def human_move_to(x: int, y: int, *, duration_sec: float = 0.9, steps: int | None = None) -> None:
    """Move cursor along a Bezier curve with easing — visible on screen."""
    start = pyautogui.position()
    sx, sy = float(start.x), float(start.y)
    dx, dy = float(x), float(y)
    dist = math.hypot(dx - sx, dy - sy)
    n = steps or max(28, min(120, int(dist / 8)))
    cx1 = sx + (dx - sx) * random.uniform(0.15, 0.45) + random.uniform(-40, 40)
    cy1 = sy + (dy - sy) * random.uniform(0.05, 0.35) + random.uniform(-30, 30)
    cx2 = sx + (dx - sx) * random.uniform(0.55, 0.85) + random.uniform(-40, 40)
    cy2 = sy + (dy - sy) * random.uniform(0.65, 0.95) + random.uniform(-30, 30)
    p0, p1, p2, p3 = (sx, sy), (cx1, cy1), (cx2, cy2), (dx, dy)
    t0 = time.perf_counter()
    for i, (px, py) in enumerate(_bezier_points(p0, p1, p2, p3, n)):
        ease = pytweening.easeOutQuad(i / n)
        elapsed = time.perf_counter() - t0
        target_t = duration_sec * ease
        if elapsed < target_t:
            time.sleep(target_t - elapsed)
        jx = px + random.uniform(-0.8, 0.8)
        jy = py + random.uniform(-0.8, 0.8)
        pyautogui.moveTo(int(jx), int(jy), _pause=False)


def human_click(x: int, y: int, **kwargs) -> None:
    human_move_to(x, y, **kwargs)
    time.sleep(random.uniform(0.08, 0.18))
    pyautogui.click()


def human_type(text: str, *, interval: float = 0.04) -> None:
    pyautogui.write(text, interval=interval)


def human_press(*keys: str) -> None:
    pyautogui.hotkey(*keys)
