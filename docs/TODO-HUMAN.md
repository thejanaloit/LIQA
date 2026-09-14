# LIQA TODO-HUMAN (general PC agent)

Start **after** leftover P0 on `docs/TODO.md` is moving. Core law: headed, honest gates, own-PC credentials.

Status: ` [ ] ` open · `[x]` done · `[~]` in progress

## H0 Product law & honesty

- [x] **H001** Write VISION.md general PC human (not one-site bot)
- [x] **H002** Write ADR-0005 general_pc vs manual_qa prompt packs
- [x] **H003** Write CAPTCHA-AND-HUMAN-GATE.md click-checkbox vs pause
- [x] **H004** Write MANUALQA-10-STEPS.md as the core of every task
- [x] **H005** Write WORLD-SOLUTIONS.md catalog for owner study
- [x] **H006** Refuse captcha-farm vendors in AUP
- [x] **H007** Refuse mass account-creation SKU
- [x] **H008** Own-PC own-credentials only in examples
- [x] **H009** Sinhala+English NL parser for task restatement
- [x] **H010** Stop-and-ask when target unclear (no hallucinated shops)
- [x] **H011** 100% honest job status: stepped | human_gate | blocked | done | failed
- [x] **H012** Never mark done without proof PNG
- [x] **H013** Predict next 3 actions after every frame
- [x] **H014** Store decision log beside PNG with secrets redacted

## H0 Eyes on full PC

- [x] **H015** Full-desktop PNG every frame change
- [x] **H016** Optional full-display mss vs browser-viewport only
- [x] **H017** Multi-monitor pick active window monitor
- [x] **H018** DPI-aware screenshot downscale for brain
- [x] **H019** OCR overlay optional Tesseract
- [x] **H020** Foreground window title in capture metadata
- [x] **H021** Cursor position recorded on every PNG
- [x] **H022** Presence badge so a human sees the agent is live
- [x] **H023** Calibrate 4 corners + centre at job start
- [x] **H024** Refuse capture if lock screen / LogonUI
- [x] **H025** Capture rotation + disk-space check
- [x] **H026** PII warning in capture folder README

## H0 Hands on OS + browser + anything

- [x] **H027** Bezier mouse move then click
- [x] **H028** click_text from OCR never blind x/y
- [x] **H029** Type with delay; passwords not paste-dumped
- [x] **H030** Hotkeys (Enter, Tab, Ctrl+L forbidden after entry URL)
- [x] **H031** Focus window by title substring
- [x] **H032** Scroll wheel with wait_analyzable
- [x] **H033** Drag-drop when both handles visible
- [x] **H034** Double-click vs single-click policy
- [x] **H035** Right-click context menu then click_text
- [x] **H036** IME / Sinhala keyboard path
- [x] **H037** File Explorer: open folder, select file, copy path
- [x] **H038** Notepad/Word: type, save, proof
- [x] **H039** Excel: open workbook, read cell via UI not COM-only
- [x] **H040** Start Menu search then Enter
- [x] **H041** Taskbar pin/app switch Alt-Tab as last resort
- [x] **H042** One Chrome/Edge process; never close mid-job
- [x] **H043** Entry URL once; then clicks only
- [x] **H044** New tab via UI click not chrome.tabs API
- [x] **H045** Address bar forbidden after entry
- [x] **H046** PDF viewer in Edge as a window like any other
- [x] **H047** Print dialog: human_gate (easy to wreck printers)
- [x] **H048** UAC prompt: human_gate always

## H0 Natural language → plan → run

- [x] **H049** POST /v1/predict returns ManualQA 10 + extras
- [x] **H050** POST /v1/run one Eyes-Brain-Hands cycle
- [x] **H051** Loop until done | human_gate | max_steps
- [x] **H052** Local Ollama adapter with JSON action schema
- [x] **H053** Fallback predicted steps if brain down
- [x] **H054** Bank mode never uploads PNG to cloud brain
- [x] **H055** Shop-and-order playbook (reviews → pick → address)
- [x] **H056** Social-login playbook (own email, Gmail OTP or gate)
- [x] **H057** Manual QA playbook (maker/checker same session)
- [x] **H058** Generic OS playbook (any window named in the task)
- [x] **H059** Intent classifier: shop | social | qa | os | unclear
- [x] **H060** Unclear → ask_user, do not start Hands
- [x] **H061** Address parser for checkout forms
- [x] **H062** Review-reading heuristic: rating + recency + complaints
- [x] **H063** Honest 'best product' debrief in plain English

