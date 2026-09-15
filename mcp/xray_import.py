"""Xray Cloud Manual-step importer for LIQA (Sigiri PF-59194 shape).

Uses Xray Cloud REST auth + GraphQL:
  POST /api/v2/authenticate  → Bearer token
  GraphQL removeAllTestSteps + addTestStep

Credentials (never commit):
  Env: XRAY_CLIENT_ID, XRAY_CLIENT_SECRET
  Or file: <LIQA_HOME>/secrets/xray.env
  Optional: XRAY_BASE_URL (default https://xray.cloud.getxray.app)

Create API keys in Jira: Apps → Xray → Global Settings → API Keys.
"""
from __future__ import annotations

import csv
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from paths import REPO_ROOT, SECRETS, WORKSPACE

try:
    import sigiri_xray_contract as sigiri
except ImportError:  # pragma: no cover
    sigiri = None  # type: ignore

DEFAULT_BASE = "https://xray.cloud.getxray.app"
TOKEN_CACHE = SECRETS / ".xray_token_cache.json"
ENV_FILE = SECRETS / "xray.env"
ENV_EXAMPLE = SECRETS / "xray.env.example"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def load_credentials() -> dict[str, Any]:
    file_vals = _read_env_file(ENV_FILE)
    client_id = (
        os.environ.get("XRAY_CLIENT_ID")
        or file_vals.get("XRAY_CLIENT_ID")
        or ""
    ).strip()
    client_secret = (
        os.environ.get("XRAY_CLIENT_SECRET")
        or file_vals.get("XRAY_CLIENT_SECRET")
        or ""
    ).strip()
    base = (
        os.environ.get("XRAY_BASE_URL")
        or file_vals.get("XRAY_BASE_URL")
        or DEFAULT_BASE
    ).strip().rstrip("/")
    return {
        "ok": bool(client_id and client_secret),
        "client_id_set": bool(client_id),
        "client_secret_set": bool(client_secret),
        "client_id": client_id,
        "client_secret": client_secret,
        "base_url": base,
        "env_file": str(ENV_FILE),
        "source": "env" if os.environ.get("XRAY_CLIENT_ID") else ("file" if client_id else "none"),
    }


def credentials_status() -> dict[str, Any]:
    c = load_credentials()
    return {
        "ok": c["ok"],
        "client_id_set": c["client_id_set"],
        "client_secret_set": c["client_secret_set"],
        "base_url": c["base_url"],
        "env_file": c["env_file"],
        "source": c["source"],
        "example_file": str(ENV_EXAMPLE),
        "setup": [
            "Jira → Apps → Xray → Global Settings (or Xray Settings) → API Keys",
            "Create API Key → copy Client Id + Client Secret",
            f"Save to {ENV_FILE} as XRAY_CLIENT_ID=... and XRAY_CLIENT_SECRET=...",
            "Or set env vars XRAY_CLIENT_ID / XRAY_CLIENT_SECRET for the LIQA MCP process",
            "Then call liqa_xray_import_steps / liqa_xray_import_csv",
        ],
        "message": "Xray API ready"
        if c["ok"]
        else "BLOCKED: Xray API keys missing — cannot push Manual steps until configured.",
    }


