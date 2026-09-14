"""Extra engineer tools: SBTM, OTP await, proof crop, revalidate, browser entry, evaluate."""
from __future__ import annotations

import json
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from paths import CAPTURE_ROOT, REPO_ROOT, WORKSPACE


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sbtm_charter(
    task_key: str,
    charter_id: str,
    mission: str,
    risks: str = "",
    duration_min: int = 90,
) -> dict[str, Any]:
    safe = "".join(c for c in task_key if c.isalnum() or c in "-_") or "TASK"
    dest = WORKSPACE / "map" / safe / "sbtm"
    dest.mkdir(parents=True, exist_ok=True)
    cid = "".join(c for c in charter_id if c.isalnum() or c in "-_") or "C1"
    payload = {
        "task_key": safe,
        "charter_id": cid,
        "mission": mission,
        "risks": risks,
        "duration_min": int(duration_min),
        "created_at": _now(),
        "tbs": {"test": [], "bug_candidates": [], "setup_blocked": []},
        "rule": "NO Pass/Fail during map — TBS notes only; verdicts via honesty later",
    }
    path = dest / f"{cid}-charter.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md = dest / f"{cid}-charter.md"
    md.write_text(
        f"# SBTM Charter {cid}\n\n**Task:** {safe}\n**Duration:** {duration_min} min\n\n"
        f"## Mission\n{mission}\n\n## Risks\n{risks or '(none listed)'}\n\n"
        f"## TBS\n- T: …\n- B: …\n- S: …\n",
        encoding="utf-8",
    )
    return {"ok": True, "path": str(path), "md": str(md), "charter": payload}


def revalidate_cycle(
    task_key: str, cycle: int, summary: str, still_honest: bool
) -> dict[str, Any]:
    safe = "".join(c for c in task_key if c.isalnum() or c in "-_") or "TASK"
    dest = WORKSPACE / "reports" / "honesty" / safe
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / "revalidate.json"
    data: dict[str, Any] = {"task_key": safe, "cycles": []}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    entry = {
        "cycle": int(cycle),
        "summary": summary,
        "still_honest": bool(still_honest),
        "at": _now(),
    }
    data.setdefault("cycles", []).append(entry)
    done = [c for c in data["cycles"] if c.get("cycle") in (1, 2, 3) and c.get("still_honest")]
    data["complete"] = len({c["cycle"] for c in done}) >= 3
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "path": str(path),
        "complete": data["complete"],
        "cycles_recorded": len(data["cycles"]),
        "message": "Need 3 honest cycles (1|2|3) to close completion."
        if not data["complete"]
        else "Triple honesty complete.",
    }


FORMAT_REFS = {
    "story_gold": "https://ipaydev.atlassian.net/browse/SSP-42118",
    "test_gold": "https://ipaydev.atlassian.net/browse/SSP-38278",
    "pf_gold": "https://lolcgroupdev.atlassian.net/browse/PF-59194",
    "book1_gold": "artifacts/book1-samples/gold-share-pf58374/PF-58374-Book1-SHARE.xlsx",
}


def seed_format_refs() -> dict[str, Any]:
    dest = WORKSPACE / "knowledgeBase" / "harvest"
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / "format-refs.json"
    path.write_text(json.dumps(FORMAT_REFS, indent=2), encoding="utf-8")
    md = dest / "format-refs.md"
    md.write_text(
        "# Format refs (seed — harvest tone from live Jira)\n\n"
        + "\n".join(f"- **{k}:** {v}" for k, v in FORMAT_REFS.items())
        + "\n",
        encoding="utf-8",
    )
    return {"ok": True, "refs": FORMAT_REFS, "path": str(path), "md": str(md)}


