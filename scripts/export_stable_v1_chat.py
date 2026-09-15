"""Export the LIQA Full Stable V1 chat transcript to artifacts/stable-v1/."""
from __future__ import annotations

import datetime
import hashlib
import json
import pathlib
import re
import shutil
from typing import Any

SRC = pathlib.Path(
    r"C:\Users\ThejanaD\.cursor\projects\e-agency-agents\agent-transcripts"
    r"\eba41c65-a769-4c5e-a6ab-b2c6c59ae740"
    r"\eba41c65-a769-4c5e-a6ab-b2c6c59ae740.jsonl"
)
OUT = pathlib.Path(r"E:\LIQA\artifacts\stable-v1")
CHAT = OUT / "chat"

SECRET_PATTERNS = [
    (
        re.compile(
            r"(?i)(password|passwd|pwd|secret|token|api[_-]?key|client[_-]?secret)"
            r"\s*[:=]\s*['\"]?[^\s'\"<>]{4,}"
        ),
        r"\1=[REDACTED]",
    ),
    (re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-._~+/]+=*"), "Bearer [REDACTED]"),
]


def redact(s: str) -> str:
    out = s
    for pat, repl in SECRET_PATTERNS:
        out = pat.sub(repl, out)
    return out


def extract_text(msg: Any) -> str:
    if msg is None:
        return ""
    if isinstance(msg, str):
        return msg
    if isinstance(msg, dict):
        content = msg.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, dict):
                    if "text" in block:
                        parts.append(str(block["text"]))
                elif isinstance(block, str):
                    parts.append(block)
            return "\n".join(parts)
        return json.dumps(msg, ensure_ascii=False)
    return str(msg)


def strip_tags(text: str) -> str:
    text = re.sub(r"</?timestamp>", "", text)
    text = re.sub(r"</?user_query>", "", text)
    return text.strip()


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Missing transcript: {SRC}")

    CHAT.mkdir(parents=True, exist_ok=True)
    raw_dest = CHAT / "FULL-CHAT.raw.jsonl"
    shutil.copy2(SRC, raw_dest)

    all_md_parts: list[str] = []
    user_turns: list[dict[str, Any]] = []
    line_n = 0
    user_n = 0
    asst_n = 0

    with SRC.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            line_n += 1
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            role = obj.get("role") or "unknown"
            if role == "turn_ended":
                continue
            text = strip_tags(extract_text(obj.get("message")))
            if not text:
                continue
            text = redact(text)
            if role == "user":
                user_n += 1
                user_turns.append({"n": user_n, "line": line_n, "text": text})
                all_md_parts.append(f"\n\n---\n\n## USER #{user_n}\n\n{text}\n")
            elif role == "assistant":
                asst_n += 1
                all_md_parts.append(f"\n\n---\n\n## ASSISTANT #{asst_n}\n\n{text}\n")

    exported = datetime.datetime.now(datetime.timezone.utc).isoformat()
    header = f"""# LIQA Full Stable V1 — Entire Chat Export

**Chat id:** `eba41c65-a769-4c5e-a6ab-b2c6c59ae740`  
**Title for seekers:** LIQA Full Stable V1 Version Chat  
**Exported:** {exported}  
**Source transcript:** Cursor agent transcript JSONL  
**Raw lines:** {line_n}  
**User turns:** {user_n}  
**Assistant turns:** {asst_n}  
**Perfect-100 bar:** PF-59486  
**MCP version:** `2026-09-16-liqa-perfect-100-v5`  
**Agency train:** `2026-09-16-qa-trained-perfect-100-v2` (279)

> If somebody asks for the **LIQA full stable v1 version chat**, give them **this file**
> (and `FULL-CHAT.raw.jsonl`). Nothing intentional is left out of the conversation export.

Secrets in this export are redacted where pattern-matched. Do not commit real passwords.

"""

    full_md = CHAT / "FULL-CHAT.md"
    full_body = header + "".join(all_md_parts)
    full_md.write_text(full_body, encoding="utf-8")

    parts_dir = CHAT / "parts"
    parts_dir.mkdir(exist_ok=True)
    max_chars = 1_500_000
    buf = header
    part_i = 1
    for chunk in all_md_parts:
        if len(buf) + len(chunk) > max_chars and len(buf) > len(header) + 1000:
            (parts_dir / f"FULL-CHAT-part-{part_i:02d}.md").write_text(buf, encoding="utf-8")
            part_i += 1
            buf = f"# LIQA Full Stable V1 — Chat Part {part_i}\n\nContinuation of FULL-CHAT.md\n" + chunk
        else:
            buf += chunk
    (parts_dir / f"FULL-CHAT-part-{part_i:02d}.md").write_text(buf, encoding="utf-8")

    uo_lines = ["# LIQA Stable V1 — User turns only (entire chat)\n"]
    for u in user_turns:
        preview = u["text"][:8000]
        uo_lines.append(f"\n## USER #{u['n']} (jsonl line {u['line']})\n\n{preview}\n")
    (CHAT / "USER-TURNS-ONLY.md").write_text("".join(uo_lines), encoding="utf-8")

    sha = hashlib.sha256(raw_dest.read_bytes()).hexdigest()
    manifest = {
        "product": "LIQA",
        "label": "Full Stable V1",
        "chat_id": "eba41c65-a769-4c5e-a6ab-b2c6c59ae740",
        "exported_utc": exported,
        "raw_jsonl": "chat/FULL-CHAT.raw.jsonl",
        "full_markdown": "chat/FULL-CHAT.md",
        "user_turns_only": "chat/USER-TURNS-ONLY.md",
        "parts_dir": "chat/parts/",
        "part_count": part_i,
        "stats": {
            "raw_bytes": raw_dest.stat().st_size,
            "md_bytes": full_md.stat().st_size,
            "jsonl_lines": line_n,
            "user_turns": user_n,
            "assistant_turns": asst_n,
        },
        "sha256_raw_jsonl": sha,
        "perfect100_ref": "PF-59486",
        "mcp_version": "2026-09-16-liqa-perfect-100-v5",
        "agency_train_version": "2026-09-16-qa-trained-perfect-100-v2",
        "agency_train_count": 279,
        "doctrine": "skills/PERFECT-100-PF-59486-GOLD.md",
        "github_answer": (
            "Give artifacts/stable-v1/chat/FULL-CHAT.md (entire chat) "
            "+ artifacts/stable-v1/README.md"
        ),
    }
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
