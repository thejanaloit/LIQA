# LIQA TODO (full product)

Status: ` [ ] ` open · `[x]` done · `[~]` in progress
Core law: headed Worker is the product. Headless is not a P0 SKU.

## P0 Foundation & repo

- [x] **T001** Create LIQA monorepo layout (apps/control, apps/worker, docs, tests, vendor)
- [x] **T002** Add .gitignore for .env, captures, vendor/oss, secrets, __pycache__
- [x] **T003** Add LICENSE (proprietary + OSS attribution file)
- [x] **T004** Add CODEOWNERS and SECURITY.md (no secrets in git)
- [x] **T005** Add CONTRIBUTING.md and PR template
- [x] **T006** Add .editorconfig and ruff/black/pytest config
- [x] **T007** Write PRODUCT.md one-pager for sales
- [x] **T008** Write PRODUCT-PLAN.md (this plan)
- [x] **T009** Write ARCHITECTURE.md with mermaid diagrams
- [x] **T010** Write DATA-RESIDENCY.md (bank / hybrid / cloud-brain modes)
- [x] **T011** Write THREAT-MODEL.md (STRIDE on Control, Worker, live view)
- [x] **T012** Write ADR-0001 headed-not-headless core
- [x] **T013** Write ADR-0002 outbound-only worker connect
- [x] **T014** Write ADR-0003 model-agnostic brain
- [x] **T015** Write ADR-0004 Cursor API is dispatcher not clicker
- [x] **T016** Pin Python 3.11+ for worker and control
- [x] **T017** Create apps/control/requirements.txt
- [x] **T018** Create apps/worker/requirements.txt
- [x] **T019** Create scripts/dev.ps1 to run control+worker locally
- [x] **T020** Create scripts/verify-install.ps1 for customer worker
- [x] **T021** Add health smoke script scripts/smoke.ps1
- [x] **T022** Document Cursor API in .env.example only (never commit keys)
- [x] **T023** Wire TBB letter for LIQA start in ThejaBackBone town
- [x] **T024** Add README badges: headed-only, outbound-tunnel, bank-sku

## P0 Worker (headed appliance)

- [x] **T025** Port ManualQA headed-worker HTTP into apps/worker
- [x] **T026** GET /health fail-closed on Session 0 / LogonUI / tiny display
- [x] **T027** Reject QAFUSIONX_HEADED=0 and HUMANIZE_HEADLESS
- [x] **T028** GET /v1/status with monitor list, DPI, foreground window
- [x] **T029** POST /v1/jobs queue headed jobs on disk
- [x] **T030** GET /v1/jobs and GET /v1/jobs/{id}
- [x] **T031** Bearer token auth (LIQA_WORKER_TOKEN)
- [x] **T032** Bind 127.0.0.1 by default; optional LAN with token
- [x] **T033** Integrate humanize screenshot (full desktop PNG)
- [x] **T034** Integrate Bezier mouse move then click
- [x] **T035** Integrate typed input with delay (no paste-dump for passwords)
- [x] **T036** Wait-until-analyzable after every action (splash/modals)
- [x] **T037** humanize_wait_frame_change before next decision
- [x] **T038** Presence overlay / badge so customer sees agent is live
- [x] **T039** One-browser session lock (never close mid-job)
- [x] **T040** Entry URL once; forbid page.goto after entry
- [x] **T041** Chrome/Edge detect on PATH
- [x] **T042** Autologon + never-sleep checklist in worker README
- [x] **T043** Windows scheduled task start-worker-at-logon
- [x] **T044** Heartbeat POST to Control (outbound)
- [x] **T045** Job pull from Control (outbound websocket or poll)
- [x] **T046** Local vault path for maker/checker JSON (gitignored)
- [x] **T047** Refuse to start job if /health not ok
- [x] **T048** Capture dir rotation + PII warning
- [x] **T049** OCR optional (Tesseract) for click-text
- [x] **T050** DPI-aware coordinate remap (computer-use ScalePlan pattern)
- [x] **T051** Multi-monitor: capture active UAT monitor only by default
- [x] **T052** Focus target window before click
- [x] **T053** Calibrate 4-corners + centre before first click of a job
- [x] **T054** Worker version endpoint /v1/version

## P0 Control plane

- [x] **T055** HTTP Control server (stdlib first, FastAPI later)
- [x] **T056** GET /health live + ready
- [x] **T057** Tenant create/list (single-tenant stub then multi)
- [x] **T058** API keys per tenant (hash at rest)
- [x] **T059** POST /v1/jobs create story pack
- [x] **T060** GET /v1/jobs list/filter by status
- [x] **T061** GET /v1/jobs/{id} detail
- [x] **T062** POST /v1/jobs/{id}/cancel
- [x] **T063** Worker registry: last heartbeat, headed health
- [x] **T064** Assign job to a headed-ready worker only
- [x] **T065** Artifact upload endpoint (PNG, xlsx, mp4)
- [x] **T066** Signed download URLs for artifacts
- [x] **T067** Human-gate inbox: list pending MFA/CAPTCHA
- [x] **T068** POST /v1/gates/{id}/ack resume job
- [x] **T069** Audit log of who started/cancelled/acked
- [x] **T070** CORS allowlist for Control UI
- [x] **T071** Rate limit job create
- [x] **T072** OpenAPI.yaml for Control
- [x] **T073** Control UI stub: job list + health pills
- [x] **T074** Control UI: live view placeholder iframe
- [x] **T075** Control UI: download Book1 button
- [x] **T076** Session cookie + CSRF for UI
- [x] **T077** SSO stub (OIDC) for customer IdP
- [x] **T078** RBAC: owner / qa-lead / viewer
- [x] **T079** License seat count (workers max)

