"""Redact secrets inside Stable V1 chat exports before git push."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"E:\LIQA\artifacts\stable-v1\chat")
FILES = [
    ROOT / "FULL-CHAT.raw.jsonl",
    ROOT / "FULL-CHAT.md",
    ROOT / "USER-TURNS-ONLY.md",
    *sorted((ROOT / "parts").glob("FULL-CHAT-part-*.md")),
]

REPLACERS = [
    (re.compile(r"(?i)(password['\"]?\s*[:=]\s*['\"])[^'\"]{3,}"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(\"password\"\s*:\s*\")[^\"]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(Bearer\s+)[A-Za-z0-9\-._~+/]+=*"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(client_secret['\"]?\s*[:=]\s*['\"])[^'\"]{3,}"), r"\1[REDACTED]"),
    # known leaked UAT-style password fragment from this chat
    (re.compile(re.escape("The@#2275384@#")), "[REDACTED]"),
]


def main() -> None:
    for path in FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        orig = text
        for pat, repl in REPLACERS:
            text = pat.sub(repl, text)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            print("redacted", path.name, "delta", len(orig) - len(text))
        else:
            print("clean", path.name)


if __name__ == "__main__":
    main()
