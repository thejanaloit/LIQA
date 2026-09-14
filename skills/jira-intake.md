# Jira Intake role skill

Use **Atlassian MCP** (user account) — this ManualQA MCP does not store Jira passwords.

## Checklist
1. `searchJiraIssuesUsingJql` — issues assigned to current user (or sprint filter).
2. For each KEY: `getJiraIssue` — epic + story; write plain English via `mqa_save_assigned_task`.
3. Stories: Confluence / description → `mqa_save_user_story`.
4. Existing tests: “is tested by” / Xray links → `mqa_save_existing_testcase` (read-only).
5. `mqa_request_credentials` then headed login; `mqa_credentials_status(enough=…)`.
6. `mqa_announce_planning_done` after phase 1 complete.

## Gold refs
Seed with `mqa_seed_format_refs` then harvest live tone:
- Story: SSP-42118
- Test: SSP-38278 / PF-59194

## Forbidden
- Edit/delete existing Xray
- Invent issue keys or AC not in Jira
