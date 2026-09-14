"""Frame capture + change detection + component analysis.

Like a remote-control watcher: continuously look at the screen, detect
frame motion, then analyze every changed region/component aggressively.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class FrameChange:
    index: int
    changed_ratio: float
    bbox: tuple[int, int, int, int] | None
    components: list[dict[str, Any]] = field(default_factory=list)
    path: str = ""
    findings: list[str] = field(default_factory=list)


class FrameWatcher:
    def __init__(self, dest: Path, *, interval_s: float = 0.55, threshold: float = 0.012) -> None:
        self.dest = Path(dest)
        self.dest.mkdir(parents=True, exist_ok=True)
        self.interval_s = interval_s
        self.threshold = threshold
        self._prev = None
        self._idx = 0
        self.changes: list[FrameChange] = []
        self.frames_dir = self.dest / "frames"
        self.frames_dir.mkdir(exist_ok=True)

    def capture(self, *, tag: str = "") -> Path | None:
        try:
            import pyautogui
            from PIL import ImageChops, ImageStat
        except Exception:
            return None
        shot = pyautogui.screenshot()
        path = self.frames_dir / f"f{self._idx:05d}{('_' + tag) if tag else ''}.png"
        shot.save(path)
        finding = FrameChange(index=self._idx, changed_ratio=0.0, bbox=None, path=str(path))
        if self._prev is not None:
            diff = ImageChops.difference(self._prev.convert("RGB"), shot.convert("RGB"))
            stat = ImageStat.Stat(diff)
            # mean channel / 255 ≈ change intensity
            mean = sum(stat.mean) / (len(stat.mean) * 255.0)
            finding.changed_ratio = round(mean, 5)
            if mean >= self.threshold:
                bbox = diff.getbbox()
                finding.bbox = bbox
                finding.components = self._analyze_region(shot, bbox)
                finding.findings = self._aggressive_findings(finding.components, mean)
                self.changes.append(finding)
        self._prev = shot
        self._idx += 1
        return path

    def _analyze_region(self, image, bbox: tuple[int, int, int, int] | None) -> list[dict[str, Any]]:
        if not bbox:
            return []
        x0, y0, x1, y1 = bbox
        w, h = max(1, x1 - x0), max(1, y1 - y0)
        crop = image.crop(bbox)
        # coarse grid components inside changed bbox
        comps: list[dict[str, Any]] = []
        gx, gy = 3, 3
        cw, ch = max(1, w // gx), max(1, h // gy)
        try:
            from PIL import ImageStat
        except Exception:
            return [{"bbox": bbox, "area": w * h}]
        for iy in range(gy):
            for ix in range(gx):
                cx0 = x0 + ix * cw
                cy0 = y0 + iy * ch
                cx1 = min(x1, cx0 + cw)
                cy1 = min(y1, cy0 + ch)
                cell = image.crop((cx0, cy0, cx1, cy1))
                st = ImageStat.Stat(cell.convert("L"))
                comps.append(
                    {
                        "cell": f"{ix},{iy}",
                        "bbox": [cx0, cy0, cx1, cy1],
                        "mean_luma": round(st.mean[0], 2),
                        "stdev": round(st.stddev[0], 2),
                        "area": (cx1 - cx0) * (cy1 - cy0),
                    }
                )
        # also record whole region
        comps.insert(
            0,
            {
                "cell": "full",
                "bbox": list(bbox),
                "area": w * h,
                "mean_luma": round(ImageStat.Stat(crop.convert("L")).mean[0], 2),
            },
        )
        return comps

    def _aggressive_findings(self, components: list[dict[str, Any]], mean: float) -> list[str]:
        out: list[str] = []
        if mean > 0.08:
            out.append("LARGE_VISUAL_JUMP — possible unintended layout shift / flash")
        for c in components:
            if c.get("cell") == "full":
                continue
            # very dark or very bright flash cells
            luma = float(c.get("mean_luma") or 0)
            if luma < 8:
                out.append(f"NEAR_BLACK_CELL {c.get('cell')} — possible missing asset / cover")
            if luma > 248:
                out.append(f"NEAR_WHITE_FLASH {c.get('cell')} — possible blank panel")
            if float(c.get("stdev") or 0) < 1.5 and int(c.get("area") or 0) > 40_000:
                out.append(f"FLAT_REGION {c.get('cell')} — large empty / broken panel risk")
        return out

    def flush(self) -> dict[str, Any]:
        payload = {
            "frames": self._idx,
            "changes": [asdict(c) for c in self.changes],
            "aggressive_findings": [f for c in self.changes for f in c.findings],
            "fail_tiny_bugs": True,
        }
        (self.dest / "FRAME_WATCH.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def poll_while(self, seconds: float, *, tag: str = "watch") -> dict[str, Any]:
        end = time.time() + seconds
        while time.time() < end:
            self.capture(tag=tag)
            time.sleep(self.interval_s)
        return self.flush()
