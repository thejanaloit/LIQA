# VISION — LIQA as a complete human on this PC

LIQA is **not** a single bot for one website. It is a headed **human substitute** for whatever this Windows PC can already do: browser, Explorer, Notepad, Excel, Chrome, Outlook, UAT, shopping, QA.

## What you asked for (kept)

- Natural language in. Understand intent. Predict the next steps. Execute them.
- Control **OS + browser + whatever is on screen** in a format a human uses (mouse, keyboard, wait, look).
- Example: go to a shop, read reviews, pick the honestly best item, order to an address.
- Example: use an email/password **you provided for your own account**, complete verifications (Gmail on this PC or human gate), then post.
- “I’m not a robot” / CAPTCHA: click the visible checkbox; pause for hard puzzles and phone 2FA.
- Think like a QA engineer + software engineer + someone who can go around a wall — with **honest** answers, not fake success.
- Core idea follows ManualQA’s 10 steps.
- Locally hosted (this machine: Control `:8788`, Worker `:8787`).
- World solutions catalog for you to read; LIQA absorbs lawful ideas.

## Honest completeness (not a lie about “no limits”)

The **goal** is full-PC human behaviour. Real gates we will not fake:

- Hard image CAPTCHA, SMS, Google prompt, phone call → you.
- Invisible controls → ask, never hallucinate clicks.
- Other people’s accounts / credential stuffing / captcha farms → refused.
- Headless silent Chromium as the product → refused.

That is 100% honesty, which you also required.

## Architecture (same product, wider brain)

```
You (plain English)
    → Control UI :8788 (queue, gates, watch)
        → Worker :8787 on this interactive desktop
            → Eyes (PNG) → Brain (local Ollama / optional cloud) → Hands (Bezier + keys)
            → Chrome / Explorer / any window
```

## Status after this slice

Previous 230-todo list is **in progress, not finished**. This vision’s backlog is `docs/TODO-HUMAN.md` (200+). Start those after more of list 1 is done — this turn finished leftover P0 Hands/Control/UI/gates and locally hosted the servers.
