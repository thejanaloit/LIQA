# Deploy LIQA Worker VM (industry default)

## Why a VM / VDI (not a random laptop)

Manual QA Hands need a **stable interactive Windows session**:

- Autologon user (not Session 0 service)
- Screen never locks during business hours
- Edge/Chrome installed
- Outbound HTTPS to Control only (bank-friendly)
- Local vault for maker/checker

Laptop Cursor MCP is for **authors**. Production execution = **Worker VM**.

---

## Minimum VM spec

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| OS | Windows 10/11 Pro or Windows Server with Desktop Experience | Win11 Enterprise / AVD |
| vCPU | 4 | 8 |
| RAM | 16 GB | 32 GB |
| Disk | 128 GB SSD | 256 GB (proofs) |
| Display | 1920×1080 virtual display | Dual if OCR-heavy |
| Network | Outbound 443 to Control + UAT | No inbound from internet |

Cloud examples: Azure `D4s_v5` / `D8s_v5`, or AVD personal host pool.

---

## One-time bootstrap (on the VM)

1. Create local service account `liqa-worker` (or domain) with autologon  
2. Disable lock screen / set power to never sleep when plugged in  
3. Install Python 3.11+, Edge, Git  
4. Clone / unzip LIQA to `C:\LIQA` (or `D:\LIQA`)  
5. Copy `.env` + `secrets\tmp-creds.json` (from vault inject — not email)  
6. Set `LIQA_CONTROL_URL=https://control.internal/...`  
7. Run:

```powershell
cd C:\LIQA
powershell -File scripts\bootstrap-worker-vm.ps1
powershell -File scripts\verify-install.ps1
powershell -File scripts\register-logon-task.ps1
```

8. Reboot into autologon; confirm `GET http://127.0.0.1:8787/health` → headed ok  
9. Worker heartbeats to Control

---

## Hardening

- BitLocker on disk  
- Creds only in DPAPI / Windows Credential Manager / Key Vault agent  
- No inbound RDP from internet (jump host / Bastion only for the 2 QA)  
- Capture retention policy (auto-prune proofs older than N days)  
- Separate Worker per tenant if bank isolation requires it  

---

## Control placement

| Mode | Control runs | Workers run |
|------|--------------|-------------|
| Bank | On-prem VM / private AKS+Windows jump | Same DC / VDI |
| Hybrid | Customer VNet appliance | Customer VNet |
| Studio-only | Dev laptop | Dev laptop (non-prod) |

Workers **poll outbound**; do not open inbound ports on the bank firewall for Control→Worker if policy forbids it.

---

## Scale-out

- Clone golden Worker image (Sysprep carefully — keep autologon recipe)  
- Register unique `LIQA_WORKER_ID` per VM  
- Control assigns jobs only to `headed: true` workers  
- Never two headed jobs on one desktop  

---

## Acceptance before go-live

- [ ] `verify-install.ps1` green  
- [ ] Health red when locked (prove fail-closed)  
- [ ] Queue job from Control → Worker executes headed  
- [ ] Force a Human Gate → appears in Control → 2QA resolve → job resumes  
- [ ] Book1 validate + sign-off path exercised once  
- [ ] Audit entries present  

See `docs/INDUSTRY-PRODUCT.md` and `docs/OPS-MODEL-2QA.md`.
