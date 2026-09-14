"""Mandatory mouse calibration — 4 corners + mid + screenshots.

Owner law:
- Before QA clicks, take ~4–5 screenshots with the cursor parked at known viewport points.
- Measure from the four corners (and centre). Use axes (x/y) + direction to build a
  viewport→screen map so every later move lands on the real control — not a guess.
"""

from __future__ import annotations

import json
import statistics
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    import pyautogui

    pyautogui.FAILSAFE = True
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore


@dataclass
class MouseCalibration:
    """Affine map: screen = origin + scale * viewport_css."""

    origin_x: float
    origin_y: float
    scale_x: float = 1.0
    scale_y: float = 1.0
    inner_w: float = 0.0
    inner_h: float = 0.0
    dpr: float = 1.0
    method: str = "corners4+center"
    samples: list[dict[str, Any]] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    ok: bool = False
    notes: str = ""

    def to_screen(self, vx: float, vy: float) -> tuple[int, int]:
        return (
            int(round(self.origin_x + self.scale_x * vx)),
            int(round(self.origin_y + self.scale_y * vy)),
        )

    def dump(self, path: Path) -> None:
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")


def _dpi_aware() -> None:
    try:
        import ctypes

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        return


def _screen_size() -> tuple[int, int]:
    try:
        import win32api

        return int(win32api.GetSystemMetrics(0)), int(win32api.GetSystemMetrics(1))
    except Exception:
        if pyautogui is not None:
            sz = pyautogui.size()
            return int(sz[0]), int(sz[1])
        return 1920, 1080


def _clamp_screen(x: int, y: int) -> tuple[int, int]:
    sw, sh = _screen_size()
    return min(max(4, x), sw - 5), min(max(4, y), sh - 5)


def _win_metrics(page) -> dict[str, Any]:
    script = """() => {
          const side = Math.max(0, Math.floor((window.outerWidth - window.innerWidth) / 2));
          const top = Math.max(0, Math.floor(window.outerHeight - window.innerHeight - side));
          return {
            screenX: window.screenX,
            screenY: window.screenY,
            outerWidth: window.outerWidth,
            outerHeight: window.outerHeight,
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight,
            dpr: window.devicePixelRatio || 1,
            side,
            top,
            vvOffsetLeft: (window.visualViewport && window.visualViewport.offsetLeft) || 0,
            vvOffsetTop: (window.visualViewport && window.visualViewport.offsetTop) || 0
          };
        }"""
    last_exc: Exception | None = None
    for attempt in range(6):
        try:
            try:
                page.wait_for_load_state("domcontentloaded", timeout=15_000)
            except Exception:
                pass
            return page.evaluate(script)
        except Exception as exc:
            last_exc = exc
            if "destroyed" not in str(exc).lower() and attempt >= 2:
                raise
            time.sleep(0.8 + attempt * 0.3)
    if last_exc:
        raise last_exc
    raise RuntimeError("win_metrics failed without exception")


def _content_origin(m: dict[str, Any]) -> tuple[float, float]:
    """CSS viewport (0,0) → screen pixels (first principles)."""
    ox = float(m["screenX"] + m["side"] + m["vvOffsetLeft"])
    oy = float(m["screenY"] + m["top"] + m["vvOffsetTop"])
    return ox, oy


def _cursor_pos() -> tuple[int, int] | None:
    try:
        import win32api

        return tuple(win32api.GetCursorPos())  # type: ignore[return-value]
    except Exception:
        if pyautogui is not None:
            p = pyautogui.position()
            return int(p[0]), int(p[1])
        return None


