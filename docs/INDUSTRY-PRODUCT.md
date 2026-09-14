# LIQA Industry Product — 2 QA humans + agent execution

## Product statement

**LIQA Industry** is the deployable form of Manual QA execution:

- **LIQA Workers** run almost all headed QA execution
- **2 QA humans** own gates, data unblock, and release sign-off
- Remaining staff move off click-level QA

This is **not** “put Cursor on a laptop and hope.”  
Industry grade = **Control plane + headed Worker appliances + Human Gate inbox**.

---

## Best suitable method (honest)

| Option | Fit | Verdict |
|--------|-----|---------|
| **Dedicated Windows Worker VM / VDI** (Azure VM, Hyper-V, VMware, AVD) | Interactive desktop, autologon, never-lock, outbound-only to Control | **Primary — industry default** |
| Physical Windows QA PCs | Same as VM, stronger for GPU/OCR | OK for on-prem banks |
| Linux Docker / k8s headless Chrome | No real desktop Hands | **Reject for Manual QA SKU** |
| Cursor Cloud Agent alone | Cannot click customer Windows UAT | Authoring only, not execution SKU |
| One shared RDP session for many jobs | Focus fights, proof pollution | Avoid; 1 job ↔ 1 worker session |

**Recommendation:**  
1–N **Windows Worker VMs** inside the customer network (or VDI), plus **1 Control** (private VPC or on-prem).  
Cursor MCP (`liqa`) stays for **agent authors / platform team** — production jobs queue through Control.

```
 Jira / backlog
        │
        ▼
 ┌─────────────────────┐
 │  LIQA Control       │  ← 2 QA humans live here (gates + sign-off UI)
 │  jobs · gates ·     │
 │  audit · Book1 meta │
 └─────────┬───────────┘
           │ worker polls OUTBOUND (no inbound bank hole)
           ▼
 ┌─────────────────────┐     ┌─────────────────────┐
 │ Worker VM A         │     │ Worker VM B         │  … scale out
 │ headed Edge/Chrome  │     │ headed Edge/Chrome  │
 │ Eyes/Brain/Hands    │     │ Eyes/Brain/Hands    │
 │ local vault         │     │ local vault         │
 └─────────┬───────────┘     └─────────┬───────────┘
           └──────────┬────────────────┘
                      ▼
                 Customer UAT
```

---

## SKUs

| SKU | Who | What ships |
|-----|-----|------------|
| **LIQA Bank** | Regulated | Workers on-prem/VDI; pixels stay on worker; local LLM; Control private |
| **LIQA Hybrid** | Mid-market | Workers in customer VNet; Control managed; labels only leave worker |
| **LIQA Studio** | Platform team | Cursor MCP + gold packs + handover zip (dev/authoring) |

Industry “replace 18 of 20 clickers” = **Bank or Hybrid** + Studio for the platform owners.

---

## Capacity planning (starting point)

| Workers (headed VMs) | Rough concurrent stories | Human gate load (2 QA) |
|----------------------|--------------------------|-------------------------|
| 1 | 1 active headed run | Light |
| 2–3 | Parallel epics / tenants | Normal for 2 seniors |
| 5+ | Multi-product factory | Need clear on-call rota for the 2 |

Rule: **one headed job per worker desktop session**.

---

## Non-negotiables (industry)

1. Worker `/health` fails if Session 0 / locked / LogonUI  
2. Secrets never in git; worker-local vault or HSM/Key Vault inject at boot  
3. Human Gate for OTP/MFA — alert the 2 QA (Teams/email/Control inbox)  
4. Book1 SHARE validators before sign-off  
5. Audit log on job create / gate resolve / sign-off  
6. Outbound-only worker connectivity where bank policy requires it  

---

## Deploy docs

- Ops model for the 2 humans: `docs/OPS-MODEL-2QA.md`
- Worker VM blueprint: `docs/DEPLOY-WORKER-VM.md`
- Architecture (market patterns): `docs/ARCHITECTURE.md`
- Quality bar: `docs/QUALITY-CONTRACT.md`

## Bootstrap

```powershell
# On Control host
powershell -File scripts\bootstrap-control.ps1

# On each Worker VM (interactive user session)
powershell -File scripts\bootstrap-worker-vm.ps1
powershell -File scripts\verify-install.ps1
powershell -File scripts\register-logon-task.ps1
```
