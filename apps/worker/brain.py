"""Azure OpenAI + Ollama + schema + token meter. Bank mode refuses cloud pixels."""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

ALLOWED = {"click_text", "type", "wait", "human_gate", "screenshot", "done", "hotkey", "scroll"}
OLLAMA = os.environ.get("LIQA_OLLAMA", "http://127.0.0.1:11434/v1/chat/completions")
MODEL = os.environ.get("LIQA_BRAIN_MODEL", "qwen2.5-coder:3b")
BANK = os.environ.get("LIQA_BRAIN_MODE", "local") == "local"
TOKENS = {"prompt": 0, "completion": 0}


def models_available() -> dict[str, Any]:
    return {
        "ollama": MODEL,
        "vl": os.environ.get("LIQA_VL_MODEL", "qwen2.5-vl"),
        "llava": "llava",
        "azure": bool(os.environ.get("AZURE_OPENAI_KEY")),
        "bank": BANK,
        "cloud_pixels": False if BANK else os.environ.get("LIQA_ALLOW_CLOUD_BRAIN") == "1",
    }


def validate_action(parsed: dict[str, Any]) -> dict[str, Any]:
    act = parsed.get("action")
    if act not in ALLOWED:
        return {"ok": False, "action": "human_gate", "kind": "unclear", "reason": f"bad action {act}"}
    if act in ("click", "click_xy") or "x" in parsed and "y" in parsed:
        return {"ok": False, "action": "human_gate", "kind": "unclear", "reason": "Refuse raw x/y from model."}
    return {**parsed, "ok": True}


def _chat(url: str, key: str | None, model: str, prompt: str) -> dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    payload = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}).encode()
    req = urllib.request.Request(url, data=payload, method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = json.loads(resp.read().decode())
    usage = raw.get("usage") or {}
    TOKENS["prompt"] += int(usage.get("prompt_tokens") or 0)
    TOKENS["completion"] += int(usage.get("completion_tokens") or 0)
    text = (((raw.get("choices") or [{}])[0].get("message") or {}).get("content")) or ""
    return {"text": text, "tokens": dict(TOKENS)}


def decide(task: str, ocr_preview: str, predicted: list[str]) -> dict[str, Any]:
    schema_hint = (
        "Return ONLY JSON: {action: click_text|type|wait|human_gate|screenshot|done, "
        "text?: string, secret?: bool, reason: string}. Never invent x,y. "
        "If control not in OCR, action=human_gate kind=unclear."
    )
    fallback = {
        "ok": True,
        "source": "predicted_steps",
        "action": "screenshot",
        "reason": "Brain offline — Eyes first, then scripted/predicted steps.",
        "predicted": predicted[:5],
        "bank": BANK,
        "tokens": dict(TOKENS),
    }
    if BANK and os.environ.get("LIQA_ALLOW_CLOUD_BRAIN") == "1":
        return {"ok": False, "action": "human_gate", "kind": "policy", "reason": "Refuse cloud brain in bank mode."}
    prompt = f"Task: {task}\nOCR (no secrets): {ocr_preview[:1500]}\nPredicted: {predicted}\n{schema_hint}"
    azure = os.environ.get("AZURE_OPENAI_ENDPOINT")
    try:
        if azure and os.environ.get("AZURE_OPENAI_KEY") and not BANK:
            raw = _chat(azure.rstrip("/") + "/openai/deployments/default/chat/completions?api-version=2024-02-15-preview", os.environ.get("AZURE_OPENAI_KEY"), MODEL, prompt)
            src = "azure"
        else:
            raw = _chat(OLLAMA, None, MODEL, prompt)
            src = "ollama"
        text = raw.get("text") or ""
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            parsed = json.loads(text[start : end + 1])
            parsed["source"] = src
            parsed["tokens"] = raw.get("tokens")
            parsed["bank"] = BANK
            return validate_action(parsed)
        return fallback
    except Exception as e:
        fallback["brain_error"] = str(e)
        return fallback
