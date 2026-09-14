"""Signed download URLs + Fernet-or-xor artifact encrypt."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from pathlib import Path
from typing import Any

SECRET = os.environ.get("LIQA_SIGNING_SECRET", "liqa-dev-only-change-me")
ART = Path(os.environ.get("LIQA_CONTROL_DATA", Path(__file__).resolve().parent / "data")) / "artifacts"
ART.mkdir(parents=True, exist_ok=True)


def sign(artifact_id: str, ttl: int = 600) -> dict[str, Any]:
    exp = int(time.time()) + ttl
    msg = f"{artifact_id}.{exp}".encode()
    sig = hmac.new(SECRET.encode(), msg, hashlib.sha256).hexdigest()
    return {"ok": True, "url": f"/v1/artifacts/{artifact_id}/download?exp={exp}&sig={sig}", "exp": exp}


def verify(artifact_id: str, exp: str, sig: str) -> bool:
    try:
        if int(exp) < time.time():
            return False
    except ValueError:
        return False
    msg = f"{artifact_id}.{exp}".encode()
    expect = hmac.new(SECRET.encode(), msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expect, sig)


def encrypt_bytes(data: bytes) -> bytes:
    key = hashlib.sha256(SECRET.encode()).digest()
    out = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    return base64.b64encode(out)


def decrypt_bytes(data: bytes) -> bytes:
    key = hashlib.sha256(SECRET.encode()).digest()
    raw = base64.b64decode(data)
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))
