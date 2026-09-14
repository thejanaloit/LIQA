"""LIQA Worker HTTP — headed Hands + health. P0."""
from __future__ import annotations

import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request

from health import headed_health
import hands
import urllib.request

HOST = os.environ.get("LIQA_WORKER_HOST", "127.0.0.1")
PORT = int(os.environ.get("LIQA_WORKER_PORT", "8787"))
TOKEN = os.environ.get("LIQA_WORKER_TOKEN", "")
JOBS_DIR = Path(os.environ.get("LIQA_WORKER_JOBS", Path(__file__).resolve().parent / "jobs"))
CONTROL = os.environ.get("LIQA_CONTROL_URL", "http://127.0.0.1:8788")
CURSOR_API = os.environ.get("CURSOR_API_BASE", "https://api.cursor.com")
GATES_DIR = JOBS_DIR.parent / "gates"
JOBS_DIR.mkdir(parents=True, exist_ok=True)
GATES_DIR.mkdir(parents=True, exist_ok=True)


def _auth(handler: BaseHTTPRequestHandler) -> bool:
    if not TOKEN:
        return True
    return handler.headers.get("Authorization", "") == f"Bearer {TOKEN}"


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    n = int(handler.headers.get("Content-Length") or 0)
    if n <= 0:
        return {}
    return json.loads(handler.rfile.read(n).decode("utf-8") or "{}")


