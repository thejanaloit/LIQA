# Jira bug-proof comment media RPA (LIQA)

**Lock:** `2026-09-22-v2-comment-media` · Owner feedback on PF-59783

## Rule

Every REAL_BUG must show **normal PNG uploads inside an Activity comment**.

Do **not** stop at:
- filename lists in Description
- Attachments panel only (often hard to find in the new issue view)

## Exact UI path (locked)

1. Open `/browse/{BUG_KEY}`
2. Scroll to **Activity** → open comment composer
3. Click toolbar button **Add image, video, or file** (picture icon)
4. Choose PNG proof file(s)
5. Wait for media cards in the editor
6. Type a short caption → click **Save**

## Pack layout

```
outputs/<STORY>/jira-attach-pack-<BUG_KEY>/*.png
```

## Tools

| Tool | When |
|------|------|
| `liqa_attach_method` | Read locked contract (`jira_comment_add_image_video_or_file`) |
| `liqa_attach_bug_proofs` | Upload one bug or discover packs |
| `liqa_attach_end_of_run` | All packs (auto on phase 7 / learn_cycle) |

## Auto hook

1. `liqa_complete_phase(7)` → Xray EOR → **bug_proof_attach** (comment media)
2. `liqa_learn_cycle` → same

`skip_existing` defaults **false** so reviewers always get a visible comment with images.
