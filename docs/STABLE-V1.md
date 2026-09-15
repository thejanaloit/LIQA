# LIQA Full Stable V1

**Status:** FINAL STABLE  
**GitHub:** https://github.com/thejanaloit/LIQA  
**Tag:** `stable-v1`  
**MCP:** `2026-09-16-liqa-perfect-100-v5`  
**Perfect-100 run:** PF-59486  
**Agency train:** `2026-09-16-qa-trained-perfect-100-v2` (279)

## If someone asks for the Stable V1 chat

Give them the **entire conversation export**:

1. [`artifacts/stable-v1/README.md`](../artifacts/stable-v1/README.md)
2. [`artifacts/stable-v1/chat/FULL-CHAT.md`](../artifacts/stable-v1/chat/FULL-CHAT.md) — full readable chat
3. [`artifacts/stable-v1/chat/FULL-CHAT.raw.jsonl`](../artifacts/stable-v1/chat/FULL-CHAT.raw.jsonl) — raw Cursor transcript (nothing left out of the JSONL)
4. [`artifacts/stable-v1/MANIFEST.json`](../artifacts/stable-v1/MANIFEST.json) — checksums + stats

Re-export (same chat id):

```powershell
py -3 scripts\export_stable_v1_chat.py
```

## What Stable V1 locks

- End-to-end Manual QA = Perfect-100 PF-59486 bar
- Book1 SHARE ≥110 + 100% screenshots
- Sigiri Xray UI RPA (subprocess if asyncio)
- Bug dedupe before createJiraIssue
- 279 agency-qa-trained overlays

Doctrine: [`skills/PERFECT-100-PF-59486-GOLD.md`](../skills/PERFECT-100-PF-59486-GOLD.md)
