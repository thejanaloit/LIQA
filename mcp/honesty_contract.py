"""Honesty + evaluate-every-time laws (ManualQA v116).

Law A — Everything is possible:
  Try up to 20 distinct approaches before REAL_BUG.
  If ANY approach finds a working way → PASS (not a bug).
  Only after 20 failed approaches with proof → REAL_BUG.

Law B — Evaluate every step every time:
  On every complete_step / gate unlock, re-evaluate steps 1..current.
  A prior step that regresses blocks advance.
"""
from __future__ import annotations

import re
from typing import Any

HONESTY_MAX_APPROACHES = 20
OBVIOUS_MIN_REPROS = 3
OBVIOUS_DEFECT_CLASSES = {
    "blank_shell",
    "blank_page",
    "http_5xx",
    "crash",
    "missing_control",
    "wrong_module_confirmed",
    "data_loss",
}
HONESTY_CONTRACT_VERSION = "2026-09-13-honesty-obvious-3-repro-v118"

_SUCCESS_RE = re.compile(
    r"\b(PASS|PASSED|SUCCESS|SUCCEEDED|WORKED|FOUND[_\s-]?WAY|OK|RESOLVED|FIXED|ABLE)\b",
    re.I,
)
_FAIL_RE = re.compile(
    r"\b(FAIL|FAILED|BLOCKED|ERROR|STILL[_\s-]?BROKEN|NO[_\s-]?WAY|UNABLE|MISSING)\b",
    re.I,
)


def attempt_succeeded(result: str) -> bool:
    text = (result or "").strip()
    if not text:
        return False
    if _SUCCESS_RE.search(text) and not re.search(r"\b(DID\s+NOT|NOT\s+PASS|UNABLE)\b", text, re.I):
        return True
    return False


def attempt_failed(result: str) -> bool:
    text = (result or "").strip()
    if attempt_succeeded(text):
        return False
    if not text:
        return True
    return bool(_FAIL_RE.search(text)) or True  # unknown → treat as not-yet-success


def summarize_honesty_case(case: dict[str, Any]) -> dict[str, Any]:
    attempts = list(case.get("attempts") or [])
    n = len(attempts)
    successes = [a for a in attempts if attempt_succeeded(str(a.get("result") or ""))]
    failures = [a for a in attempts if not attempt_succeeded(str(a.get("result") or ""))]
    verdict = str(case.get("verdict") or "").upper().strip()
    return {
        "attempts": n,
        "success_count": len(successes),
        "failure_count": len(failures),
        "remaining_before_bug": max(0, HONESTY_MAX_APPROACHES - n),
        "found_a_way": len(successes) > 0,
        "exhausted_20_failures": n >= HONESTY_MAX_APPROACHES and len(successes) == 0,
        "proof_count": sum(1 for a in attempts if str(a.get("proof") or "").strip()),
        "defect_class": str(case.get("defect_class") or "").strip().lower(),
        "verdict": verdict or None,
        "max_approaches": HONESTY_MAX_APPROACHES,
        "contract_version": HONESTY_CONTRACT_VERSION,
    }


def _is_obvious(case: dict[str, Any], defect_class: str = "") -> bool:
    cls = (defect_class or case.get("defect_class") or "").strip().lower()
    return cls in OBVIOUS_DEFECT_CLASSES


