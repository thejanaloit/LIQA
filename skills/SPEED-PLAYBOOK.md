# LIQA Speed Playbook

Learned shortcuts from real headed QA rounds (PF-55248 / PF-59194).

## Seed — PF-55248 / PF-59194

- WORKED (PF-55248): Build Book1 only from headed proof PNGs; validate SHARE parity (≥110 rows, 100% images, full English).
- WORKED (PF-59194): Prefer Playwright CDP attached to live Edge over raw pyautogui for FusionX SPA forms.
- WORKED (PF-59194): Minimize Excel before every capture — Excel steals focus and poisons proof.
- WORKED (nav): Expand Loan Origination → Transaction Management by visible text; wait splash gone before next click.
- AVOID: Inventing receipt/account numbers — pull from Jira/Xray evidence or mark BLOCKED.
- AVOID: Closing the browser between maker and checker — same headed session.
- TECHNIQUE: Human Gate only for Azure AD / OTP splash; do not pause for ordinary clicks.
- TECHNIQUE: Dispatch intake + designer specialists in parallel via agency mesh while mapper runs headed.
- TECHNIQUE: Call liqa_learn_speed at start of every new KEY.

## Round 2026-09-14 05:27 UTC
- WORKED (PF-55248): CDP+Playwright+minimize Excel
- AVOID (PF-55248): pyautogui SPA focus loss
