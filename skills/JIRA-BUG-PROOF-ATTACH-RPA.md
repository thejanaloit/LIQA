# Jira bug-proof Attachments RPA (LIQA)

**Lock:** `2026-09-22` · Lesson from PF-59783 (filenames in Description ≠ visible proof)

## Rule

Every REAL_BUG must show **binary PNGs in the Jira Attachments panel**.  
Listing filenames under a “Proof” heading in the description is **not** enough.

## Pack layout

```
outputs/<STORY>/jira-attach-pack-<BUG_KEY>/*.png
```

Optional manifest: `reports/jira-attach-manifest.json`

```json
{ "PF-59783": ["reports/proof/PF-59726/cropped.png"] }
```

## Tools

| Tool | When |
|------|------|
| `liqa_attach_method` | Read locked contract |
| `liqa_attach_bug_proofs` | Attach one bug or discover packs |
| `liqa_attach_end_of_run` | All packs (also auto on phase 7 / learn_cycle) |

## Auto hook (locked)

1. `liqa_complete_phase(7)` → Xray EOR → **bug_proof_attach**
2. `liqa_learn_cycle` → same

## Method

Headed Playwright (same Chrome profile / CDP as Xray UI):

1. Open `/browse/{BUG}`
2. `input[type=file].set_input_files(paths)`
3. Verify `GET .../issue/{BUG}?fields=attachment`
4. Comment: point reviewers to **Attachments** panel
5. Idempotent: skip filenames already present

## Close gate

Do not mark Perfect-100 complete until `reports/jira-attachment-log.json` (or end-of-run last) shows `ok: true` and each bug has `attachments.length >= 1`.
