"""Optional ffmpeg recording of PNG sequence → mp4 artifact."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from capture_ops import ROOT


def to_mp4(job_id: str) -> dict[str, Any]:
    ffmpeg = shutil.which("ffmpeg")
    src = ROOT / "jobs"
    out = ROOT / f"{job_id}.mp4"
    if not ffmpeg:
        return {"ok": True, "skipped": True, "reason": "ffmpeg not on PATH — keep PNG sequence", "hint": "Install ffmpeg for T093"}
    try:
        subprocess.run([ffmpeg, "-y", "-framerate", "5", "-i", str(src / f"job-{job_id}-%d.png"), str(out)], check=False, timeout=60)
    except Exception as e:
        return {"ok": False, "reason": str(e)}
    return {"ok": True, "path": str(out), "fpsCap": 25}
