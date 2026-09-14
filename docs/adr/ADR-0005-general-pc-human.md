# ADR-0005 — General PC human, not a single-site bot

## Status

Accepted. 2026-09-10.

## Context

LIQA started as headed manual QA. The owner also needs the same engine to shop, use Facebook with **their** credentials, drive Explorer, and follow any short natural-language task — like a complete human on this PC.

## Decision

- One product, two SKUs of **prompt packs**: `manual_qa` and `general_pc`.
- Core loop is always ManualQA’s 10 steps + Eyes→Brain→Hands.
- Shopping / social examples are **playbooks**, not the architecture.
- Human gates stay: hard CAPTCHA, SMS, Google 2FA.
- Own-PC, own-credentials. No account-farm SKU.

## Consequences

Control UI accepts any English/Sinhala task. Worker `/v1/predict` + `/v1/run` execute on the interactive desktop. Bank customers can disable general_pc playbooks.
