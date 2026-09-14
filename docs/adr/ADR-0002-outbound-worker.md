# ADR-0002 — Outbound-only Worker

Status: accepted  
Date: 2026-09-10

The Worker opens HTTPS **out** to Control (BrowserStack Local / Cursor self-hosted worker pattern). Banks do not open inbound ports to our cloud.

If Control cannot be reached, jobs queue locally and export as a zip (air-gap).