def test_case_template(parent_key: str = "") -> dict[str, Any]:
    key = parent_key or "STORY-KEY"
    template = f"""Title: [Module] [Submodule][Feature][FP] - Validate that <behaviour>.

Affects versions:
Status: Draft
Assignee:
Reporter:
Labels: manual-qa, new
Test Case Type: Functional
Priority: Medium
Parent: {key}
Linked work items: is tested by → {key}

Preconditions:
1. …

Steps:
1. …
2. …

Test Comments:

Expected Result:

Actual Result: (fill during headed execution)
"""
    dest = WORKSPACE / "NewTestCases" / "_templates"
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / "jira-functional-template.md"
    path.write_text(template, encoding="utf-8")
    return {"ok": True, "path": str(path), "template": template, "parent_key": key}


def browser_open(url: str) -> dict[str, Any]:
    """Open entry URL once in default headed browser. After this: mouse-click only."""
    u = (url or "").strip()
    if not u:
        return {"ok": False, "error": "url required"}
    marker = WORKSPACE / "agents" / "browser-entry.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    if marker.exists():
        prev = json.loads(marker.read_text(encoding="utf-8"))
        return {
            "ok": False,
            "error": "entry URL already opened this run — navigate by mouse clicks only",
            "previous": prev,
            "law": "One headed entry load; no page.goto / deep-link reloads after.",
        }
    webbrowser.open(u, new=2)
    payload = {"url": u, "opened_at": _now(), "method": "webbrowser"}
    marker.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {
        "ok": True,
        **payload,
        "next": "Capture screen, then mouse-click only. Do not reopen URL.",
    }


def evaluate_all_phases() -> dict[str, Any]:
    import flow

    st = flow.ensure_workspace()
    results = []
    blocked = False
    for i in range(1, 8):
        phase = st["phases"].get(str(i), {})
        status = phase.get("status", "pending")
        ok = status in ("done", "in_progress", "pending")
        note = ""
        if i > 1:
            prev = st["phases"].get(str(i - 1), {})
            if status == "done" and prev.get("status") != "done":
                ok = False
                blocked = True
                note = f"phase {i} done but {i-1} not done"
        if i in (3, 6) and status == "in_progress" and not (st.get("monitor") or {}).get("ok", True):
            ok = False
            blocked = True
            note = "monitor blocker on live phase"
        results.append({"phase": i, "status": status, "ok": ok, "note": note})
    return {
        "ok": not blocked,
        "blocked": blocked,
        "phases": results,
        "monitor": st.get("monitor"),
        "current_phase": st.get("current_phase"),
    }


def stop_the_line(reason: str) -> dict[str, Any]:
    import flow

    st = flow.ensure_workspace()
    st["monitor"] = {
        "ok": False,
        "blocker": reason or "stop_the_line",
        "last_heartbeat": _now(),
        "stop_the_line": True,
    }
    flow.save_state(st)
    path = WORKSPACE / "agents" / "stop-the-line.json"
    path.write_text(
        json.dumps({"reason": reason, "at": _now()}, indent=2), encoding="utf-8"
    )
    return {"ok": True, "stopped": True, "reason": reason, "path": str(path)}


def proof_crop(
    image_path: str,
    x: int,
    y: int,
    w: int,
    h: int,
    label: str = "proof",
    red_box: bool = True,
) -> dict[str, Any]:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return {"ok": False, "error": "pip install pillow"}
    src = Path(image_path)
    if not src.exists():
        return {"ok": False, "error": f"missing image {image_path}"}
    img = Image.open(src).convert("RGB")
    x2, y2 = max(0, x), max(0, y)
    w2, h2 = max(1, w), max(1, h)
    crop = img.crop((x2, y2, min(img.width, x2 + w2), min(img.height, y2 + h2)))
    if red_box:
        draw = ImageDraw.Draw(crop)
        draw.rectangle([1, 1, crop.width - 2, crop.height - 2], outline=(192, 0, 0), width=4)
    out_dir = WORKSPACE / "reports" / "proof"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = out_dir / f"{label}_{stamp}.png"
    crop.save(out)
    # also copy under captures
    CAPTURE_ROOT.mkdir(parents=True, exist_ok=True)
    return {
        "ok": True,
        "path": str(out),
        "bbox": [x2, y2, w2, h2],
        "size": [crop.width, crop.height],
        "next": "Use path in Book1 Screenshot column and Jira attach.",
    }
