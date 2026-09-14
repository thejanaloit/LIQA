# ADR-0001 — Headed core

Status: accepted  
Date: 2026-09-10

LIQA’s execution environment is a **logged-in Windows desktop** the customer can watch.

Headless Chromium / Docker Chrome is not the P0 SKU. It produces false pass/fail on splash, Azure AD, and maker-checker (VOID lesson from PF-57868).

Replay of already-proved steps may come later (P3), still visible by default.