def save_credentials(client_id: str, client_secret: str, base_url: str = "") -> dict[str, Any]:
    """Write secrets/xray.env (gitignored). Does not echo secrets back."""
    cid = (client_id or "").strip()
    sec = (client_secret or "").strip()
    if not cid or not sec:
        return {"ok": False, "error": "client_id and client_secret required"}
    SECRETS.mkdir(parents=True, exist_ok=True)
    base = (base_url or DEFAULT_BASE).strip().rstrip("/")
    ENV_FILE.write_text(
        "\n".join(
            [
                "# LIQA Xray Cloud API keys — DO NOT COMMIT",
                f"XRAY_CLIENT_ID={cid}",
                f"XRAY_CLIENT_SECRET={sec}",
                f"XRAY_BASE_URL={base}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    if TOKEN_CACHE.exists():
        TOKEN_CACHE.unlink()
    # Ensure example exists without secrets
    if not ENV_EXAMPLE.exists():
        ENV_EXAMPLE.write_text(
            "\n".join(
                [
                    "# Copy to xray.env and fill real values",
                    "XRAY_CLIENT_ID=",
                    "XRAY_CLIENT_SECRET=",
                    f"XRAY_BASE_URL={DEFAULT_BASE}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    return {
        "ok": True,
        "saved": str(ENV_FILE),
        "client_id_set": True,
        "client_secret_set": True,
        "base_url": base,
        "note": "Credentials saved. Secrets not returned. Call liqa_xray_import_csv next.",
    }


def _http_json(
    url: str,
    *,
    method: str = "POST",
    headers: dict[str, str] | None = None,
    body: Any = None,
    timeout: int = 60,
) -> tuple[int, Any]:
    data = None
    hdrs = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            code = resp.getcode()
            if not raw:
                return code, None
            # authenticate returns a JSON string token
            try:
                return code, json.loads(raw)
            except json.JSONDecodeError:
                return code, raw.strip().strip('"')
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(err_body)
        except json.JSONDecodeError:
            parsed = err_body
        return e.code, {"error": True, "status": e.code, "body": parsed}
    except Exception as e:  # noqa: BLE001
        return 0, {"error": True, "status": 0, "body": str(e)}


def authenticate(force: bool = False) -> dict[str, Any]:
    creds = load_credentials()
    if not creds["ok"]:
        return {**credentials_status(), "ok": False, "token": None}

    if not force and TOKEN_CACHE.exists():
        try:
            cached = json.loads(TOKEN_CACHE.read_text(encoding="utf-8"))
            # token lasts 24h — refresh if older than 20h
            age = time.time() - float(cached.get("at_epoch", 0))
            if cached.get("token") and age < 20 * 3600:
                return {
                    "ok": True,
                    "token": cached["token"],
                    "cached": True,
                    "base_url": creds["base_url"],
                }
        except Exception:  # noqa: BLE001
            pass

    url = f"{creds['base_url']}/api/v2/authenticate"
    code, payload = _http_json(
        url,
        body={"client_id": creds["client_id"], "client_secret": creds["client_secret"]},
    )
    if code != 200 or not payload or (isinstance(payload, dict) and payload.get("error")):
        return {
            "ok": False,
            "error": "Xray authenticate failed",
            "status": code,
            "detail": payload,
            "hint": "Check Client Id/Secret in Apps → Xray → API Keys",
        }
    token = payload if isinstance(payload, str) else str(payload)
    SECRETS.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE.write_text(
        json.dumps({"token": token, "at_epoch": time.time(), "at": _now()}, indent=2),
        encoding="utf-8",
    )
    return {"ok": True, "token": token, "cached": False, "base_url": creds["base_url"]}


def graphql(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    auth = authenticate()
    if not auth.get("ok"):
        return auth
    url = f"{auth['base_url']}/api/v2/graphql"
    body: dict[str, Any] = {"query": query}
    if variables is not None:
        body["variables"] = variables
    code, payload = _http_json(
        url,
        headers={"Authorization": f"Bearer {auth['token']}"},
        body=body,
    )
    if code != 200 or not isinstance(payload, dict):
        return {"ok": False, "error": "GraphQL HTTP failure", "status": code, "detail": payload}
    if payload.get("errors"):
        return {"ok": False, "error": "GraphQL errors", "errors": payload["errors"], "data": payload.get("data")}
    return {"ok": True, "data": payload.get("data")}


def resolve_issue_id(issue_key: str) -> dict[str, Any]:
    key = (issue_key or "").strip().upper()
    if not re.match(r"^[A-Z][A-Z0-9]+-\d+$", key):
        return {"ok": False, "error": f"invalid issue key: {issue_key}"}
    # Escape quotes in JQL
    q = f"""
    query {{
      getTests(jql: "key = {key}", limit: 1) {{
        total
        results {{
          issueId
          jira(fields: ["key", "summary"])
          testType {{ name }}
          steps {{
            id
            action
            data
            result
          }}
        }}
      }}
    }}
    """
    res = graphql(q)
    if not res.get("ok"):
        return res
    results = (((res.get("data") or {}).get("getTests") or {}).get("results")) or []
    if not results:
        return {"ok": False, "error": f"No Xray Test found for {key} (wrong type or no access)"}
    t = results[0]
    return {
        "ok": True,
        "issue_key": key,
        "issue_id": t.get("issueId"),
        "summary": (t.get("jira") or {}).get("summary"),
        "test_type": (t.get("testType") or {}).get("name"),
        "existing_steps": len(t.get("steps") or []),
        "steps_preview": (t.get("steps") or [])[:3],
    }


def _escape_gql_string(s: str) -> str:
    return (
        (s or "")
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "")
    )


def ensure_manual_type(issue_id: str) -> dict[str, Any]:
    q = f'''
    mutation {{
      updateTestType(issueId: "{_escape_gql_string(issue_id)}", testType: {{ name: "Manual" }}) {{
        issueId
        testType {{ name }}
      }}
    }}
    '''
    return graphql(q)


def remove_all_steps(issue_id: str) -> dict[str, Any]:
    q = f'''
    mutation {{
      removeAllTestSteps(issueId: "{_escape_gql_string(issue_id)}")
    }}
    '''
    return graphql(q)


def add_step(issue_id: str, action: str, data: str, result: str) -> dict[str, Any]:
    step_fields = [
        f'action: "{_escape_gql_string(action)}"',
        f'result: "{_escape_gql_string(result)}"',
    ]
    if data:
        step_fields.insert(1, f'data: "{_escape_gql_string(data)}"')
    step_body = ", ".join(step_fields)
    q = (
        "mutation { addTestStep(issueId: \""
        + _escape_gql_string(issue_id)
        + "\", step: {"
        + step_body
        + "}) { id action data result } }"
    )
    return graphql(q)


def _normalize_steps(steps: list[dict[str, Any]] | str) -> dict[str, Any]:
    if sigiri is None:
        # minimal local normalize
        if isinstance(steps, str):
            steps = json.loads(steps)
        out = []
        for s in steps:
            out.append(
                {
                    "Action": str(s.get("Action") or s.get("action") or "").strip(),
                    "Data": str(s.get("Data") if s.get("Data") is not None else s.get("data") or "").strip(),
                    "Expected Result": str(
                        s.get("Expected Result") or s.get("result") or s.get("expected") or ""
                    ).strip(),
                }
            )
        return {"ok": True, "steps": out, "step_count": len(out)}
    return sigiri.validate_steps(steps)


def import_steps(
    issue_key: str,
    steps_json: str,
    *,
    replace: bool = True,
    require_manual: bool = True,
) -> dict[str, Any]:
    """Validate Sigiri steps then push to Xray Manual table on existing Test."""
    gate = _normalize_steps(steps_json)
    if not gate.get("ok"):
        return {
            "ok": False,
            "blocked": True,
            "stop_upload": True,
            "error": "Sigiri guard failed — fix steps before import",
            "reasons": gate.get("reasons", []),
        }

    resolved = resolve_issue_id(issue_key)
    if not resolved.get("ok"):
        return resolved

    issue_id = str(resolved["issue_id"])
    log: list[dict[str, Any]] = []

    if require_manual:
        mt = ensure_manual_type(issue_id)
        log.append({"op": "updateTestType", "ok": mt.get("ok"), "detail": mt if not mt.get("ok") else "Manual"})
        if not mt.get("ok"):
            # Non-fatal if already Manual — continue unless hard error
            pass

    if replace:
        rm = remove_all_steps(issue_id)
        log.append({"op": "removeAllTestSteps", "ok": rm.get("ok"), "detail": rm if not rm.get("ok") else "cleared"})
        if not rm.get("ok"):
            return {
                "ok": False,
                "error": "Failed to clear existing steps",
                "resolve": resolved,
                "log": log,
                "detail": rm,
            }

    added = 0
    failures: list[dict[str, Any]] = []
    for i, s in enumerate(gate["steps"], start=1):
        r = add_step(issue_id, s["Action"], s.get("Data") or "", s["Expected Result"])
        if r.get("ok"):
            added += 1
        else:
            failures.append({"step": i, "action": s["Action"][:80], "error": r})
            # stop early on auth/schema failures
            if i == 1:
                return {
                    "ok": False,
                    "error": "addTestStep failed on first step",
                    "resolve": resolved,
                    "log": log,
                    "failures": failures,
                }

    # verify
    verify = resolve_issue_id(issue_key)
    dest = WORKSPACE / "NewTestCases" / issue_key.replace("/", "-") / "sigiri-manual"
    dest.mkdir(parents=True, exist_ok=True)
    report = {
        "ok": added == len(gate["steps"]) and not failures,
        "issue_key": issue_key.upper(),
        "issue_id": issue_id,
        "url": f"https://lolcgroupdev.atlassian.net/browse/{issue_key.upper()}",
        "steps_requested": len(gate["steps"]),
        "steps_added": added,
        "failures": failures,
        "existing_before": resolved.get("existing_steps"),
        "existing_after": verify.get("existing_steps") if verify.get("ok") else None,
        "replace": replace,
        "contract": getattr(sigiri, "CONTRACT_VERSION", "sigiri"),
        "at": _now(),
        "log": log,
    }
    (dest / f"import-{issue_key.upper()}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    report["report"] = str(dest / f"import-{issue_key.upper()}.json")
    return report


def load_csv_steps(csv_path: str) -> dict[str, Any]:
    path = Path(csv_path)
    if not path.is_absolute():
        # try under workspace
        cand = WORKSPACE / csv_path
        if cand.exists():
            path = cand
        else:
            path = REPO_ROOT / csv_path
    if not path.exists():
        return {"ok": False, "error": f"CSV not found: {csv_path}"}
    steps: list[dict[str, str]] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            steps.append(
                {
                    "Action": (row.get("Action") or row.get("action") or "").strip(),
                    "Data": (row.get("Data") or row.get("data") or "").strip(),
                    "Expected Result": (
                        row.get("Expected Result")
                        or row.get("Result")
                        or row.get("result")
                        or row.get("Expected")
                        or ""
                    ).strip(),
                }
            )
    return {"ok": True, "path": str(path), "steps": steps, "count": len(steps)}


def import_csv(issue_key: str, csv_path: str, replace: bool = True) -> dict[str, Any]:
    loaded = load_csv_steps(csv_path)
    if not loaded.get("ok"):
        return loaded
    return import_steps(issue_key, json.dumps(loaded["steps"]), replace=replace)


def import_pack(story_key: str, pack_id: str, issue_key: str, replace: bool = True) -> dict[str, Any]:
    """Import NewTestCases/<story>/sigiri-manual/<pack>/<pack>-steps.csv → issue."""
    safe = "".join(c for c in story_key if c.isalnum() or c in "-_") or "STORY"
    pid = "".join(c for c in pack_id if c.isalnum() or c in "-_") or "P01"
    csv_path = WORKSPACE / "NewTestCases" / safe / "sigiri-manual" / pid / f"{pid}-steps.csv"
    if not csv_path.exists():
        return {"ok": False, "error": f"pack CSV missing: {csv_path}"}
    return import_csv(issue_key, str(csv_path), replace=replace)


def import_registry(registry_json_path: str = "") -> dict[str, Any]:
    """Import all packs listed in jira-created.json (or default PF-58380 registry)."""
    path = Path(registry_json_path) if registry_json_path else (
        WORKSPACE / "NewTestCases" / "PF-58380" / "sigiri-manual" / "jira-created.json"
    )
    if not path.exists():
        return {"ok": False, "error": f"registry not found: {path}"}
    reg = json.loads(path.read_text(encoding="utf-8"))
    results = []
    for t in reg.get("tests") or []:
        key = t.get("key")
        pack = t.get("pack")
        story = reg.get("story") or "PF-58380"
        if not key or not pack:
            continue
        r = import_pack(story, pack, key, replace=True)
        results.append({"key": key, "pack": pack, "ok": r.get("ok"), "steps_added": r.get("steps_added"), "error": r.get("error")})
    ok_all = all(x.get("ok") for x in results) if results else False
    return {"ok": ok_all, "registry": str(path), "results": results}
