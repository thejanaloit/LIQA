"""LIQA Control — jobs, workers, gates, local UI."""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = os.environ.get("LIQA_CONTROL_HOST", "127.0.0.1")
PORT = int(os.environ.get("LIQA_CONTROL_PORT", "8788"))
TOKEN = os.environ.get("LIQA_CONTROL_TOKEN", "")
DATA = Path(os.environ.get("LIQA_CONTROL_DATA", Path(__file__).resolve().parent / "data"))
UI = Path(__file__).resolve().parent / "ui" / "index.html"
for sub in ("jobs", "workers", "tenants", "gates", "audit", "artifacts"):
    (DATA / sub).mkdir(parents=True, exist_ok=True)

_HITS: dict[str, list[float]] = defaultdict(list)
CORS = os.environ.get("LIQA_CORS", "*")


def _audit(action: str, extra: dict | None = None) -> None:
    rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "action": action, **(extra or {})}
    p = DATA / "audit" / f"{int(time.time())}-{action}.json"
    p.write_text(json.dumps(rec, indent=2), encoding="utf-8")


def _rate_ok(ip: str, limit: int = 30, window: float = 60.0) -> bool:
    now = time.time()
    bucket = [t for t in _HITS[ip] if now - t < window]
    bucket.append(now)
    _HITS[ip] = bucket
    return len(bucket) <= limit

HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>LIQA Control — 2QA Ops</title>
<style>
body{font-family:Segoe UI,system-ui,sans-serif;margin:24px;background:#111;color:#eee}
h1{font-size:22px} h2{font-size:16px;margin:0 0 8px;color:#bbb}
a{color:#8ab4ff}
.card{background:#1c1c1c;padding:16px;margin:12px 0;border:1px solid #333}
.ok{color:#6f6}.bad{color:#f66}.warn{color:#fc6}
button{padding:8px 12px;margin:4px 8px 4px 0;cursor:pointer}
input,textarea{width:100%;padding:8px;margin:6px 0;background:#222;color:#eee;border:1px solid #444;box-sizing:border-box}
pre{white-space:pre-wrap;font-size:12px;max-height:280px;overflow:auto}
.grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
.stat{font-size:28px;font-weight:600}
</style></head><body>
<h1>LIQA Control — 2 QA humans console</h1>
<p>Workers execute. You only resolve <b>gates</b> and <b>sign-off</b>. OTP/MFA = Human Gate — never invent codes.</p>
<div class="card grid" id="summary">
  <div><h2>Workers headed</h2><div class="stat" id="sWorkers">…</div></div>
  <div><h2>Gates waiting</h2><div class="stat warn" id="sGates">…</div></div>
  <div><h2>Needs sign-off</h2><div class="stat" id="sSign">…</div></div>
</div>
<div class="card">
  <b>Health</b> Control: <span id="ch">…</span> · Local worker probe: <span id="wh">…</span>
</div>
<div class="card">
  <b>Queue headed job</b>
  <input id="jira" placeholder="Jira KEY e.g. PF-55248">
  <input id="story" placeholder="Story / task text">
  <input id="url" placeholder="Entry URL (loaded once on worker)">
  <button onclick="createJob()">Queue for Worker</button>
</div>
<div class="card">
  <b>Resolve gate (Human 1)</b>
  <input id="gateId" placeholder="Gate id">
  <input id="gateUser" placeholder="Your name" value="qa-gate-lead">
  <input id="gateNote" placeholder="Note e.g. OTP entered / SSO done / account supplied">
  <button onclick="resolveGate()">Resolve gate</button>
</div>
<div class="card">
  <b>Sign-off (Human 2)</b>
  <input id="jobId" placeholder="Job id">
  <input id="signUser" placeholder="Your name" value="qa-signoff-lead">
  <input id="book1" placeholder="Book1 path on worker/share">
  <button onclick="signOff(true)">Sign-off PASS</button>
  <button onclick="signOff(false)">Reject</button>
</div>
<div class="card"><b>Ops summary</b><pre id="ops">loading</pre></div>
<div class="card"><b>Gates</b><pre id="gates">loading</pre></div>
<div class="card"><b>Jobs</b><pre id="jobs">loading</pre></div>
<div class="card"><b>Workers</b><pre id="workers">loading</pre></div>
<script>
async function j(u,opt){const r=await fetch(u,opt);return r.json()}
async function refresh(){
  try{const c=await j('/health'); ch.textContent=c.ok?'OK':'DOWN'; ch.className=c.ok?'ok':'bad'}catch(e){ch.textContent='DOWN';ch.className='bad'}
  try{const w=await j('http://127.0.0.1:8787/health'); wh.textContent=w.ok?'HEADED READY':'NOT HEADED'; wh.className=w.ok?'ok':'bad'}catch(e){wh.textContent='n/a';wh.className='warn'}
  const ops=await j('/v1/ops/summary');
  opsEl=document.getElementById('ops'); opsEl.textContent=JSON.stringify(ops,null,2);
  sWorkers.textContent=ops.workers_headed ?? '—';
  sGates.textContent=ops.gates_waiting ?? '—';
  sSign.textContent=ops.jobs_needs_signoff ?? '—';
  jobs.textContent=JSON.stringify(await j('/v1/jobs'),null,2);
  workers.textContent=JSON.stringify(await j('/v1/workers'),null,2);
  gates.textContent=JSON.stringify(await j('/v1/gates'),null,2);
}
async function createJob(){
  await j('/v1/jobs',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({story:story.value,url:url.value,jiraKey:jira.value,mode:'headed'})});
  refresh();
}
async function resolveGate(){
  const id=gateId.value.trim(); if(!id) return alert('gate id required');
  await j('/v1/gates/'+id+'/resolve',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({user:gateUser.value,note:gateNote.value})});
  refresh();
}
async function signOff(ok){
  const id=jobId.value.trim(); if(!id) return alert('job id required');
  await j('/v1/jobs/'+id+'/signoff',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({user:signUser.value,book1Path:book1.value,pass:ok,note:ok?'accepted':'rejected'})});
  refresh();
}
refresh(); setInterval(refresh,4000);
</script>
</body></html>
"""


def _auth(h: BaseHTTPRequestHandler) -> bool:
    if not TOKEN:
        return True
    return h.headers.get("Authorization", "") == f"Bearer {TOKEN}"


def _read(h: BaseHTTPRequestHandler) -> dict:
    n = int(h.headers.get("Content-Length") or 0)
    if n <= 0:
        return {}
    return json.loads(h.rfile.read(n).decode("utf-8") or "{}")


def _list(folder: str) -> list:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((DATA / folder).glob("*.json"))]


class Handler(BaseHTTPRequestHandler):
    server_version = "LIQA-Control/0.1"

    def log_message(self, fmt: str, *args) -> None:
        __import__("sys").stderr.write("[liqa-control] " + (fmt % args) + "\n")

    def _send(self, code: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", CORS)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _html(self, code: int, text: str) -> None:
        data = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", CORS)
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path in ("/", "/ui", "/index.html"):
            html = UI.read_text(encoding="utf-8") if UI.exists() else HTML
            self._html(200, html)
            return
        if self.path in ("/health", "/v1/health"):
            self._send(200, {"ok": True, "product": "LIQA", "component": "control", "live": True})
            return
        if not _auth(self):
            self._send(401, {"ok": False, "reason": "unauthorized"})
            return
        if self.path in ("/v1/jobs", "/jobs"):
            self._send(200, {"ok": True, "jobs": _list("jobs")[-100:]})
            return
        if self.path.startswith("/v1/jobs/"):
            jid = self.path.rsplit("/", 1)[-1]
            p = DATA / "jobs" / f"{jid}.json"
            if not p.exists():
                self._send(404, {"ok": False, "reason": "job not found"})
                return
            self._send(200, json.loads(p.read_text(encoding="utf-8")))
            return
        if self.path in ("/v1/workers", "/workers"):
            self._send(200, {"ok": True, "workers": _list("workers")})
            return
        if self.path in ("/v1/gates", "/gates"):
            self._send(200, {"ok": True, "gates": _list("gates")})
            return
        if self.path in ("/v1/ops/summary", "/ops/summary"):
            workers = _list("workers")
            jobs = _list("jobs")
            gates = _list("gates")
            waiting = [g for g in gates if g.get("status") in ("waiting_human", "acked")]
            needs = [j for j in jobs if j.get("status") == "needs_signoff"]
            headed = [w for w in workers if w.get("headed")]
            self._send(
                200,
                {
                    "ok": True,
                    "model": "2QA + LIQA execution",
                    "workers_total": len(workers),
                    "workers_headed": len(headed),
                    "gates_waiting": len(waiting),
                    "jobs_queued": len([j for j in jobs if j.get("status") == "queued"]),
                    "jobs_running": len([j for j in jobs if j.get("status") == "running"]),
                    "jobs_needs_signoff": len(needs),
                    "jobs_done": len([j for j in jobs if j.get("status") == "done"]),
                    "waiting_gates": waiting[-20:],
                    "needs_signoff": needs[-20:],
                    "docs": ["docs/OPS-MODEL-2QA.md", "docs/INDUSTRY-PRODUCT.md"],
                },
            )
            return
        if self.path in ("/v1/tenants", "/tenants"):
            tenants = []
            for t in _list("tenants"):
                t = dict(t)
                t.pop("keyHash", None)
                tenants.append(t)
            self._send(200, {"ok": True, "tenants": tenants})
            return
        if self.path in ("/v1/audit", "/audit"):
            self._send(200, {"ok": True, "audit": _list("audit")[-200:]})
            return
        if self.path in ("/metrics", "/v1/metrics"):
            workers = _list("workers")
            jobs = _list("jobs")
            self._send(
                200,
                {
                    "ok": True,
                    "prometheus": f"liqa_jobs {len(jobs)}\nliqa_workers {len(workers)}\n",
                    "durations": [j.get("id") for j in jobs[-20:]],
                },
            )
            return
        if self.path in ("/v1/csrf",):
            import authz

            tok = authz.csrf_token()
            self._send(200, {"ok": True, "csrf": tok, "oidc": authz.OIDC, "roles": authz.ROLES})
            return
        if self.path in ("/v1/i18n",):
            self._send(
                200,
                {
                    "en": {"empty": "No jobs yet. Queue a headed task.", "live": "Live screenshot poll"},
                    "si": {"empty": "තවම jobs නැහැ. Headed task එකක් queue කරන්න.", "live": "සජීවී screenshot poll"},
                },
            )
            return
        if self.path in ("/v1/status-page",):
            self._send(200, {"ok": True, "control": "up", "product": "LIQA"})
            return
        if self.path.startswith("/v1/artifacts/") and "/download" in self.path:
            import crypto_art
            from urllib.parse import parse_qs, urlparse

            u = urlparse(self.path)
            aid = u.path.split("/")[3]
            q = parse_qs(u.query)
            if not crypto_art.verify(aid, (q.get("exp") or [""])[0], (q.get("sig") or [""])[0]):
                self._send(403, {"ok": False, "reason": "bad_or_expired_sig"})
                return
            p = DATA / "artifacts" / f"{aid}.json"
            self._send(200, json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"ok": False})
            return
        if self.path in ("/v1/book1.csv",):
            p = Path(__file__).resolve().parents[2] / "reports" / "book1-latest.csv"
            if not p.exists():
                self._send(404, {"ok": False, "reason": "generate book1 on worker first"})
                return
            data = p.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.send_header("Content-Disposition", "attachment; filename=book1.csv")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self._send(404, {"ok": False, "reason": "not found"})

    def do_POST(self) -> None:
        if not _auth(self):
            self._send(401, {"ok": False, "reason": "unauthorized"})
            return
        ip = self.client_address[0] if getattr(self, "client_address", None) else "local"
        if not _rate_ok(ip):
            self._send(429, {"ok": False, "reason": "rate_limited"})
            return
        body = _read(self)
        if self.path in ("/v1/tenants", "/tenants"):
            tid = uuid.uuid4().hex[:8]
            raw = body.get("apiKey") or uuid.uuid4().hex
            rec = {
                "id": tid,
                "name": body.get("name") or "default",
                "keyHash": hashlib.sha256(raw.encode()).hexdigest(),
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            (DATA / "tenants" / f"{tid}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
            _audit("tenant_create", {"id": tid})
            shown = dict(rec)
            shown.pop("keyHash")
            self._send(201, {"ok": True, **shown, "apiKeyOnce": raw, "note": "Store the apiKey now. Only the hash is kept."})
            return
        if self.path in ("/v1/jobs", "/jobs"):
            jid = uuid.uuid4().hex[:12]
            job = {
                "id": jid,
                "status": "queued",
                "mode": "headed",
                "tenant": body.get("tenant") or "default",
                "jiraKey": body.get("jiraKey") or body.get("key") or "",
                "story": body.get("story") or body.get("task") or "",
                "url": body.get("url") or "",
                "charter": body.get("charter") or body.get("story") or "",
                "telemetryOptIn": os.environ.get("LIQA_TELEMETRY") == "1",
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "note": "Queued. Worker executes; 2QA only gates + sign-off.",
            }
            workers = _list("workers")
            ready = [w for w in workers if w.get("headed")]
            job["assignedWorker"] = ready[0]["id"] if ready else None
            job["assignNote"] = "Assigned to headed-ready worker" if ready else "No headed worker yet — queued"
            (DATA / "jobs" / f"{jid}.json").write_text(json.dumps(job, indent=2), encoding="utf-8")
            _audit("job_create", {"id": jid})
            self._send(201, {"ok": True, **job})
            return
        if self.path.startswith("/v1/jobs/") and self.path.endswith("/cancel"):
            jid = self.path.split("/")[3]
            p = DATA / "jobs" / f"{jid}.json"
            if not p.exists():
                self._send(404, {"ok": False})
                return
            job = json.loads(p.read_text(encoding="utf-8"))
            job["status"] = "cancelled"
            p.write_text(json.dumps(job, indent=2), encoding="utf-8")
            _audit("job_cancel", {"id": jid})
            self._send(200, {"ok": True, **job})
            return
        if self.path in ("/v1/artifacts", "/artifacts"):
            aid = uuid.uuid4().hex[:10]
            rec = {
                "id": aid,
                "kind": body.get("kind") or "png",
                "path": body.get("path") or "",
                "note": "Worker-local path. Bank SKU: pixels stay on worker.",
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            (DATA / "artifacts" / f"{aid}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
            self._send(201, {"ok": True, **rec})
            return
        if self.path in ("/v1/workers/heartbeat", "/workers/heartbeat"):
            wid = body.get("id") or "local-worker"
            rec = {
                "id": wid,
                "headed": bool(body.get("headed")),
                "lastSeen": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "health": body.get("health") or {},
            }
            (DATA / "workers" / f"{wid}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
            self._send(200, {"ok": True, **rec})
            return
        if self.path in ("/v1/gates", "/gates"):
            gid = uuid.uuid4().hex[:10]
            g = {
                "id": gid,
                "kind": body.get("kind") or "captcha",
                "status": "waiting_human",
                "detail": body.get("detail") or "",
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            (DATA / "gates" / f"{gid}.json").write_text(json.dumps(g, indent=2), encoding="utf-8")
            self._send(201, {"ok": True, **g})
            return
        if self.path.startswith("/v1/gates/") and self.path.endswith("/ack"):
            gid = self.path.split("/")[3]
            p = DATA / "gates" / f"{gid}.json"
            if not p.exists():
                self._send(404, {"ok": False})
                return
            g = json.loads(p.read_text(encoding="utf-8"))
            g["status"] = "acked"
            g["ackedBy"] = body.get("user") or "local"
            p.write_text(json.dumps(g, indent=2), encoding="utf-8")
            _audit("gate_ack", {"id": gid, "by": g["ackedBy"]})
            self._send(200, {"ok": True, **g})
            return
        if self.path.startswith("/v1/gates/") and self.path.endswith("/resolve"):
            gid = self.path.split("/")[3]
            p = DATA / "gates" / f"{gid}.json"
            if not p.exists():
                self._send(404, {"ok": False, "reason": "gate not found"})
                return
            g = json.loads(p.read_text(encoding="utf-8"))
            g["status"] = "resolved"
            g["resolvedBy"] = body.get("user") or "qa-gate-lead"
            g["resolveNote"] = body.get("note") or ""
            g["resolvedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            p.write_text(json.dumps(g, indent=2), encoding="utf-8")
            _audit("gate_resolve", {"id": gid, "by": g["resolvedBy"]})
            self._send(200, {"ok": True, **g})
            return
        if self.path.startswith("/v1/jobs/") and self.path.endswith("/needs_signoff"):
            jid = self.path.split("/")[3]
            p = DATA / "jobs" / f"{jid}.json"
            if not p.exists():
                self._send(404, {"ok": False})
                return
            job = json.loads(p.read_text(encoding="utf-8"))
            job["status"] = "needs_signoff"
            job["book1Path"] = body.get("book1Path") or job.get("book1Path") or ""
            job["book1Validate"] = body.get("book1Validate")
            job["honesty"] = body.get("honesty")
            p.write_text(json.dumps(job, indent=2), encoding="utf-8")
            _audit("job_needs_signoff", {"id": jid})
            self._send(200, {"ok": True, **job})
            return
        if self.path.startswith("/v1/jobs/") and self.path.endswith("/signoff"):
            jid = self.path.split("/")[3]
            p = DATA / "jobs" / f"{jid}.json"
            if not p.exists():
                self._send(404, {"ok": False, "reason": "job not found"})
                return
            job = json.loads(p.read_text(encoding="utf-8"))
            passed = bool(body.get("pass", True))
            job["status"] = "done" if passed else "rejected"
            job["signoff"] = {
                "by": body.get("user") or "qa-signoff-lead",
                "pass": passed,
                "book1Path": body.get("book1Path") or job.get("book1Path") or "",
                "note": body.get("note") or "",
                "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            p.write_text(json.dumps(job, indent=2), encoding="utf-8")
            _audit("job_signoff", {"id": jid, "pass": passed, "by": job["signoff"]["by"]})
            self._send(200, {"ok": True, **job})
            return
        if self.path in ("/v1/license",):
            import authz

            self._send(200, authz.license_activate(body.get("key") or ""))
            return
        if self.path in ("/v1/artifacts/sign",):
            import crypto_art

            self._send(200, crypto_art.sign(body.get("id") or "x"))
            return
        self._send(404, {"ok": False, "reason": "not found"})


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"LIQA control http://{HOST}:{PORT}/")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
