# LIQA Industry pack

Read in order:

1. [INDUSTRY-PRODUCT.md](../../docs/INDUSTRY-PRODUCT.md) — what to deploy
2. [DEPLOY-WORKER-VM.md](../../docs/DEPLOY-WORKER-VM.md) — Worker VM blueprint
3. [OPS-MODEL-2QA.md](../../docs/OPS-MODEL-2QA.md) — how the 2 humans work
4. [ARCHITECTURE.md](../../docs/ARCHITECTURE.md) — market patterns

## Quick start

```powershell
# Control host
powershell -File scripts\bootstrap-control.ps1

# Each Worker VM (interactive session)
powershell -File scripts\bootstrap-worker-vm.ps1
```

Control UI: `http://<control>:8788/` — gates + sign-off for the 2 QA leads.