def allow_verdict(case: dict[str, Any], verdict: str, defect_class: str = "") -> dict[str, Any]:
    """Return ok + reason for PASS | REAL_BUG | BLOCKED | N/A."""
    v = (verdict or "").upper().strip()
    if defect_class:
        case["defect_class"] = defect_class.strip().lower()
    summary = summarize_honesty_case(case)
    obvious = _is_obvious(case, defect_class)
    law = (
        "Obvious product defects (blank shell, 5xx, missing control, crash) "
        f"need {OBVIOUS_MIN_REPROS} headed repros with proof PNGs. "
        "Ambiguous 'cannot complete AC' still needs 20 approaches. "
        "If you find a working way → PASS, not a bug."
    )

    if v in ("REAL_BUG", "BUG"):
        if summary["found_a_way"]:
            return {
                "ok": False,
                "error": (
                    "REAL_BUG forbidden — at least one approach FOUND A WAY. "
                    "Label PASS (or BLOCKED/N/A if environment), not a product bug."
                ),
                "law": law,
                "summary": summary,
            }
        proofs = int(summary.get("proof_count") or 0)
        fails = int(summary.get("failure_count") or 0)
        if obvious and fails >= OBVIOUS_MIN_REPROS and proofs >= OBVIOUS_MIN_REPROS:
            return {
                "ok": True,
                "verdict": "REAL_BUG",
                "law": law,
                "summary": summary,
                "fast_path": "obvious_defect_3_repro",
            }
        if summary["attempts"] < HONESTY_MAX_APPROACHES:
            need = OBVIOUS_MIN_REPROS if obvious else HONESTY_MAX_APPROACHES
            return {
                "ok": False,
                "error": (
                    f"REAL_BUG needs {need} headed failures with proof "
                    f"(have attempts={summary['attempts']} proofs={proofs}"
                    f"{', defect_class=' + summary['defect_class'] if obvious else ', pass defect_class=blank_shell|missing_control|http_5xx for the 3-repro path'})."
                ),
                "law": law,
                "summary": summary,
            }
        return {"ok": True, "verdict": "REAL_BUG", "law": law, "summary": summary}

    if v == "PASS":
        if summary["attempts"] < 1:
            return {
                "ok": False,
                "error": "PASS requires at least one recorded approach with proof that it worked.",
                "law": law,
                "summary": summary,
            }
        if not summary["found_a_way"]:
            return {
                "ok": False,
                "error": (
                    "PASS requires a successful approach result "
                    "(e.g. PASS/WORKED/FOUND_WAY). All attempts look failed — "
                    "continue approaches or use REAL_BUG only after 20 failures."
                ),
                "law": law,
                "summary": summary,
            }
        return {"ok": True, "verdict": "PASS", "law": law, "summary": summary}

    if v in ("BLOCKED", "N/A"):
        if summary["attempts"] < 1:
            return {
                "ok": False,
                "error": f"{v} still needs at least one honest attempt documenting the wall.",
                "law": law,
                "summary": summary,
            }
        return {"ok": True, "verdict": v, "law": law, "summary": summary}

    return {
        "ok": False,
        "error": f"Unknown verdict {verdict!r}; use PASS|REAL_BUG|BLOCKED|N/A",
        "law": law,
        "summary": summary,
    }


def honesty_state_gate(honesty: dict[str, Any] | None) -> dict[str, Any]:
    """Aggregate gate across all honesty cases for evaluator / n8n."""
    honesty = honesty or {}
    if not honesty:
        return {
            "ok": False,
            "error": "no honesty cases",
            "max_attempts": 0,
            "illegal_real_bugs": [],
            "contract_version": HONESTY_CONTRACT_VERSION,
        }
    illegal: list[str] = []
    max_attempts = 0
    any_real_bug = False
    for case_id, case in honesty.items():
        if not isinstance(case, dict):
            continue
        summary = summarize_honesty_case(case)
        max_attempts = max(max_attempts, summary["attempts"])
        v = summary["verdict"] or ""
        if v in ("REAL_BUG", "BUG"):
            any_real_bug = True
            check = allow_verdict(case, "REAL_BUG")
            if not check["ok"]:
                illegal.append(f"{case_id}: {check['error']}")
    return {
        "ok": not illegal,
        "max_attempts": max_attempts,
        "any_real_bug": any_real_bug,
        "illegal_real_bugs": illegal,
        "cases": len(honesty),
        "contract_version": HONESTY_CONTRACT_VERSION,
        "law": (
            f"Obvious defects: {OBVIOUS_MIN_REPROS} repros with proof. "
            f"Ambiguous AC: {HONESTY_MAX_APPROACHES} approaches. Found-a-way => PASS."
        ),
    }
