# ManualQA 10 steps = LIQA core loop (any task)

Not a QA-only pipeline. The same ten points drive shopping, OS work, social, and UAT.

1. **Assigned task** — Restate the user’s sentence. Stop if the target is unclear.
2. **Credentials** — Request 2–3 that actually have access. Honest “not enough”. Vault gitignored.
3. **Requirements** — User story, shop URL, post text, address — whatever success means.
4. **Existing knowledge** — Xray clones, prior maps, review notes. Read-only for customer tests.
5. **Confirm preflight** — Headed desktop, one browser, entry URL once.
6. **Map** — Experience the live UI. No Pass/Fail yet. Capture every frame change.
7. **Plan** — Predicted next steps + new cases if this is QA. Sigiri pack optional.
8. **Execute** — Eyes PNG → Brain JSON → Hands Bezier/type → wait analyzable → wait frame.
9. **Evidence** — Proof PNGs, Book1 when QA, plain-English debrief always.
10. **Honesty + learn** — 20 approaches before REAL BUG; 3 cycles; harvest knowledge.

Device loop inside step 8:

`EYES (full desktop) → BRAIN (TTP/TCB/Ollama) → HANDS (mouse+keyboard) → OUTPUT (next PNG)`