def calibrate_mouse(
    page,
    pack_dir: Path,
    *,
    announce: Any | None = None,
    move_visible: Any | None = None,
) -> MouseCalibration:
    """Owner-visible 4-corner + centre calibration with 5 screenshots.

    Method (stable):
      1) Predict content origin from window.screenX/Y + chrome chrome (axes).
      2) Park cursor at TL, TR, BR, BL, C (visible moves along x then y).
      3) Screenshot each park.
      4) Measure cursor − prediction error at each sample.
      5) Apply ONE median origin correction; keep scale≈1 unless TL↔TR / TL↔BL
         distances prove a consistent DPI scale (0.85–1.25 band).
    """
    _dpi_aware()
    out_dir = Path(pack_dir) / "mouse_calib"
    out_dir.mkdir(parents=True, exist_ok=True)

    from fusionx_qa.surface import bring_uat_to_front

    bring_uat_to_front(maximize=True)
    time.sleep(0.4)

    m = _win_metrics(page)
    iw, ih = float(m["innerWidth"]), float(m["innerHeight"])
    ox0, oy0 = _content_origin(m)

    if iw < 200 or ih < 200:
        calib = MouseCalibration(
            origin_x=ox0,
            origin_y=oy0,
            inner_w=iw,
            inner_h=ih,
            dpr=float(m["dpr"]),
            ok=False,
            notes="viewport too small — formula only",
        )
        calib.dump(out_dir / "CALIBRATION.json")
        return calib

    margin = 28.0
    points = [
        ("TL", margin, margin),
        ("TR", iw - margin - 1.0, margin),
        ("BR", iw - margin - 1.0, ih - margin - 1.0),
        ("BL", margin, ih - margin - 1.0),
        ("C", iw / 2.0, ih / 2.0),
    ]

    # Pass-1 predictions: origin + 1:1 CSS pixels
    pred = {name: (ox0 + vx, oy0 + vy) for name, vx, vy in points}

    if announce:
        try:
            announce("CALIBRATE mouse: 4 corners + centre (watch axes)")
        except Exception:
            pass

    prev_failsafe = True
    if pyautogui is not None:
        prev_failsafe = bool(getattr(pyautogui, "FAILSAFE", True))
        pyautogui.FAILSAFE = False

    samples: list[dict[str, Any]] = []
    shots: list[str] = []
    err_x: list[float] = []
    err_y: list[float] = []

    try:
        for idx, (name, vx, vy) in enumerate(points, start=1):
            px, py = pred[name]
            sx, sy = _clamp_screen(int(round(px)), int(round(py)))
            if announce:
                try:
                    announce(f"CALIB {name} axis=({vx:.0f},{vy:.0f}) → screen=({sx},{sy})")
                except Exception:
                    pass
            if move_visible is not None:
                try:
                    move_visible(sx, sy, f"Calibration park at {name} — measure axes")
                except Exception:
                    if pyautogui is not None:
                        pyautogui.moveTo(sx, sy, duration=0.55)
            elif pyautogui is not None:
                pyautogui.moveTo(sx, sy, duration=0.55)
            time.sleep(0.4)

            actual = _cursor_pos()
            shot = out_dir / f"calib_{idx}_{name}.png"
            try:
                if pyautogui is not None:
                    pyautogui.screenshot(str(shot))
                    shots.append(str(shot))
            except Exception:
                pass

            dx = dy = 0.0
            if actual:
                dx = float(actual[0] - sx)
                dy = float(actual[1] - sy)
                # Ignore huge outliers (user grabbed mouse / multi-monitor glitch)
                if abs(dx) < 120 and abs(dy) < 120:
                    err_x.append(dx)
                    err_y.append(dy)

            samples.append(
                {
                    "name": name,
                    "viewport": {"x": vx, "y": vy},
                    "screen_pred": {"x": sx, "y": sy},
                    "cursor_actual": {"x": actual[0], "y": actual[1]} if actual else None,
                    "error_px": {"dx": dx, "dy": dy},
                    "screenshot": str(shot) if shot.exists() else None,
                }
            )
            time.sleep(0.15)
    finally:
        if pyautogui is not None:
            pyautogui.FAILSAFE = prev_failsafe

    # One global origin correction from median error (stable vs per-point nudge)
    corr_x = statistics.median(err_x) if err_x else 0.0
    corr_y = statistics.median(err_y) if err_y else 0.0
    ox = ox0 + corr_x
    oy = oy0 + corr_y

    # Optional DPI scale from TL↔TR (x) and TL↔BL (y) if actual spans are trustworthy
    scale_x = 1.0
    scale_y = 1.0
    by = {s["name"]: s for s in samples}

    def _span_scale(a: str, b: str, axis: str) -> float | None:
        sa, sb = by.get(a), by.get(b)
        if not sa or not sb or not sa.get("cursor_actual") or not sb.get("cursor_actual"):
            return None
        if axis == "x":
            dv = sb["viewport"]["x"] - sa["viewport"]["x"]
            ds = sb["cursor_actual"]["x"] - sa["cursor_actual"]["x"]
        else:
            dv = sb["viewport"]["y"] - sa["viewport"]["y"]
            ds = sb["cursor_actual"]["y"] - sa["cursor_actual"]["y"]
        if abs(dv) < 50:
            return None
        sc = ds / dv
        if 0.85 <= sc <= 1.25:
            return sc
        return None

    sx_meas = _span_scale("TL", "TR", "x")
    sy_meas = _span_scale("TL", "BL", "y")
    if sx_meas is not None:
        scale_x = sx_meas
    if sy_meas is not None:
        scale_y = sy_meas

    # If scale changed, re-derive origin from TL actual so TL still lands
    if by.get("TL") and by["TL"].get("cursor_actual"):
        tl = by["TL"]
        ox = float(tl["cursor_actual"]["x"]) - scale_x * float(tl["viewport"]["x"])
        oy = float(tl["cursor_actual"]["y"]) - scale_y * float(tl["viewport"]["y"])

    calib = MouseCalibration(
        origin_x=ox,
        origin_y=oy,
        scale_x=scale_x,
        scale_y=scale_y,
        inner_w=iw,
        inner_h=ih,
        dpr=float(m["dpr"]),
        method="corners4+center+median_origin",
        samples=samples,
        screenshots=shots,
        ok=True,
        notes=(
            f"origin0=({ox0:.1f},{oy0:.1f}) median_corr=({corr_x:.1f},{corr_y:.1f}) "
            f"scale=({scale_x:.4f},{scale_y:.4f}) samples_ok={len(err_x)}"
        ),
    )
    # Rewrite screen_cmd using final map for evidence
    for s in calib.samples:
        fx, fy = calib.to_screen(s["viewport"]["x"], s["viewport"]["y"])
        s["screen_cmd"] = {"x": fx, "y": fy}

    calib.dump(out_dir / "CALIBRATION.json")
    if announce:
        try:
            announce(
                f"CALIB DONE origin=({ox:.0f},{oy:.0f}) scale=({scale_x:.3f},{scale_y:.3f})"
            )
        except Exception:
            pass
    return calib


def viewport_to_screen_calibrated(
    page,
    x: float,
    y: float,
    calib: MouseCalibration | None = None,
) -> tuple[int, int]:
    if calib and calib.ok:
        return _clamp_screen(*calib.to_screen(x, y))
    m = _win_metrics(page)
    ox, oy = _content_origin(m)
    return _clamp_screen(int(round(ox + x)), int(round(oy + y)))
