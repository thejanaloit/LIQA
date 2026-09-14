# Device control — Teams-style remote (100%)

## Owner requirement

Take full screen / device control the same way a person gets control during a **Teams screen-share remote-control** session.

## Loop (every action)

1. **EYES** — full desktop PNG (`humanize_screenshot` / capture)  
2. **BRAIN** — vision + think (ttp/tcb); web search if unknown  
3. **HANDS** — visible Bezier mouse + keyboard (`humanize_click` / type)  
4. **WAIT** — frame change analyzable → capture again  

## Rules

- Never teleport click  
- Never guess x/y if control not visible → Ask user  
- One headed browser; entry URL once  
- Human Gate for SMS / Google 2FA / CAPTCHA  

## Tools

`humanize_device_status`, `humanize_capture`, `humanize_move`, `humanize_click`, `humanize_type`, `humanize_wait_frame_change`, `humanize_human_gate`, ManualQA monitor heartbeat.

## Research note

Remote-assistance patterns (shared desktop + controlled input) map to: capture full frame → decide → inject human-like input → verify next frame. That is ManualQA device law.