## P0 Cursor API dispatcher

- [x] **T080** Document Cursor Cloud Agents API as optional dispatcher
- [x] **T081** Read CURSOR_API_KEY from env only
- [x] **T082** POST /v1/cursor/dispatch wrapper with timeout
- [x] **T083** Map Cursor run status to LIQA job status
- [x] **T084** Never send UAT screenshots to Cursor by default (bank SKU)
- [x] **T085** Self-hosted worker note: computer-use is macOS/Linux, LIQA Worker is Windows
- [x] **T086** Rotate leaked keys procedure in SECURITY.md
- [x] **T087** Service-account vs user API key notes for Enterprise

## P1 Live view (Steel/Rainforest/BrowserStack)

- [x] **T088** WebRTC publisher on Worker (desktop H.264)
- [x] **T089** Control SFU or simple P2P relay for tenant viewers
- [x] **T090** debugUrl embed in Control UI
- [x] **T091** interactive=true take-over for human gate
- [x] **T092** Viewer auth: only same tenant
- [x] **T093** Recording to MP4 on worker disk
- [x] **T094** Upload recording as artifact
- [x] **T095** Blur PII toggle (future)
- [x] **T096** 25fps cap to control bandwidth
- [x] **T097** Fallback screenshot poll if WebRTC blocked
- [x] **T098** NAT: outbound-only ICE/TURN in customer VPC
- [x] **T099** Presence badge visible in live view

## P1 Brain (model-agnostic)

- [x] **T100** Brain interface: screenshot + map + story → next action JSON
- [x] **T101** Local Ollama adapter (qwen2.5-vl / llava when available)
- [x] **T102** Azure OpenAI adapter (customer key on worker)
- [x] **T103** Refuse cloud brain in bank mode
- [x] **T104** Action schema: click_text | type | wait | human_gate | done
- [x] **T105** Never guess x/y if control not in latest capture
- [x] **T106** Ask-user path when target unclear
- [x] **T107** Honesty referee: 20 approaches before REAL BUG
- [x] **T108** 3-cycle revalidation hook
- [x] **T109** Store decision log next to PNG (no secrets)
- [x] **T110** Prompt pack: Sigiri/TestCrafters format optional
- [x] **T111** Prompt pack: customer format pack loader
- [x] **T112** Token/cost meter per job
- [x] **T113** Offline brain fallback: scripted case steps only

## P1 Jira / stories / tests

- [x] **T114** Jira OAuth app (lolcgroupdev + generic Atlassian)
- [x] **T115** Pull assigned issues into job pack
- [x] **T116** Pull linked Xray tests read-only
- [x] **T117** Never edit/delete customer existing Xray tests
- [x] **T118** Create NEW tests only when licensed
- [x] **T119** Bug file with PNG attach (gold title pattern pluggable)
- [x] **T120** Confluence page fetch for URS (never invent URS)
- [x] **T121** Format pack JSON: story/test/bug templates
- [x] **T122** Default pack: generic ISTQB functional
- [x] **T123** Optional pack: PF-59194 Sigiri (LOLC only)
- [x] **T124** CSV/XLSX export of cases
- [x] **T125** Book1 generator (7 columns + embedded PNG)
- [x] **T126** Validate Book1 ≥110 rows contract optional per tenant
- [x] **T127** iPay-lite 7-col matrix optional

## P1 Human gate & dual control

- [x] **T128** Detect MFA/CAPTCHA/phone-call screens
- [x] **T129** Pause job + notify Control
- [x] **T130** Email/desktop OTP capture when field visible (never invent)
- [x] **T131** SMS/Google 2FA: wait for human ACK
- [x] **T132** Maker then checker in SAME worker session
- [x] **T133** Logout/login inside same Chrome (no new process)
- [x] **T134** Vault: two or three creds; honest not-enough
- [x] **T135** Audit who acked the gate
- [x] **T136** Timeout then BLOCKED not FAIL

## P2 Security, tenancy, compliance

- [x] **T137** Tenant isolation tests
- [x] **T138** Encrypt artifacts at rest
- [x] **T139** TLS for Control
- [x] **T140** mTLS optional worker↔control
- [x] **T141** SBOM generation
- [x] **T142** Dependabot / pip-audit
- [x] **T143** No secrets in logs (redact)
- [x] **T144** PII retention policy (days)
- [x] **T145** GDPR DPA template
- [x] **T146** SOC2 control list (later)
- [x] **T147** Customer can wipe worker captures in one command
- [x] **T148** Air-gap export: zip artifacts without Control
- [x] **T149** Network policy: worker egress allowlist
- [x] **T150** Pentest checklist
- [x] **T151** Session lock detection as security event

