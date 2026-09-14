"""Persist viewport CSS -> screen pixel map for embedded browser panels."""
from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT = Path(r"E:/ThejaUltimate/gateways/humanize-mcp/data/viewport_calib.json")

@dataclass
class ViewportCalib:
    origin_x: float
    origin_y: float
    scale_x: float = 1.0
    scale_y: float = 1.0
    inner_w: float = 0.0
    inner_h: float = 0.0
    notes: str = ""

    def to_screen(self, vx: float, vy: float) -> tuple[int, int]:
        return (
            int(round(self.origin_x + self.scale_x * vx)),
            int(round(self.origin_y + self.scale_y * vy)),
        )

    def save(self, path: Path = DEFAULT) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path = DEFAULT) -> "ViewportCalib | None":
        if not path.exists():
            return None
        d = json.loads(path.read_text(encoding="utf-8"))
        return cls(**d)