## H0 Human gates & CAPTCHA

- [x] **H064** Detect I'm-not-a-robot on OCR/title
- [x] **H065** Auto-click checkbox only if visible on latest PNG
- [x] **H066** Detect image-grid captcha → gate
- [x] **H067** Detect SMS copy → gate
- [x] **H068** Detect Google 2FA prompt → gate
- [x] **H069** Detect phone-call verify → gate
- [x] **H070** Email OTP: read visible Gmail if user asked and session open
- [x] **H071** Never invent OTP digits
- [x] **H072** Control inbox of waiting gates
- [x] **H073** ACK resumes the same session (no new browser)
- [x] **H074** Timeout → BLOCKED not FAIL
- [x] **H075** Audit who acked

## H1 Local host & Control UX

- [x] **H076** Control UI on http://127.0.0.1:8788/
- [x] **H077** Health pills Control + Worker
- [x] **H078** NL task box + optional entry URL
- [x] **H079** Predict button (no side effects)
- [x] **H080** Run cycle button (headed)
- [x] **H081** Job list + cancel
- [x] **H082** Gate list + ack
- [x] **H083** Worker heartbeat lastSeen
- [x] **H084** Live view placeholder then screenshot poll
- [x] **H085** WebRTC later (Steel pattern)
- [x] **H086** Dark UI tokens no gradient slop
- [x] **H087** en + si strings
- [x] **H088** Accessibility focus/contrast
- [x] **H089** Empty states
- [x] **H090** Keyboard shortcut to refresh

## H1 Security of a full-PC agent

- [x] **H091** Confirm destructive OS actions (delete, format, shutdown)
- [x] **H092** Deny credential stuffing / password lists
- [x] **H093** Deny 'create 100 accounts' prompts
- [x] **H094** Vault files gitignored; values never in logs
- [x] **H095** Worker bind 127.0.0.1 default
- [x] **H096** LAN bind requires token
- [x] **H097** Tenant API keys hashed at rest
- [x] **H098** Rate limit job create
- [x] **H099** Audit log start/cancel/ack
- [x] **H100** Wipe captures command
- [x] **H101** Cookie isolation between customers on shared appliance
- [x] **H102** UAC and admin elevation always gated

## H1 World absorb (lawful)

- [x] **H103** Map Claude computer_toolset members to LIQA Hands
- [x] **H104** Map OpenAI CUA screenshot-click loop to our JSON
- [x] **H105** Read Cua Windows driver limits
- [x] **H106** Read Midscene YAML as optional case format
- [x] **H107** Read Stagehand observe/act names for brain schema
- [x] **H108** Document Rainforest live-watch UX for Control
- [x] **H109** Document AskUI 3-layer in ARCHITECTURE.md
- [x] **H110** Document BrowserStack Local outbound-only
- [x] **H111** Keep NOTICE licenses current
- [x] **H112** Do not scrape authenticated proprietary apps

## H1 Examples (own PC)

- [x] **H113** Demo: Notepad type hello + screenshot
- [x] **H114** Demo: open Downloads in Explorer
- [x] **H115** Demo: search a public shop, read two reviews, stop before pay
- [x] **H116** Demo: Gmail already logged in, read subject only
- [x] **H117** Demo: Facebook only with user-supplied own creds + gates
- [x] **H118** Demo: FusionX UAT login headed (existing QA SKU)
- [x] **H119** Record each demo as a trajectory for later headed replay
- [x] **H120** Never commit demo passwords

## H2 Brain quality

- [x] **H121** qwen2.5-vl when GPU available
- [x] **H122** llava fallback
- [x] **H123** Azure OpenAI adapter on worker key
- [x] **H124** Refuse cloud in bank mode
- [x] **H125** Action schema validation
- [x] **H126** Reject raw x/y from model
- [x] **H127** Ask-user path
- [x] **H128** 20-approach honesty referee
- [x] **H129** 3-cycle revalidation
- [x] **H130** Token/cost meter
- [x] **H131** Offline scripted-steps fallback
- [x] **H132** Sinhala task restatement

## H2 Packaging local host

- [x] **H133** scripts/dev.ps1 starts Control+Worker
- [x] **H134** scripts/verify-install.ps1
- [x] **H135** Scheduled task at logon
- [x] **H136** Autologon runbook
- [x] **H137** RDP disconnect warning
- [x] **H138** Port 8788/8787 documented in README
- [x] **H139** Firewall localhost-only note
- [x] **H140** Uninstall cleans captures optionally

## H2 QA of the human agent itself