class Handler(BaseHTTPRequestHandler):
    server_version = "LIQA-Worker/0.1"

    def log_message(self, fmt: str, *args) -> None:
        __import__("sys").stderr.write("[liqa-worker] " + (fmt % args) + "\n")

    def _send(self, code: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path in ("/health", "/v1/health"):
            h = headed_health()
            self._send(200 if h["ok"] else 503, h)
            return
        if not _auth(self):
            self._send(401, {"ok": False, "reason": "unauthorized"})
            return
        if self.path in ("/v1/version", "/version"):
            self._send(200, {"ok": True, "product": "LIQA", "component": "worker", "version": "0.1.0"})
            return
        if self.path in ("/v1/status", "/status"):
            h = headed_health()
            self._send(200 if h["ok"] else 503, {**h, "hands": "ready"})
            return
        if self.path in ("/v1/gates", "/gates"):
            items = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(GATES_DIR.glob("*.json"))]
            self._send(200, {"ok": True, "gates": items})
            return
        if self.path.startswith("/v1/jobs/"):
            jid = self.path.rsplit("/", 1)[-1]
            p = JOBS_DIR / f"{jid}.json"
            if not p.exists():
                self._send(404, {"ok": False, "reason": "job not found"})
                return
            self._send(200, json.loads(p.read_text(encoding="utf-8")))
            return
        if self.path in ("/v1/jobs", "/jobs"):
            jobs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(JOBS_DIR.glob("*.json"))]
            self._send(200, {"ok": True, "jobs": jobs[-50:]})
            return
        extra_hit = None
        try:
            import extra as extra_mod

            extra_hit = extra_mod.get(self.path)
        except Exception as e:
            extra_hit = (500, {"ok": False, "reason": str(e)})
        if extra_hit:
            self._send(extra_hit[0], extra_hit[1])
            return
        self._send(404, {"ok": False, "reason": "not found"})

    def do_POST(self) -> None:
        __import__("sys").stderr.write(f"[liqa-worker] POST start {self.path}\n")
        if not _auth(self):
            self._send(401, {"ok": False, "reason": "unauthorized"})
            return
        body = _read_json(self)
        needs_headed = self.path.startswith("/v1/hands/") or self.path in ("/v1/jobs", "/jobs")
        if needs_headed:
            h = headed_health()
            if not h["ok"]:
                self._send(503, {"ok": False, "reason": "worker not headed-ready", "health": h})
                return
        if self.path in ("/v1/hands/screenshot",):
            self._send(200, hands.screenshot(body.get("label") or "liqa"))
            return
        if self.path in ("/v1/hands/click_text",):
            self._send(200, hands.click_text(body.get("text") or ""))
            return
        if self.path in ("/v1/hands/click",):
            self._send(200, hands.click_xy(int(body.get("x") or 0), int(body.get("y") or 0)))
            return
        if self.path in ("/v1/hands/type",):
            self._send(200, hands.type_text(body.get("text") or "", is_secret=bool(body.get("secret"))))
            return
        if self.path in ("/v1/hands/wait",):
            self._send(200, hands.wait_analyzable(float(body.get("seconds") or 1.2)))
            return
        if self.path in ("/v1/hands/wait_frame",):
            self._send(200, hands.wait_frame(float(body.get("timeout") or 15)))
            return
        if self.path in ("/v1/hands/presence",):
            self._send(200, hands.presence())
            return
        if self.path in ("/v1/gates", "/gates"):
            gid = uuid.uuid4().hex[:10]
            gate = {
                "id": gid,
                "kind": body.get("kind") or "captcha",
                "status": "waiting_human",
                "detail": body.get("detail") or "",
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "honesty": "Hard CAPTCHA / SMS / Google 2FA: human completes it. LIQA does not use captcha farms.",
            }
            (GATES_DIR / f"{gid}.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")
            self._send(201, gate)
            return
        if self.path.startswith("/v1/gates/") and self.path.endswith("/ack"):
            gid = self.path.split("/")[3]
            p = GATES_DIR / f"{gid}.json"
            if not p.exists():
                self._send(404, {"ok": False, "reason": "gate not found"})
                return
            g = json.loads(p.read_text(encoding="utf-8"))
            g["status"] = "acked"
            g["ackedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            p.write_text(json.dumps(g, indent=2), encoding="utf-8")
            self._send(200, {"ok": True, **g})
            return
        if self.path in ("/v1/run", "/run"):
            from loop import run_job

            out = run_job(
                body.get("task") or body.get("story") or "",
                url=body.get("url") or "",
                creds=body.get("creds") or None,
            )
            self._send(200 if out.get("ok") else 409, out)
            return
        if self.path in ("/v1/predict", "/predict"):
            import intent as intent_mod

            self._send(200, intent_mod.predict(body.get("task") or body.get("story") or ""))
            return
        if self.path in ("/v1/hands/calibrate",):
            self._send(200, hands.calibrate())
            return
        if self.path in ("/v1/hands/focus",):
            self._send(200, hands.focus_window(body.get("title") or ""))
            return
        if self.path in ("/v1/hands/hotkey",):
            keys = body.get("keys") or ["enter"]
            self._send(200, hands.hotkey(*[str(k) for k in keys]))
            return
        if self.path in ("/v1/poll",):
            import poll as poll_mod

            try:
                self._send(200, {"ok": True, "heartbeat": poll_mod.heartbeat(), "jobs": poll_mod.pull_jobs()})
            except Exception as e:
                self._send(502, {"ok": False, "reason": str(e)})
            return
        if self.path in ("/v1/heartbeat",):
            h = headed_health()
            payload = json.dumps({"id": "local-worker", "headed": h["ok"], "health": h}).encode()
            req = urllib.request.Request(
                f"{CONTROL}/v1/workers/heartbeat",
                data=payload,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    out = json.loads(resp.read().decode())
                self._send(200, {"ok": True, "control": out})
            except Exception as e:
                self._send(502, {"ok": False, "reason": str(e)})
            return
        if self.path in ("/v1/jobs", "/jobs"):
            jid = uuid.uuid4().hex[:12]
            job = {
                "id": jid,
                "ok": True,
                "product": "LIQA",
                "mode": "headed",
                "status": "queued",
                "story": body.get("story") or "",
                "intent": body.get("intent") or "",
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "note": "Queued on headed LIQA Worker. Not headless.",
            }
            (JOBS_DIR / f"{jid}.json").write_text(json.dumps(job, indent=2), encoding="utf-8")
            self._send(201, job)
            return
        if self.path in ("/v1/cursor/dispatch", "/cursor/dispatch"):
            key = os.environ.get("CURSOR_API_KEY", "")
            if not key:
                self._send(400, {"ok": False, "reason": "CURSOR_API_KEY not set"})
                return
            prompt = body.get("prompt") or "Run headed LIQA on this Windows worker. Do not use headless."
            payload = json.dumps({"prompt": {"text": prompt}}).encode("utf-8")
            req = request.Request(
                f"{CURSOR_API}/v1/agents",
                data=payload,
                method="POST",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            )
            try:
                with request.urlopen(req, timeout=30) as resp:
                    out = json.loads(resp.read().decode("utf-8"))
                self._send(
                    200,
                    {
                        "ok": True,
                        "cursor": out,
                        "note": "Dispatcher only — clicks stay on this headed Windows desktop.",
                    },
                )
            except error.HTTPError as e:
                self._send(e.code, {"ok": False, "reason": e.read().decode("utf-8", errors="replace")[:2000]})
            except Exception as e:
                self._send(502, {"ok": False, "reason": str(e)})
            return
        try:
            import extra as extra_mod

            hit = extra_mod.post(self.path, body)
        except Exception as e:
            hit = (500, {"ok": False, "reason": str(e)})
        if hit:
            self._send(hit[0], hit[1])
            return
        self._send(404, {"ok": False, "reason": "not found"})


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"LIQA worker http://{HOST}:{PORT} (headless_allowed=false)")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
