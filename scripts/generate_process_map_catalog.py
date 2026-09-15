#!/usr/bin/env python3
"""Generate LIQA micro-process catalog + mermaid fragments from MCP + doctrine."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"E:\LIQA")
OUT = ROOT / "artifacts" / "stable-v1" / "process-map"
OUT.mkdir(parents=True, exist_ok=True)

TOOLS = re.findall(r"^def (liqa_\w+)\(", (ROOT / "mcp" / "server.py").read_text(encoding="utf-8"), re.M)

# Every micro-process observed / required across Stable V1 chat + Perfect-100
MICRO: list[dict] = []


def mp(pid: str, name: str, phase: str, agents: list[str], tools: list[str], steps: list[str], outputs: list[str], gates: list[str] | None = None):
    MICRO.append(
        {
            "id": pid,
            "name": name,
            "phase": phase,
            "agents": agents,
            "tools": tools,
            "steps": steps,
            "outputs": outputs,
            "gates": gates or [],
        }
    )


# --- META: company birth (from chat) ---
mp("MP-000", "Connect agency-agents source", "meta-genesis", ["orchestrator"], [], ["Clone/connect msitarzewski/agency-agents"], ["agency-agents workspace"], [])
mp("MP-001", "Handover intent: company MCP for Manual QA", "meta-genesis", ["orchestrator", "product-manager"], [], ["Owner defines YouTube Manual QA analogy + 10-step doctrine"], ["owner doctrine notes"], [])
mp("MP-002", "Absorb ManualQA + QAFusionX repos", "meta-genesis", ["codebase-archaeologist", "software-architect"], [], ["Study why prior MCP slow/incomplete", "Extract skills/laws"], ["gap analysis"], [])
mp("MP-003", "Industry method research ISTQB+SBTM+29119", "meta-genesis", ["research-synthesist", "test-results-analyzer"], [], ["Map owner 10 steps → ISTQB CTFL 7"], ["PROCESS lock"], [])
mp("MP-004", "Scaffold LIQA product E:/LIQA", "meta-genesis", ["platform-engineer", "mcp-builder"], [], ["Create mcp/server.py FastMCP", "Wire Cursor mcp.json"], ["LIQA MCP"], [])
mp("MP-005", "Train agency overlays Perfect-100", "meta-genesis", ["agents-orchestrator", "learner"], ["liqa_agency_train_status"], ["scripts/train_agency_qa.py → 279 overlays"], ["packaging/industry/agency-qa-trained"], [])
mp("MP-006", "Lock Perfect-100 PF-59486", "meta-genesis", ["reality-checker", "evidence-collector"], ["liqa_learn_record"], ["Bake laws/persona v5", "SPEED-PLAYBOOK"], ["skills/PERFECT-100-PF-59486-GOLD.md"], [])
mp("MP-007", "Export Stable V1 entire chat to GitHub", "meta-genesis", ["technical-writer", "git-workflow-master"], [], ["export_stable_v1_chat", "redact secrets", "tag stable-v1"], ["artifacts/stable-v1", "GitHub release"], [])

# --- BOOT ---
mp("MP-010", "Boot LIQA session", "boot", ["orchestrator"], ["liqa_boot", "liqa_laws", "liqa_engineer_persona", "liqa_todo_list", "liqa_company_status", "liqa_product_status"], ["Load persona Perfect-100 v5", "Show ISTQB todos"], ["agents/flow-state.json"], ["persona loaded"])
mp("MP-011", "Fresh KEY memory wipe", "boot", ["orchestrator", "intake"], ["liqa_fresh_task", "liqa_self_assign"], ["Ignore prior KEY memory", "Self-assign engineer"], ["assignedTasks/<KEY>/"], [])
mp("MP-012", "Learn speed tips before work", "boot", ["learner"], ["liqa_learn_speed"], ["Read SPEED-PLAYBOOK tips"], ["planning notes"], [])
mp("MP-013", "Flow chart materialize", "boot", ["orchestrator"], ["liqa_flow_chart"], ["Write agents/FLOW-CHART.md"], ["FLOW-CHART.md"], [])

# --- PHASE 1 PLANNING ---
mp("MP-100", "Pull assigned Jira issues", "1-planning", ["intake"], ["Atlassian getJiraIssue/searchJiraIssuesUsingJql", "liqa_save_assigned_task"], ["JQL assignee=currentUser", "Plain English MD per KEY"], ["assignedTasks/<KEY>/task.md"], [])
mp("MP-101", "Jira harvest checklist open", "1-planning", ["intake"], ["liqa_jira_harvest_checklist"], ["List mandatory harvest items"], ["checklist"], [])
mp("MP-102", "Harvest KEY issue body", "1-planning", ["intake"], ["getJiraIssue", "liqa_jira_harvest_record"], ["Summary AC description links"], ["knowledgeBase/<KEY>/"], [])
mp("MP-103", "Harvest Cloners links", "1-planning", ["intake"], ["getJiraIssue", "liqa_jira_harvest_record"], ["Follow Cloners to source story"], ["knowledgeBase/<KEY>/cloners/"], [])
mp("MP-104", "Harvest Relates / Tests / is-tested-by", "1-planning", ["intake"], ["getJiraIssue", "getIssueLinkTypes"], ["Map Test links + related bugs"], ["knowledgeBase/<KEY>/links/"], [])
mp("MP-105", "Harvest epic/feature/parent", "1-planning", ["intake"], ["getJiraIssue"], ["Pull PF-50130-style feature docs"], ["knowledgeBase/<KEY>/epic/"], [])
mp("MP-106", "Download ALL attachments PDF/PNG/msg", "1-planning", ["intake", "document-generator"], ["Atlassian attachments / download scripts"], ["Save every attachment binary"], ["knowledgeBase/<KEY>/jira-attachments/"], ["attachments present OR noted empty"])
mp("MP-107", "Extract PDF process text", "1-planning", ["intake", "technical-writer"], [], ["OCR/PDF text → knowledgeBase"], ["knowledgeBase/<KEY>/pdf-text.md"], [])
mp("MP-108", "Harvest status gate until complete", "1-planning", ["intake", "orchestrator"], ["liqa_jira_harvest_record", "liqa_jira_harvest_status"], ["Loop until complete=true"], ["harvest status JSON"], ["harvest.complete=true"])
mp("MP-109", "Request 2–3 credentials", "1-planning", ["intake"], ["liqa_request_credentials"], ["Ask maker/checker/vault paths"], ["secrets request"], ["Ask mode"])
mp("MP-110", "Credentials honesty check", "1-planning", ["intake", "reality-checker"], ["liqa_credentials_status"], ["After login: enough? blockers?"], ["credentials status"], [])
mp("MP-111", "Agency mesh intake dispatch", "1-planning", ["agents-orchestrator"], ["liqa_agency_dispatch", "liqa_agency_list", "liqa_agency_trained_prompt"], ["Dispatch intake specialists parallel"], ["agents/mesh/*/"], [])
mp("MP-112", "Announce planning done", "1-planning", ["orchestrator"], ["liqa_announce_planning_done", "liqa_complete_phase"], ["Only if harvest.complete"], ["phase1 done"], ["BLOCK if harvest incomplete"])
mp("MP-113", "Heartbeat planning", "1-planning", ["orchestrator"], ["liqa_heartbeat"], ["Pulse after meaningful work"], ["heartbeat log"], [])

# --- PHASE 2 MONITORING ---
mp("MP-200", "Continuous monitoring pulse", "2-monitoring", ["orchestrator", "senior-project-manager"], ["liqa_heartbeat", "liqa_status", "liqa_todo_list", "liqa_company_status", "liqa_mesh_status"], ["Track blockers", "Never guess coords"], ["reports/ live notes"], ["Ask if control missing"])
mp("MP-201", "Stop the line on missing evidence", "2-monitoring", ["reality-checker", "orchestrator"], ["liqa_stop_the_line"], ["Block advance without proof"], ["stop reason"], [])
mp("MP-202", "Evaluate all phases regression", "2-monitoring", ["orchestrator"], ["liqa_evaluate_all"], ["Prior phase regressions block advance"], ["evaluate report"], [])

# --- PHASE 3 ANALYSIS ---
mp("MP-300", "Save user stories", "3-analysis", ["intake", "product-manager"], ["liqa_save_user_story"], ["Confluence/epic/story → MD"], ["UserStories/<KEY>/"], [])
mp("MP-301", "Clone existing Xray tests read-only", "3-analysis", ["designer", "intake"], ["liqa_save_existing_testcase", "liqa_seed_format_refs"], ["is-tested-by clones", "Never edit/delete"], ["ExistingTestCases/<KEY>/"], [])
mp("MP-302", "Harvest Jira writing tone", "3-analysis", ["designer", "technical-writer"], ["liqa_save_knowledge", "liqa_seed_format_refs"], ["Study PF-59194/PF-55248/SSP golds"], ["knowledgeBase/skills/"], [])
mp("MP-303", "Gate: harvest complete before map", "3-analysis", ["orchestrator"], ["liqa_jira_harvest_status"], ["BLOCK map if incomplete"], [], ["harvest.complete"])
mp("MP-304", "Open ONE headed browser entry URL once", "3-analysis", ["mapper", "executor"], ["liqa_browser_open", "liqa_device_status", "liqa_list_windows", "liqa_focus_window"], ["Entry URL once", "Never close mid-session"], ["agents/browser-entry.json"], [])
mp("MP-305", "Human Gate OTP/MFA if needed", "3-analysis", ["mapper"], ["liqa_human_gate", "liqa_await_otp_field", "liqa_ack_gate"], ["Never invent OTP"], ["gate ack"], ["Ask mode"])
mp("MP-306", "SBTM charter for exploratory map", "3-analysis", ["mapper"], ["liqa_sbtm_charter"], ["Time-box experience map"], ["map charter"], [])
mp("MP-307", "Device Eyes→Brain→Hands loop (map)", "3-analysis", ["mapper", "evidence-collector"], ["liqa_capture", "liqa_click", "liqa_click_text", "liqa_move", "liqa_type", "liqa_hotkey", "liqa_press", "liqa_wait_frame", "liqa_device_loop", "liqa_recursive_step", "liqa_calibrate_viewport", "liqa_viewport_click"], ["Capture full desktop", "Decide", "Visible mouse", "Wait frame"], ["reports/proof/<KEY>/map/"], [])
mp("MP-308", "Map every button/tab/dropdown", "3-analysis", ["mapper", "workflow-architect"], ["liqa_save_map_node"], ["Click X → screen Y MD", "NO Pass/Fail"], ["map/<KEY>/"], [])
mp("MP-309", "Living plan update after each screen", "3-analysis", ["mapper", "senior-project-manager"], ["liqa_set_notes", "liqa_heartbeat"], ["Update unvisited controls list"], ["map living-plan"], [])
mp("MP-310", "Round-2 miss hunt (validation/empty/error)", "3-analysis", ["mapper", "reality-checker"], ["liqa_capture", "liqa_click"], ["Same browser", "Document misses even if none"], ["map/<KEY>/round-2/"], [])
mp("MP-311", "FusionX nav recovery micro", "3-analysis", ["mapper", "executor"], ["liqa_type", "liqa_hotkey", "liqa_capture"], ["AM tile miss → one address-bar deep URL", "Blue-pixel Create New locate"], ["proof recovery PNGs"], ["same session only"])
mp("MP-312", "Minimize Excel before capture", "3-analysis", ["mapper"], ["liqa_hotkey", "liqa_focus_window"], ["Prevent Excel focus steal"], [], [])
mp("MP-313", "Complete analysis phase", "3-analysis", ["orchestrator"], ["liqa_complete_phase"], ["Map exists"], ["phase3 done"], ["map artifacts exist"])

# --- PHASE 4 DESIGN ---
mp("MP-400", "Sigiri laws load", "4-design", ["designer"], ["liqa_sigiri_laws", "liqa_xray_gold_steps", "liqa_test_case_template"], ["Action|Data|Expected Result only"], [], [])
mp("MP-401", "Split story into path parts P00…", "4-design", ["designer"], ["liqa_xray_split_paths"], ["One path pack per flow"], ["NewTestCases/<KEY>/sigiri-manual/Pxx/"], [])
mp("MP-402", "Draft steps per path", "4-design", ["designer", "sachini_story_draft equiv"], ["liqa_xray_build_manual_test", "liqa_save_new_testcase"], ["Sigiri-simple English", "PF pipe titles"], ["Pxx-steps.csv", "manual test MD"], [])
mp("MP-403", "Validate steps guard", "4-design", ["designer", "reality-checker"], ["liqa_xray_validate_steps", "liqa_xray_validate_title"], ["No decimal difference from Sigiri shape"], [], ["validate_steps pass"])
mp("MP-404", "EP/BVA/decision-table/state design", "4-design", ["designer", "statistician"], [], ["Cover empty/error/RBAC/maker-checker"], ["NewTestCases design notes"], [])
mp("MP-405", "Sufficiency loop", "4-design", ["designer", "orchestrator"], ["liqa_testcase_sufficiency"], ["Show count + enough yes/no", "Cycle until enough"], ["sufficiency JSON"], ["enough=true"])
mp("MP-406", "Agency designer dispatch parallel", "4-design", ["agents-orchestrator"], ["liqa_agency_dispatch"], ["designer + technical-writer while mapper finishes"], ["mesh assignments"], [])
mp("MP-407", "Complete design phase", "4-design", ["orchestrator"], ["liqa_complete_phase"], ["NEW cases only"], ["phase4 done"], [])

# --- PHASE 5 IMPLEMENTATION ---
mp("MP-500", "Create Jira Test issues NEW only", "5-implementation", ["designer", "intake"], ["createJiraIssue", "createIssueLink"], ["Link tests → Story", "ADD NEW only"], ["jira-created.json"], [])
mp("MP-501", "Xray UI method doctrine", "5-implementation", ["executor", "designer"], ["liqa_xray_ui_method"], ["Import→From csv→#xray-csv-file→Action*|Data|Expected Result"], [], ["never Attachments"])
mp("MP-502", "Ensure Xray/Jira headed login", "5-implementation", ["executor"], ["liqa_xray_ui_ensure_login", "liqa_human_gate"], ["Azure AD Human Gate if needed"], ["login session"], [])
mp("MP-503", "UI RPA import CSV one test", "5-implementation", ["executor"], ["liqa_xray_ui_import_csv"], ["Playwright subprocess if asyncio", "CDP 9333"], ["import log"], [])
mp("MP-504", "UI RPA import pack P00…", "5-implementation", ["executor"], ["liqa_xray_ui_import_pack"], ["force_reset if wrong steps"], ["pack log"], [])
mp("MP-505", "UI RPA import registry all packs", "5-implementation", ["executor"], ["liqa_xray_ui_import_registry", "liqa_xray_end_of_run_upload"], ["All jira-created packs"], ["registry result"], [])
mp("MP-506", "Optional Xray API path only if Client Id/Secret", "5-implementation", ["executor"], ["liqa_xray_credentials_status", "liqa_xray_set_credentials", "liqa_xray_import_csv", "liqa_xray_import_pack", "liqa_xray_import_steps"], ["Fallback only"], [], ["prefer UI RPA"])
mp("MP-507", "force_reset wrong steps micro", "5-implementation", ["executor"], ["liqa_xray_ui_import_csv"], ["Reset Current Test Steps label", "Never Esc mid-dialog"], [], [])
mp("MP-508", "Book1 sample scaffold", "5-implementation", ["book1_reporter"], ["liqa_book1_sample", "liqa_list_outputs"], ["Create outputs/<STORY>/"], ["Book1 xlsx scaffold"], [])
mp("MP-509", "Disk free check before SHARE embed", "5-implementation", ["book1_reporter", "infrastructure-maintainer"], [], ["Require ≥50MB free on workspace drive"], [], ["disk gate"])
mp("MP-510", "Complete implementation phase", "5-implementation", ["orchestrator"], ["liqa_complete_phase"], ["Tests linked + Book1 scaffold"], ["phase5 done"], [])

# --- PHASE 6 EXECUTION ---
mp("MP-600", "Role start executor", "6-execution", ["executor"], ["liqa_role_start", "liqa_role_dispatch"], ["Headed execute cases"], [], [])
mp("MP-601", "Eyes→Brain→Hands execute case step", "6-execution", ["executor", "evidence-collector"], ["liqa_capture", "liqa_click", "liqa_type", "liqa_wait_frame", "liqa_device_loop", "liqa_proof_crop"], ["Proof PNG every frame change"], ["reports/proof/<KEY>/"], [])
mp("MP-602", "CDP Playwright SPA fill when available", "6-execution", ["executor"], [], ["Prefer CDP over raw pyautogui for FusionX forms"], ["cdp session"], [])
mp("MP-603", "Maker→checker same browser session", "6-execution", ["executor"], ["liqa_type", "liqa_human_gate"], ["Logout/login inside same window", "Never new Chromium mid-flow"], [], [])
mp("MP-604", "Honesty start case", "6-execution", ["honesty_referee"], ["liqa_honesty_start"], ["case_id + defect_class"], ["honesty session"], [])
mp("MP-605", "Honesty attempt up to 20", "6-execution", ["honesty_referee", "executor"], ["liqa_honesty_attempt"], ["Distinct approaches + proof", "found-a-way ⇒ PASS"], ["attempt log"], [])
mp("MP-606", "Obvious-class 3 headed repros", "6-execution", ["honesty_referee"], ["liqa_honesty_attempt", "liqa_honesty_verdict"], ["http_5xx / blank_shell need 3 repros"], ["proof trio"], [])
mp("MP-607", "Honesty verdict", "6-execution", ["honesty_referee", "reality-checker"], ["liqa_honesty_verdict"], ["PASS | REAL_BUG | BLOCKED"], ["verdict"], ["no REAL_BUG without process"])
mp("MP-608", "Bug draft local", "6-execution", ["executor", "evidence-collector"], ["liqa_file_bug_draft", "liqa_proof_crop"], ["Crop + red highlight"], ["bugs/<KEY>/"], [])
mp("MP-609", "Bug JQL dedupe before create", "6-execution", ["executor", "reality-checker"], ["searchJiraIssuesUsingJql"], ["Same symptom/account/trace", "If twin open → Relates + comment"], [], ["dedupe gate"])
mp("MP-610", "Create Jira Bug + attach proof", "6-execution", ["executor"], ["createJiraIssue", "createIssueLink", "addCommentToJiraIssue"], ["Attach PNG", "Match harvested tone"], ["Bug KEY"], [])
mp("MP-611", "Book1 append row with embedded PNG", "6-execution", ["book1_reporter"], ["liqa_book1_append_row"], ["Full English all columns"], ["Book1 row"], ["SHARE min chars"])
mp("MP-612", "Revalidate cycle optional", "6-execution", ["honesty_referee"], ["liqa_revalidate_cycle"], ["CONFIRMED|NOT_REPRO|PARTIAL"], ["revalidate report"], [])
mp("MP-613", "Agency evidence/reality dispatch", "6-execution", ["agents-orchestrator", "evidence-collector", "reality-checker"], ["liqa_agency_dispatch"], ["Parallel evidence review"], ["mesh latest.json"], [])
mp("MP-614", "Complete execution phase", "6-execution", ["orchestrator"], ["liqa_complete_phase"], ["Proofs + honesty done"], ["phase6 done"], [])

# --- PHASE 7 COMPLETION ---
mp("MP-700", "Book1 validate SHARE gold", "7-completion", ["book1_reporter", "reality-checker"], ["liqa_book1_validate"], ["≥110 rows", "image_coverage=100%", "gold_parity_ok"], ["validate report"], ["BLOCK share on fail"])
mp("MP-701", "Honesty triple cycle close", "7-completion", ["honesty_referee"], ["liqa_honesty_verdict"], ["3 full honesty clarifications"], [], [])
mp("MP-702", "End-of-run Xray upload all packs", "7-completion", ["executor"], ["liqa_xray_end_of_run_upload", "liqa_xray_upload_after_run"], ["Subprocess Playwright"], ["upload registry"], [])
mp("MP-703", "Learn cycle + record", "7-completion", ["learner"], ["liqa_learn_cycle", "liqa_learn_record", "liqa_learn_speed", "liqa_list_skills"], ["Update SPEED-PLAYBOOK", "skills"], ["learner/speed-log.jsonl"], [])
mp("MP-704", "Story Perfect-100 closeout comment", "7-completion", ["orchestrator", "technical-writer"], ["addCommentToJiraIssue"], ["Paths + bug keys + Book1 path"], ["Jira comment"], [])
mp("MP-705", "Dedupe Relates twins finalize", "7-completion", ["executor"], ["createIssueLink", "addCommentToJiraIssue"], ["Oldest open bug wins"], [], [])
mp("MP-706", "Evaluate all + complete phase 7", "7-completion", ["orchestrator"], ["liqa_evaluate_all", "liqa_complete_phase"], ["Exit criteria"], ["phase7 done"], ["all ISTQB done"])
mp("MP-707", "Optional Perfect-100 agency retrain", "7-completion", ["agents-orchestrator", "learner"], ["liqa_agency_train_status"], ["train_agency_qa.py if doctrine changed"], ["279 overlays"], [])

# --- DEVICE ATOMIC ---
for i, (name, tools, steps) in enumerate(
    [
        ("Capture full desktop PNG", ["liqa_capture"], ["mss/full monitor", "optional OCR"]),
        ("List/focus window", ["liqa_list_windows", "liqa_focus_window"], ["Title substr match"]),
        ("Move mouse visible", ["liqa_move"], ["Bezier-style path when available"]),
        ("Click coordinates", ["liqa_click"], ["button/clicks"]),
        ("Click by visible text", ["liqa_click_text"], ["OCR/text locate"]),
        ("Type with delay", ["liqa_type"], ["interval", "optional Enter"]),
        ("Hotkey / chord / press", ["liqa_hotkey", "liqa_hotkey_chord", "liqa_press"], ["Ctrl combos"]),
        ("Wait frame change", ["liqa_wait_frame"], ["timeout"]),
        ("Calibrate viewport", ["liqa_calibrate_viewport", "liqa_viewport_click"], ["Browser content coords"]),
        ("Recursive observe-act", ["liqa_recursive_step", "liqa_device_loop"], ["intent tagged loop"]),
        ("List monitors", ["liqa_list_monitors"], ["multi-monitor"]),
        ("Proof crop red box", ["liqa_proof_crop"], ["exact defect region"]),
    ],
    start=800,
):
    mp(f"MP-{i}", f"Device atomic: {name}", "device-atomic", ["executor", "mapper"], tools, steps, ["proof/device"], [])

# --- AGENCY TRACKS ---
tracks = {
    "orchestrator": ["agents-orchestrator", "chief-of-staff", "senior-project-manager", "project-shepherd", "workflow-architect"],
    "execution": ["evidence-collector", "reality-checker", "test-results-analyzer", "performance-benchmarker", "api-tester"],
    "design": ["ui-designer", "ux-researcher", "ux-architect", "whimsy-injector", "brand-guardian"],
    "docs": ["technical-writer", "document-generator", "executive-summary-generator", "meeting-notes-specialist", "content-creator", "prompt-engineer"],
}
for track, specs in tracks.items():
    mp(
        f"MP-9{list(tracks).index(track)}0",
        f"Agency track dispatch: {track}",
        "agency-mesh",
        specs,
        ["liqa_agency_dispatch", "liqa_agency_trained_prompt", "liqa_mesh_status"],
        [f"Load Perfect-100 overlay for each specialist in {track}", "Return evidence paths + verdict only"],
        [f"agents/mesh/<id>/"],
        ["qa_trained overlay"],
    )

mp("MP-990", "Agency full roster available", "agency-mesh", ["agents-orchestrator"], ["liqa_agency_list"], ["279 Perfect-100 trained specialists"], ["agency-qa-trained-index.json"], [])
mp("MP-991", "Industry 2QA human gate ops", "ops-2qa", ["orchestrator"], [], ["2 QA humans only for gates/sign-off", "Workers execute headed"], ["control / worker APIs"], [])

# --- STABLE EXPORT ---
mp("MP-A00", "Export full chat Stable V1", "stable-export", ["technical-writer"], [], ["export_stable_v1_chat.py", "FULL-CHAT.md + raw jsonl"], ["artifacts/stable-v1/chat/"], [])
mp("MP-A01", "Redact secrets in export", "stable-export", ["senior-secops-engineer"], [], ["redact_stable_v1_chat.py"], ["redacted chat"], ["no plaintext passwords"])
mp("MP-A02", "Push GitHub tag release", "stable-export", ["git-workflow-master", "devops-automator"], [], ["commit", "tag stable-v1", "release v1.0.0-stable"], ["GitHub"], [])
mp("MP-A03", "Publish micro-process map", "stable-export", ["workflow-architect", "technical-writer"], [], ["This process-map pack"], ["artifacts/stable-v1/process-map/"], [])

catalog = {
    "product": "LIQA",
    "label": "Full micro-process catalog — Stable V1 / Perfect-100",
    "mcp_version": "2026-09-16-liqa-perfect-100-v5",
    "perfect100_ref": "PF-59486",
    "agency_train": "2026-09-16-qa-trained-perfect-100-v2",
    "agency_count": 279,
    "tool_count": len(TOOLS),
    "tools": TOOLS,
    "microprocess_count": len(MICRO),
    "microprocesses": MICRO,
    "in_process_roles": [
        "orchestrator",
        "intake",
        "mapper",
        "designer",
        "executor",
        "honesty_referee",
        "book1_reporter",
        "learner",
    ],
    "book1_columns": [
        "Area",
        "Issue",
        "Screenshot",
        "What is testing",
        "Why that failed your prediction",
        "2nd QA confirmation",
        "Simple explanation",
    ],
}

(OUT / "MICROPROCESSES.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")
print("wrote", len(MICRO), "microprocesses", "tools", len(TOOLS))
