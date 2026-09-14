"""Extra Worker HTTP routes so api.py stays small."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import book1
import capture_ops
import dpi
import hands
import jira_client
import live
import metrics
import packs
import trajectory
from health import headed_health


def get(path: str) -> tuple[int, dict[str, Any]] | None:
    if path in ("/metrics", "/v1/metrics"):
        return 200, {"ok": True, "text": metrics.prometheus(), "alerts": metrics.alerts()}
    if path in ("/v1/live/frame", "/live/frame"):
        metrics.note_health()
        return 200, live.frame()
    if path in ("/v1/live/webrtc",):
        return 200, live.webrtc_notes()
    if path in ("/v1/packs",):
        return 200, {"ok": True, "packs": packs.list_packs(), "istqb": packs.load()}
    if path in ("/v1/book1",):
        return 200, book1.validate_book1()
    if path in ("/v1/dpi",):
        st = headed_health().get("device") or {}
        size = st.get("screen_size") or {}
        return 200, dpi.scale_plan(int(size.get("width") or 1920), int(size.get("height") or 1080))
    if path in ("/v1/capture/disk",):
        return 200, capture_ops.disk_ok()
    if path in ("/v1/jira/oauth",):
        return 200, jira_client.OAUTH
    return None


def post(path: str, body: dict) -> tuple[int, dict[str, Any]] | None:
    if path in ("/v1/hands/scroll",):
        return 200, hands.scroll(int(body.get("clicks") or -3))
    if path in ("/v1/hands/start_menu",):
        return 200, hands.start_menu_search(body.get("query") or "notepad")
    if path in ("/v1/hands/ime",):
        return 200, hands.type_ime(body.get("text") or "", sinhala=bool(body.get("sinhala")))
    if path in ("/v1/book1/generate",):
        return 200, book1.generate_book1(body.get("story") or "LIQA", int(body.get("n") or 110))
    if path in ("/v1/ipay/generate",):
        return 200, book1.generate_ipay(body.get("story") or "LIQA", int(body.get("n") or 110))
    if path in ("/v1/capture/rotate",):
        return 200, capture_ops.rotate()
    if path in ("/v1/jira/assigned",):
        return 200, jira_client.pull_assigned(body.get("jql") or "")
    if path in ("/v1/jira/xray",):
        return 200, jira_client.pull_xray_readonly(body.get("issue") or "")
    if path in ("/v1/trajectory/replay",):
        return 200, trajectory.replay_plan(body.get("jobId") or "")
    if path in ("/v1/cursor/status",):
        jid = body.get("jobId") or ""
        p = Path(__file__).resolve().parent / "jobs" / f"{jid}.json"
        st = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        mapped = {"queued": "queued", "RUNNING": "STEPPED", "FINISHED": "DONE", "ERROR": "FAILED"}.get(
            str(body.get("cursorStatus") or st.get("status") or ""), "queued"
        )
        return 200, {"ok": True, "liqaStatus": mapped, "note": "Cursor is dispatcher only."}
    if path in ("/v1/wipe",):
        root = Path(__file__).resolve().parents[2]
        n = 0
        for folder in ("captures", "trajectories"):
            d = root / folder
            if d.exists():
                for f in d.rglob("*"):
                    if f.is_file() and f.name != "README.txt":
                        f.unlink()
                        n += 1
        return 200, {"ok": True, "removed": n}
    if path in ("/v1/demo/notepad",):
        r = hands.start_menu_search("notepad")
        hands.wait_analyzable(1.0)
        t = hands.type_text("hello from LIQA")
        s = hands.screenshot("demo-notepad")
        return 200, {"ok": True, "start": r, "typed": t, "shot": s}
    if path in ("/v1/cycle20", "/v1/cycle", "/cycle20"):
        import cycle as cycle_mod

        rounds = int(body.get("rounds") or 20)
        out = cycle_mod.run_cycle(
            body.get("task") or body.get("story") or "",
            rounds=min(20, max(1, rounds)),
            eyes=body.get("eyes", True),
            use_hands=bool(body.get("hands")),
        )
        return 200 if out.get("ok") else 409, out
    if path in ("/v1/cycle/tick", "/cycle/tick"):
        import cycle as cycle_mod
        import traceback

        rnd = int(body.get("round") or 1)
        ocr = body.get("ocr")
        try:
            rec = cycle_mod.tick(
                body.get("task") or body.get("story") or "",
                rnd,
                rounds=int(body.get("rounds") or 20),
                eyes=body.get("eyes", True),
                use_hands=bool(body.get("hands")),
                ocr=bool(ocr) if ocr is not None else False,
            )
        except Exception as e:
            return 500, {"ok": False, "reason": str(e), "trace": traceback.format_exc()[-1500:]}
        return 200, rec
    return None
