# LIQA architecture

Internet-grounded. Manual QA product for external companies. Engine: headed Windows worker, not headless SaaS.

## What the market already does (2026)

| Pattern | Who | What we take |
|---|---|---|
| 3 layers: Brain / Hands / real device | [AskUI AgentOS](https://www.askui.com/blog-posts/3-layer-architecture-demo-trap-enterprise-agents) | Thinking is a commodity. Body must run **inside the customer environment**, not a cloud sandbox. |
| Pixel / OS mouse, not Selenium | [Rainforest QA](https://help.rainforestqa.com/docs/test-execution-faq) | Proprietary VM + OS-level input. Live VNC so a human can watch. |
| Headful live view | [Steel](https://docs.steel.dev/overview/sessions-api/embed-sessions/live-sessions) | WebRTC ~25fps of the real session. `interactive=true` = human-in-the-loop. |
| Outbound tunnel only | [BrowserStack Local](https://www.browserstack.com/docs/local-testing/how-local-testing-works) | Worker opens **outbound** HTTPS. Bank firewall never opens inbound. |
| On-prem agent + LLM | [Karate on-prem CUA](https://karatelabs.io/blog/enterprise-computer-use-on-premises) | Banks refuse screenshots of UAT going to a public LLM. Agent + model can stay inside the network. |
| Trajectory cache after first run | AskUI / Stagehand | Replay **after** a headed proof exists. Not instead of it. |

What we **do not** copy: Karate’s default of **headless Chrome in Docker**. That is a regression farm. LIQA sells **manual QA**. Headless is a later SKU, not the core.

Live view on local host: Worker `GET /v1/live/frame` screenshot poll (25fps cap). WebRTC H.264 when a TURN server exists (`GET /v1/live/webrtc`).


## Target architecture

```
 Customer QA lead (browser)
            │
            │  HTTPS  (jobs, live view, Excel, bugs)
            ▼
 ┌──────────────────────────────────────────────┐
 │  LIQA Control          (SaaS or private VPC) │
 │  Identity · tenants · licenses               │
 │  Job queue · Jira OAuth · format packs       │
 │  Live-view relay (WebRTC)                    │
 │  Artifact store · human-gate inbox           │
 └──────────────────┬───────────────────────────┘
                    │  Worker connects OUTBOUND
                    │  (no inbound hole in the bank)
                    ▼
 ┌──────────────────────────────────────────────┐
 │  LIQA Worker     Windows headed appliance     │
 │  Health: fail if locked / Session 0          │
 │  Eyes: full-desktop capture                  │
 │  Brain: local or approved LLM                │
 │  Hands: OS mouse + keyboard (humanize)       │
 │  Vault: maker/checker creds never leave      │
 │  Chrome: one session, entry URL once         │
 └──────────────────┬───────────────────────────┘
                    ▼
           Customer's UAT (e.g. FusionX)
```

## Three layers (AskUI mapping)

| Layer | LIQA name | Runs where | Job |
|---|---|---|---|
| 1 Thinking | **LIQA Brain** | Worker first (bank). Control LLM only if customer allows screenshots out. | Plan next click from the PNG + story + map. Model-agnostic (Ollama / Azure OpenAI / other). |
| 2 Hands | **LIQA Engine** | Worker | Eyes → wait-until-analyzable → Bezier mouse → type → frame-change. Honesty + human gate. Later: replay cache of proved steps. |
| 3 Workspace | **LIQA Worker** | Customer Windows PC/VM/VDI | Real desktop + Chrome. Same class as AskUI AgentOS / Rainforest VM — **not** a Docker headless tab. |

## Data residency (Karate constraint)

When the worker drives UAT, screenshots can contain PII, balances, session cookies.

| Mode | Screenshots | LLM | Who buys it |
|---|---|---|---|
| **Bank / air-gap** | Stay on worker | Local Ollama / vLLM | Core banking, insurance |
| **Hybrid** | Stay on worker; only labels go out | Cloud LLM under their DPA | Mid-market |
| **Cloud brain** | Cropped frames to Control | Our or their API | Non-regulated apps only |

Default for LIQA **banking SKU**: bank mode. Control never needs the raw UAT pixels — only live-view to *their* logged-in staff, plus artifacts they already own.

## Live view (Rainforest + Steel + BrowserStack)

Customer watches the Worker like Rainforest testers watched a VM over VNC:

- Worker publishes desktop (WebRTC H.264, Steel-style)
- Control relays to the tenant’s QA lead
- `interactive` flag: they can take the mouse for MFA (human gate)
- Session recording → proof MP4/PNG for bugs (Steel Files / Rainforest video logs)

Worker still **must** have a real logged-in display. A black Xvfb-only box is not LIQA Manual.

## Job lifecycle

1. Customer creates a pack in Control (Jira keys, URL, format pack).
2. Control marks job `queued`. Worker pulls it (outbound poll or websocket).
3. Worker `/health` must be headed-ready or job stays queued.
4. Loop: capture → brain → click/type → wait frame → proof PNG.
5. MFA/CAPTCHA → `human_gate` → Control notifies their user → resume on ACK.
6. Close: Excel + bugs + proof uploaded as artifacts (or left on worker for air-gap export).

One browser, entry URL once, same as ManualQA law. Parallelism = **more Workers**, not more tabs on one desktop.

## Trust boundary

```
[Customer IdP] ──OAuth──► Control (metadata, job state)
[Customer Jira] ──OAuth──► Control (issue keys, not passwords)
[Customer vault on Worker] ──never──► Control
[UAT cookies] stay in Worker Chrome profile
```

Same idea as BrowserStack Local: **outbound only**. Same idea as Cursor self-hosted workers: inference/control plane can be elsewhere; **tool execution is on their machine**.

## What is not in this architecture

- Playwright headless as the product
- Cursor Cloud Agent VM as the Kenya/UAT browser
- Crowd testers (Rainforest’s 60k) — LIQA replaces the crowd with one headed agent + their human for gates
- Customers installing Cursor

## Build map (ours today)

| Piece | Exists | Next |
|---|---|---|
| Hands + health HTTP | `manualQA/product/headed-worker` | Brand as LIQA Worker |
| 10-step manual flow | ManualQA MCP | Hide MCP from customer UI |
| Control web | No | Jobs + live view + artifacts |
| WebRTC live view | No | Steel-like debug URL |
| Format packs | LOLC gold only | Pluggable |
| Local brain | Ollama on this PC | Bundle optional on worker |

## Sources

- AskUI, *3-Layer Architecture for Enterprise AI Agents* (2026)
- Karate Labs, *Enterprise Computer Use On-Premises* (2026)
- Rainforest QA, test execution / VM + visual (not Selenium)
- Steel Live Sessions (headful WebRTC)
- BrowserStack Local Testing internals (outbound tunnel)
- Reactify, *Browser-using AI agents in 2026* (cloud browser vs OS computer-use)
