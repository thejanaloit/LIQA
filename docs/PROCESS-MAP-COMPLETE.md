# LIQA Complete Process Map

**Canonical pack:** [`artifacts/stable-v1/process-map/`](../artifacts/stable-v1/process-map/)

That folder maps **every macro and micro-process** from the Full Stable V1 chat through Perfect-100 PF-59486:

| File | Purpose |
|------|---------|
| [README.md](../artifacts/stable-v1/process-map/README.md) | Full mermaid flows + agent matrix |
| [MICROPROCESSES.json](../artifacts/stable-v1/process-map/MICROPROCESSES.json) | Machine catalog (MP-xxx IDs, tools, gates) |
| [LIQA-TOOLS.json](../artifacts/stable-v1/process-map/LIQA-TOOLS.json) | All 98 `liqa_*` tools |

Regenerate catalog:

```powershell
py -3 scripts\generate_process_map_catalog.py
```

See also: [STABLE-V1.md](STABLE-V1.md) · [PERFECT-100 doctrine](../skills/PERFECT-100-PF-59486-GOLD.md)
