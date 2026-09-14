# World solutions catalog (for you to read; LIQA absorbs lawful ideas)

This is **not** a scrape of proprietary source. Links are for your own study. LIQA copies **patterns**, not code from closed products.

## Computer-use brains (pixels → mouse/keyboard)

| Name | What it is | Take for LIQA | Reject / caution |
| --- | --- | --- | --- |
| [Anthropic Computer Use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) | Screenshot + 17 tools (`left_click`, `type`, `zoom`…) on **your** VM | Action JSON schema; never hide the environment | Cloud pixels unless customer opts in |
| [OpenAI CUA / Operator](https://openai.com/index/computer-using-agent/) | GUI agent, WebArena/WebVoyager numbers | Universal screen+mouse interface | Not a headed Windows appliance; research preview limits |
| [Google Gemini Computer Use](https://docs.stagehand.dev/v3/best-practices/computer-use) | CUA mode via Stagehand | Hot-swap models | Browser-sized frames ≠ full Windows desktop |
| [Microsoft](https://docs.stagehand.dev/v3/best-practices/computer-use) | Listed in Stagehand CUA models | Enterprise IdP later | Do not send bank UAT off-box |
| [trycua/cua](https://github.com/trycua/cua) | OSS drivers, sandboxes, OSWorld benches | Windows driver notes, trajectory export | Sandbox ≠ customer’s real UAT PC |
| [zavora computer-use-mcp](https://github.com/zavora-ai/computer-use-mcp) (MIT, cloned `vendor/oss/`) | Win32 MCP, DPI ScalePlan | DPI remap, session lock | Cloud computer-use is macOS/Linux — our Hands stay Windows |

## Browser agents (web-first, often Playwright)

| Name | Take | Reject as LIQA core |
| --- | --- | --- |
| [browser-use](https://github.com/browser-use/browser-use) MIT | Agent loop: observe → act | Headless Chromium as the SKU |
| [Stagehand](https://docs.stagehand.dev) MIT | `act` / `extract` / `observe` | Playwright-first; we click the real Chrome window |
| [Midscene](https://github.com/web-infra-dev/midscene) (cloned) | GUI agent YAML flows | Do not replace headed proof |
| [Steel browser](https://github.com/steel-dev/steel-browser) Apache-2 (cloned) | Live WebRTC debug URL | We still need OS mouse, not only a remote browser |
| Playwright / Puppeteer / Selenium | Locators for **replay after headed proof** | Silent pipeline during UAT |

## Headed QA / live watch (commercial — document only)

| Name | Pattern to copy | Do not copy |
| --- | --- | --- |
| Rainforest QA | Real VM + OS mouse + customer watches | Their runner source |
| AskUI | Brain / Hands / worker-on-device 3-layer | Proprietary models |
| BrowserStack Local | **Outbound** tunnel from customer LAN | Inbound holes in the bank firewall |
| Sauce / LambdaTest | Device farm UX | Headless as default for LIQA |
| Karate CUA on-prem | LLM next to the worker | Headless Docker as the core |

## Desktop RPA / OS control

| Name | Take | Caution |
| --- | --- | --- |
| UiPath / Power Automate / Automation Anywhere | Selector + human-in-the-loop queues | Heavy, not NL-first |
| AutoHotkey / pyautogui / mss | We already wrap these via ManualQA `device_core` | Teleport clicks |
| Recursive-Control / theja-humanize | Full-desktop PNG + Bezier | Keep as Hands engine |
| OpenAdapt | Record human trajectories | Privacy of recordings |

## Auth, OTP, CAPTCHA (honest)

| Name | LIQA stance |
| --- | --- |
| Visible reCAPTCHA checkbox | Click if on the latest PNG |
| 2captcha, Anti-Captcha, CapSolver | **Forbidden** — not in the product |
| Google Authenticator / email OTP on this PC | Type digits from a **visible** field or human paste |
| SMS / Google prompt / phone call | Human gate (`docs/CAPTCHA-AND-HUMAN-GATE.md`) |

## QA process (methods, not vendors)

- ISTQB fundamental test process (scripted functional)
- Bach SBTM (charter, time-box, PROOF debrief)
- SFDPOT / CRUD / boundaries / RBAC
- Maker-checker dual control
- ManualQA 10 steps (`docs/MANUALQA-10-STEPS.md`) — **this is LIQA’s core**

## How we absorb

1. You read this catalog.
2. We clone **MIT/Apache** into gitignored `vendor/oss/` for study.
3. We write ADRs for patterns (headed, outbound-only, model-agnostic, dispatcher ≠ clicker).
4. We never vendor closed SaaS source.

Last refresh: 2026-09-10.
