# Generated — LIQA general-human backlog (after list 1).
from pathlib import Path

SECTIONS = [
    (
        "H0 Product law & honesty",
        [
            "Write VISION.md general PC human (not one-site bot)",
            "Write ADR-0005 general_pc vs manual_qa prompt packs",
            "Write CAPTCHA-AND-HUMAN-GATE.md click-checkbox vs pause",
            "Write MANUALQA-10-STEPS.md as the core of every task",
            "Write WORLD-SOLUTIONS.md catalog for owner study",
            "Refuse captcha-farm vendors in AUP",
            "Refuse mass account-creation SKU",
            "Own-PC own-credentials only in examples",
            "Sinhala+English NL parser for task restatement",
            "Stop-and-ask when target unclear (no hallucinated shops)",
            "100% honest job status: stepped | human_gate | blocked | done | failed",
            "Never mark done without proof PNG",
            "Predict next 3 actions after every frame",
            "Store decision log beside PNG with secrets redacted",
        ],
    ),
    (
        "H0 Eyes on full PC",
        [
            "Full-desktop PNG every frame change",
            "Optional full-display mss vs browser-viewport only",
            "Multi-monitor pick active window monitor",
            "DPI-aware screenshot downscale for brain",
            "OCR overlay optional Tesseract",
            "Foreground window title in capture metadata",
            "Cursor position recorded on every PNG",
            "Presence badge so a human sees the agent is live",
            "Calibrate 4 corners + centre at job start",
            "Refuse capture if lock screen / LogonUI",
            "Capture rotation + disk-space check",
            "PII warning in capture folder README",
        ],
    ),
    (
        "H0 Hands on OS + browser + anything",
        [
            "Bezier mouse move then click",
            "click_text from OCR never blind x/y",
            "Type with delay; passwords not paste-dumped",
            "Hotkeys (Enter, Tab, Ctrl+L forbidden after entry URL)",
            "Focus window by title substring",
            "Scroll wheel with wait_analyzable",
            "Drag-drop when both handles visible",
            "Double-click vs single-click policy",
            "Right-click context menu then click_text",
            "IME / Sinhala keyboard path",
            "File Explorer: open folder, select file, copy path",
            "Notepad/Word: type, save, proof",
            "Excel: open workbook, read cell via UI not COM-only",
            "Start Menu search then Enter",
            "Taskbar pin/app switch Alt-Tab as last resort",
            "One Chrome/Edge process; never close mid-job",
            "Entry URL once; then clicks only",
            "New tab via UI click not chrome.tabs API",
            "Address bar forbidden after entry",
            "PDF viewer in Edge as a window like any other",
            "Print dialog: human_gate (easy to wreck printers)",
            "UAC prompt: human_gate always",
        ],
    ),
    (
        "H0 Natural language → plan → run",
        [
            "POST /v1/predict returns ManualQA 10 + extras",
            "POST /v1/run one Eyes-Brain-Hands cycle",
            "Loop until done | human_gate | max_steps",
            "Local Ollama adapter with JSON action schema",
            "Fallback predicted steps if brain down",
            "Bank mode never uploads PNG to cloud brain",
            "Shop-and-order playbook (reviews → pick → address)",
            "Social-login playbook (own email, Gmail OTP or gate)",
            "Manual QA playbook (maker/checker same session)",
            "Generic OS playbook (any window named in the task)",
            "Intent classifier: shop | social | qa | os | unclear",
            "Unclear → ask_user, do not start Hands",
            "Address parser for checkout forms",
            "Review-reading heuristic: rating + recency + complaints",
            "Honest 'best product' debrief in plain English",
        ],
    ),
    (
        "H0 Human gates & CAPTCHA",
        [
            "Detect I'm-not-a-robot on OCR/title",
            "Auto-click checkbox only if visible on latest PNG",
            "Detect image-grid captcha → gate",
            "Detect SMS copy → gate",
            "Detect Google 2FA prompt → gate",
            "Detect phone-call verify → gate",
            "Email OTP: read visible Gmail if user asked and session open",
            "Never invent OTP digits",
            "Control inbox of waiting gates",
            "ACK resumes the same session (no new browser)",
            "Timeout → BLOCKED not FAIL",
            "Audit who acked",
        ],
    ),
    (
        "H1 Local host & Control UX",
        [
            "Control UI on http://127.0.0.1:8788/",
            "Health pills Control + Worker",
            "NL task box + optional entry URL",
            "Predict button (no side effects)",
            "Run cycle button (headed)",
            "Job list + cancel",
            "Gate list + ack",
            "Worker heartbeat lastSeen",
            "Live view placeholder then screenshot poll",
            "WebRTC later (Steel pattern)",
            "Dark UI tokens no gradient slop",
            "en + si strings",
            "Accessibility focus/contrast",
            "Empty states",
            "Keyboard shortcut to refresh",
        ],
    ),
    (
        "H1 Security of a full-PC agent",
        [
            "Confirm destructive OS actions (delete, format, shutdown)",
            "Deny credential stuffing / password lists",
            "Deny 'create 100 accounts' prompts",
            "Vault files gitignored; values never in logs",
            "Worker bind 127.0.0.1 default",
            "LAN bind requires token",
            "Tenant API keys hashed at rest",
            "Rate limit job create",
            "Audit log start/cancel/ack",
            "Wipe captures command",
            "Cookie isolation between customers on shared appliance",
            "UAC and admin elevation always gated",
        ],
    ),
    (
        "H1 World absorb (lawful)",
        [
            "Map Claude computer_toolset members to LIQA Hands",
            "Map OpenAI CUA screenshot-click loop to our JSON",
            "Read Cua Windows driver limits",
            "Read Midscene YAML as optional case format",
            "Read Stagehand observe/act names for brain schema",
            "Document Rainforest live-watch UX for Control",
            "Document AskUI 3-layer in ARCHITECTURE.md",
            "Document BrowserStack Local outbound-only",
            "Keep NOTICE licenses current",
            "Do not scrape authenticated proprietary apps",
        ],
    ),
    (
        "H1 Examples (own PC)",
        [
            "Demo: Notepad type hello + screenshot",
            "Demo: open Downloads in Explorer",
            "Demo: search a public shop, read two reviews, stop before pay",
            "Demo: Gmail already logged in, read subject only",
            "Demo: Facebook only with user-supplied own creds + gates",
            "Demo: FusionX UAT login headed (existing QA SKU)",
            "Record each demo as a trajectory for later headed replay",
            "Never commit demo passwords",
        ],
    ),
    (
        "H2 Brain quality",
        [
            "qwen2.5-vl when GPU available",
            "llava fallback",
            "Azure OpenAI adapter on worker key",
            "Refuse cloud in bank mode",
            "Action schema validation",
            "Reject raw x/y from model",
            "Ask-user path",
            "20-approach honesty referee",
            "3-cycle revalidation",
            "Token/cost meter",
            "Offline scripted-steps fallback",
            "Sinhala task restatement",
        ],
    ),
    (
        "H2 Packaging local host",
        [
            "scripts/dev.ps1 starts Control+Worker",
            "scripts/verify-install.ps1",
            "Scheduled task at logon",
            "Autologon runbook",
            "RDP disconnect warning",
            "Port 8788/8787 documented in README",
            "Firewall localhost-only note",
            "Uninstall cleans captures optionally",
        ],
    ),
    (
        "H2 QA of the human agent itself",
        [
            "Unit: intent.predict shop vs social vs qa",
            "Unit: classify_blocker checkbox vs hard vs sms",
            "Unit: session forbids second goto",
            "Unit: vault missing → not enough",
            "Unit: job queue + cancel",
            "Integration: control assigns only headed worker",
            "Smoke: /health both processes",
            "Headed self-test notepad",
            "Negative: lock screen 503",
            "No secret in repo grep",
        ],
    ),
    (
        "H3 Polish",
        [
            "Favicon",
            "Changelog for human-agent SKU",
            "Support bundle zip no secrets",
            "Learn-cycle after every closed general_pc job",
            "Telemetry opt-in only",
            "HiDPI click retry jitter",
            "Time-box SBTM field on general jobs",
            "PROOF debrief markdown",
            "i18n si for Control empty states",
            "PDF of VISION for procurement",
        ],
    ),
    (
        "H3 Multi-app on one desktop",
        [
            "Switch apps by clicking the taskbar icon that is visible",
            "Keep Chrome + Gmail + Facebook in one session for OTP",
            "Do not spawn a second Chromium for maker-checker",
            "Explorer + browser together for download-then-upload tasks",
            "Wait for download toast before next click",
            "Human_gate if Windows Security / SmartScreen appears",
            "Human_gate if printer / UAC / BitLocker",
            "Map every new window as a map node (ManualQA step 6)",
            "Close extra popups with X only if X is OCR-visible",
            "Refuse Win+R typed shell commands as a silent bypass of Hands",
        ],
    ),
    (
        "H3 Shopping playbook depth",
        [
            "Search box fill + Enter",
            "Open top N listings not only sponsored row",
            "Read rating count vs average (honest pick)",
            "Read 3 recent 1-star and 3 5-star reviews",
            "Check delivery to the given postcode/address",
            "Size/color variant if the user named one",
            "Out of stock → next candidate, explain why",
            "Cart review screenshot before pay",
            "Payment page always human_gate unless user said test-card in vault",
            "Order confirmation PNG + plain English why this SKU",
            "Stop if checkout wants a new account the user did not request",
        ],
    ),
    (
        "H3 Social + email verification depth",
        [
            "Facebook create vs login: follow the button that is on screen",
            "Cookie consent click_text if visible",
            "Birthday/gender fields only if the user supplied them",
            "Gmail: click the visible verification mail subject",
            "Copy code from visible body — never from an API scrape of Google",
            "Paste code into Facebook field with delay",
            "If Google phone prompt appears, gate immediately",
            "After login, compose post from the user's text only",
            "Proof PNG of the live post",
            "Logout only if the user asked — default leave session for dual tasks",
            "Refuse 'create accounts for these 50 emails'",
        ],
    ),
    (
        "H3 Honesty, prediction, debrief",
        [
            "After each frame, write next-3-actions markdown",
            "If prediction misses, log the miss — do not hide it",
            "20 alternate approaches counter in the job JSON",
            "REAL BUG vs BLOCKED vs NEEDS_HUMAN labels only",
            "Triple honesty cycle hook (ManualQA step 10)",
            "Plain-English Sinhala debrief option",
            "Never claim captcha solved if a gate was used",
            "Never claim order placed without confirmation PNG",
            "Cost/time estimate before a long shop/QA job",
            "User can cancel mid-job without killing the browser",
        ],
    ),
    (
        "H3 Local-host ops",
        [
            "Document ports 8788/8787 in README (keep current)",
            "dev.ps1 reuse if already listening",
            "smoke.ps1 hits live /health after start",
            "Control UI auto-open optional",
            "Worker heartbeat every 15s outbound",
            "Alert when headed health flips to 503",
            "Log rotation without secrets",
            "One-command wipe of captures + jobs + gates",
            "Backup knowledgeBase not passwords",
            "Version endpoint both processes",
        ],
    ),
]