## P2 Packaging & install

- [x] **T152** Windows installer (Inno or msix) for Worker
- [x] **T153** Worker autostart at user logon
- [x] **T154** Hyper-V / VMware appliance image notes
- [x] **T155** Autologon + disable lock screen runbook
- [x] **T156** GPU/virtual display requirements
- [x] **T157** RDP disconnect = unhealthy (document tscon/console)
- [x] **T158** Offline installer with wheels
- [x] **T159** Update channel (signed)
- [x] **T160** License key activation
- [x] **T161** Uninstall cleans captures optionally

## P2 Observability & ops

- [x] **T162** Structured JSON logs
- [x] **T163** Prometheus /health metrics
- [x] **T164** Job duration dashboard
- [x] **T165** Headed health fail reasons counter
- [x] **T166** Alert: worker silent > 60s
- [x] **T167** Alert: job stuck in human_gate > SLA
- [x] **T168** OpenTelemetry traces brain→hands
- [x] **T169** Support bundle zip (no secrets)

## P3 Replay / hybrid AFTER headed proof

- [x] **T170** Record trajectory of proved headed steps
- [x] **T171** Replay on headed worker (visible)
- [x] **T172** Do not enable headless replay as default SKU
- [x] **T173** Self-heal when UI drifts (re-enter brain)
- [x] **T174** Cache invalidation on screenshot mismatch

## P3 Product, sales, legal

- [x] **T175** Pricing SKUs: Worker seat + Control tenant + Bank air-gap
- [x] **T176** Website copy: not Cursor, not headless SaaS
- [x] **T177** Demo script (15 min headed)
- [x] **T178** SLA: headed worker uptime
- [x] **T179** MSA + DPA + AUP
- [x] **T180** Trademark LIQA search
- [x] **T181** Customer onboarding checklist
- [x] **T182** Support runbook
- [x] **T183** Status page
- [x] **T184** Changelog

## P3 Research / OSS absorb (lawful)

- [x] **T185** Shallow-clone steel-browser (Apache-2) for live-view ideas
- [x] **T186** Shallow-clone midscene for GUI-agent E2E patterns
- [x] **T187** Shallow-clone zavora computer-use-mcp (MIT) for Win32 notes
- [x] **T188** Read Stagehand MIT docs (act/extract/observe) — do not vendor Playwright as core
- [x] **T189** Read browser-use MIT agent loop — map to LIQA brain JSON
- [x] **T190** Document AskUI 3-layer (no source steal)
- [x] **T191** Document Rainforest VM+VNC (no source steal)
- [x] **T192** Document BrowserStack Local outbound tunnel
- [x] **T193** Document Karate on-prem CUA + why we reject headless Docker core
- [x] **T194** License NOTICE for all vendor clones
- [x] **T195** Do not scrape authenticated proprietary apps
- [x] **T196** Absorb TQU/void_humanize + ManualQA device_core (owned)

## P3 QA of LIQA itself

- [x] **T197** Unit tests worker health mock lock screen
- [x] **T198** Unit tests job queue
- [x] **T199** Integration: control assigns only headed-ready worker
- [x] **T200** Smoke: start worker, GET /health 200 on this PC
- [x] **T201** Negative: lock screen → 503
- [x] **T202** Contract test OpenAPI
- [x] **T203** Book1 fixture validate
- [x] **T204** No secret in repo grep CI
- [x] **T205** Headed self-test: open notepad, type, screenshot
- [x] **T206** Chaos: kill Chrome mid-job → recover once

## P3 Minor / polish

- [x] **T207** Favicon and LIQA wordmark
- [x] **T208** Empty states in Control UI
- [x] **T209** i18n en + si strings
- [x] **T210** Keyboard shortcuts in Control
- [x] **T211** Worker toast: job started
- [x] **T212** Disk space check before capture
- [x] **T213** Clock skew warning worker vs control
- [x] **T214** NTP note in runbook
- [x] **T215** HiDPI screenshot downscale for brain (WXGA like Mcp.ComputerUse)
- [x] **T216** Click retry jitter
- [x] **T217** Double-click vs single-click policy
- [x] **T218** IME/Sinhala keyboard type path
- [x] **T219** Print-screen hotkey ignore
- [x] **T220** Remote desktop fullscreen warning
- [x] **T221** Multiple Chrome profiles isolation
- [x] **T222** Cookie wipe between customers on shared appliance
- [x] **T223** Time-box SBTM charter field on job
- [x] **T224** PROOF debrief markdown per job
- [x] **T225** Learn-cycle hook after job close
- [x] **T226** Telemetry opt-in only
- [x] **T227** Dark/light Control UI tokens (no gradient slop)
- [x] **T228** Accessibility of Control UI (focus, contrast)
- [x] **T229** PDF export of architecture for procurement
- [x] **T230** One-page bank FAQ: pixels stay on worker

_Total items: **230**_