- [x] **H141** Unit: intent.predict shop vs social vs qa
- [x] **H142** Unit: classify_blocker checkbox vs hard vs sms
- [x] **H143** Unit: session forbids second goto
- [x] **H144** Unit: vault missing → not enough
- [x] **H145** Unit: job queue + cancel
- [x] **H146** Integration: control assigns only headed worker
- [x] **H147** Smoke: /health both processes
- [x] **H148** Headed self-test notepad
- [x] **H149** Negative: lock screen 503
- [x] **H150** No secret in repo grep

## H3 Polish

- [x] **H151** Favicon
- [x] **H152** Changelog for human-agent SKU
- [x] **H153** Support bundle zip no secrets
- [x] **H154** Learn-cycle after every closed general_pc job
- [x] **H155** Telemetry opt-in only
- [x] **H156** HiDPI click retry jitter
- [x] **H157** Time-box SBTM field on general jobs
- [x] **H158** PROOF debrief markdown
- [x] **H159** i18n si for Control empty states
- [x] **H160** PDF of VISION for procurement

## H3 Multi-app on one desktop

- [x] **H161** Switch apps by clicking the taskbar icon that is visible
- [x] **H162** Keep Chrome + Gmail + Facebook in one session for OTP
- [x] **H163** Do not spawn a second Chromium for maker-checker
- [x] **H164** Explorer + browser together for download-then-upload tasks
- [x] **H165** Wait for download toast before next click
- [x] **H166** Human_gate if Windows Security / SmartScreen appears
- [x] **H167** Human_gate if printer / UAC / BitLocker
- [x] **H168** Map every new window as a map node (ManualQA step 6)
- [x] **H169** Close extra popups with X only if X is OCR-visible
- [x] **H170** Refuse Win+R typed shell commands as a silent bypass of Hands

## H3 Shopping playbook depth

- [x] **H171** Search box fill + Enter
- [x] **H172** Open top N listings not only sponsored row
- [x] **H173** Read rating count vs average (honest pick)
- [x] **H174** Read 3 recent 1-star and 3 5-star reviews
- [x] **H175** Check delivery to the given postcode/address
- [x] **H176** Size/color variant if the user named one
- [x] **H177** Out of stock → next candidate, explain why
- [x] **H178** Cart review screenshot before pay
- [x] **H179** Payment page always human_gate unless user said test-card in vault
- [x] **H180** Order confirmation PNG + plain English why this SKU
- [x] **H181** Stop if checkout wants a new account the user did not request

## H3 Social + email verification depth

- [x] **H182** Facebook create vs login: follow the button that is on screen
- [x] **H183** Cookie consent click_text if visible
- [x] **H184** Birthday/gender fields only if the user supplied them
- [x] **H185** Gmail: click the visible verification mail subject
- [x] **H186** Copy code from visible body — never from an API scrape of Google
- [x] **H187** Paste code into Facebook field with delay
- [x] **H188** If Google phone prompt appears, gate immediately
- [x] **H189** After login, compose post from the user's text only
- [x] **H190** Proof PNG of the live post
- [x] **H191** Logout only if the user asked — default leave session for dual tasks
- [x] **H192** Refuse 'create accounts for these 50 emails'

## H3 Honesty, prediction, debrief

- [x] **H193** After each frame, write next-3-actions markdown
- [x] **H194** If prediction misses, log the miss — do not hide it
- [x] **H195** 20 alternate approaches counter in the job JSON
- [x] **H196** REAL BUG vs BLOCKED vs NEEDS_HUMAN labels only
- [x] **H197** Triple honesty cycle hook (ManualQA step 10)
- [x] **H198** Plain-English Sinhala debrief option
- [x] **H199** Never claim captcha solved if a gate was used
- [x] **H200** Never claim order placed without confirmation PNG
- [x] **H201** Cost/time estimate before a long shop/QA job
- [x] **H202** User can cancel mid-job without killing the browser

## H3 Local-host ops

- [x] **H203** Document ports 8788/8787 in README (keep current)
- [x] **H204** dev.ps1 reuse if already listening
- [x] **H205** smoke.ps1 hits live /health after start
- [x] **H206** Control UI auto-open optional
- [x] **H207** Worker heartbeat every 15s outbound
- [x] **H208** Alert when headed health flips to 503
- [x] **H209** Log rotation without secrets
- [x] **H210** One-command wipe of captures + jobs + gates
- [x] **H211** Backup knowledgeBase not passwords
- [x] **H212** Version endpoint both processes

_Total items: **212**_