OUT = Path(__file__).resolve().parents[1] / "docs" / "TODO-HUMAN.md"


def main() -> None:
    lines = [
        "# LIQA TODO-HUMAN (general PC agent)",
        "",
        "Start **after** leftover P0 on `docs/TODO.md` is moving. Core law: headed, honest gates, own-PC credentials.",
        "",
        "Status: ` [ ] ` open · `[x]` done · `[~]` in progress",
        "",
    ]
    n = 0
    for title, items in SECTIONS:
        lines.append(f"## {title}")
        lines.append("")
        for item in items:
            n += 1
            lines.append(f"- [ ] **H{n:03d}** {item}")
        lines.append("")
    lines.append(f"_Total items: **{n}**_")
    lines.append("")
    DONE_PREFIX = {
        "H001", "H002", "H003", "H004", "H005",
        "H009", "H011",
        "H013", "H014", "H015", "H016", "H020", "H021", "H024",
        "H025", "H026", "H027", "H028", "H037", "H038",
        "H047", "H048", "H049", "H050", "H051",
        "H062", "H063", "H064", "H065", "H066", "H067", "H068", "H069", "H070",
        "H076", "H080", "H081", "H082", "H083",
        "H112", "H113", "H117", "H118",
    }
    text = "\n".join(lines) + "\n"
    for hid in DONE_PREFIX:
        text = text.replace(f"- [ ] **{hid}**", f"- [x] **{hid}**", 1)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {n} items -> {OUT}")


if __name__ == "__main__":
    main()
