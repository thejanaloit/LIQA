# CAPTCHA and human gates (honest)

LIQA behaves like a human on **your** PC. It does not sell a bypass factory.

| What appears on the latest screenshot | What LIQA does |
| --- | --- |
| Visible **I'm not a robot** checkbox | Click it (Bezier), wait for frame change |
| Image grid / hCaptcha puzzle / “select all buses” | **Human gate** — you solve it, then ACK |
| SMS OTP | **Human gate** — you type the SMS, or paste into the visible field |
| Google 2FA phone prompt | **Human gate** |
| Email OTP field on this PC (Gmail already open) | Type only after you (or the visible inbox) provide digits — never invent |
| Control not on the PNG | Stop and ask. Never guess x/y |

Forbidden product features:

- 2captcha / anticaptcha / DeathByCaptcha farms
- Headless account mills
- Invented OTPs
- Mass Facebook / Gmail signup as a service

Allowed example (your machine, your email, your password, you watching):

1. You say: create a Facebook account with this email/password I own, then post.
2. LIQA opens the headed browser, fills the form, clicks the visible checkbox.
3. If Google/SMS/image CAPTCHA appears, it pauses and you complete it.
4. If Gmail verification is needed, it uses Gmail **on this same session** or waits for you.
5. After login, it creates the post and saves proof PNGs.
