"""LOLC FusionX QA environment pack — separate overlay on LIQA Perfect-100.

Does NOT replace Perfect-100 / Sigiri Xray. It adapts LIQA to how LOLC QA
engineers actually work on lolcgroupdev (project PF / FusionX).

Evidence harvested 2026-09-16 from Atlassian as thejanad@lolctech.com.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from paths import REPO_ROOT, WORKSPACE, AGENCY_ROOT

PACK_VERSION = "2026-09-16-lolc-fusionx-v1"
PACK_ROOT = REPO_ROOT / "packaging" / "lolc"
SKILL_PATH = REPO_ROOT / "skills" / "LOLC-QA-ENVIRONMENT.md"
AGENCY_RULE = AGENCY_ROOT / ".cursor" / "rules" / "lolc-qa-environment.mdc"

SITE = {
    "cloud_id": "50681345-b1f0-46ba-875b-dde9c72f71c5",
    "jira": "https://lolcgroupdev.atlassian.net",
    "confluence_space": "FusionX",
    "project": "PF",
    "product": "FusionX",
}

GOLD = {
    "sigiri_test": "PF-59194",
    "story_shell": "PF-55248",
    "perfect100_clone": "PF-59486",
    "book1_share": "PF-58374 / PF-55248 SHARE",
    "teams_book1_seen": ["PF-59462", "PF-59472"],
    "teams_group": "AI QA Agent",
}

# Observed on live PF Tests (reporter != Thejana) 2026-09-16
QA_ENGINEERS = [
    "SIGIRI JAYASEKARA",
    "Theeksha Dumini",
    "Asirimath Karunathilake",
    "Janani Kariyawasam",
    "Chamoda sathsarani",
    "Kamila Sugathapala",
    "Methmi Buwanekaba",
    "Namal Paranamannage",
    "Nilmie Gamhewa",
    "Oshidhie Apsara Peiris",
    "Peenaka Wedamulla",
    "Piyumi Wickramarathna",
    "Rakitha Ranasinghe",
    "Sandun Samadhi Bandara",
    "Sashika Jayalath",
    "Senuri Sihara",
    "Thejana Dewmina",
    "UdariWi",
    "Yehan Jayasekara",
    "N Thanula Deemal",
    "Abdur Rahman",
]

SQUADS = ["TestCrafters", "AutoBots", "Shielders", "PulseCheckers", "DefectHunters", "GlobalSupport"]
TEAMS_GROUP = "AI QA Agent"

ENVIRONMENTS = {
    "kenya_uat": {
        "label": "Kenya UAT",
        "app": "https://uat.fusionx.biz",
        "branch_example": "Duruma Road Branch1",
        "channel_example": "GBAF",
        "tenant_tag": "cNwNb",
        "auth": "AuNEXO + Azure AD (ThejanaD@lolctech.com). MFA = Human Gate.",
    },
    "roles": {
        "maker": "ThejanaD (gitignored secrets)",
        "checker": "MethmiB (gitignored secrets)",
        "note": "Maker-checker is real FusionX control. Do not approve others' pending rows as maker.",
    },
}

CONFLUENCE = {
    "qa_process": {
        "id": "171638816",
        "url": "https://lolcgroupdev.atlassian.net/wiki/spaces/FusionX/pages/171638816/QA+Process",
        "author": "Nilmie Gamhewa",
        "observed": "Page body is a media diagram (not extractable text). Method must come from live Jira.",
    },
    "qa_common_guideline": {
        "id": "32374789",
        "url": "https://lolcgroupdev.atlassian.net/wiki/spaces/FusionX/pages/32374789/QA+Common+Guideline",
        "author": "Abdur Rahman",
        "observed": "Page exists; body empty via API. Do not invent guideline text.",
    },
}

FP_TITLE = re.compile(r"\[FP\]", re.I)
PIPE = re.compile(r"\|")
HASHTAG_BUG = re.compile(
    r"#(TestCrafters|Testcrafters|Autobots|Shielders|GlobalSupport|globalsupport|Live|UAT)\b",
    re.I,
)


def _laws_list() -> list[str]:
    return [
        "You are a new LOLC FusionX QA employee. Copy how Sigiri / TestCrafters already write on Jira PF, not a generic ISTQB lecture and not Teams chat.",
        "Site is lolcgroupdev.atlassian.net project PF. Product is FusionX (Lending, TD, CASA, IBAF, Cash, Mobile Kenya).",
        "Story / Test titles use PIPE taxonomy: Module | Feature | … | Testcase writing and execution. Gold: PF-59194.",
        "Never put [Module][Sub][FP] - Validate that … titles on FusionX PF. That is iPay/SSP style. Methmi [FP] tests exist — do not copy them onto new PF Tests.",
        "Xray Manual steps are ONLY Action | Data | Expected Result. Sigiri-simple English. ADD NEW only — never edit PF-59194 or other existing Tests.",
        "Bug titles look like: #TestCrafters#Lending Module#UAT#cNwNb | When user tries X, Y happens. Body: Issue / Steps to Reproduce / Actual / Expected. Gold example: PF-59174.",
        "Labels you will see: TestCrafters, V69_Testing, CyberDrift, LendingModule, GlobalSupport. Use the same family, do not invent new brand labels.",
        "QA clones often have empty attachments — harvest the feature story (Cloners/Relates/parent) and PDFs on the feature, not only the clone.",
        "Environments: Kenya UAT FusionX, GBAF, cNwNb, Duruma Road Branch1. Do not invent loan/receipt numbers. Use Jira-sourced data only.",
        "Maker-checker is mandatory on Pending Approve/Reject. Human Gate for Azure AD / MFA / OTP. Never print passwords.",
        "Book1 SHARE remains Perfect-100: ≥110 rows, 100% screenshots, full English columns.",
        "Honesty-20 / obvious-3 before REAL_BUG. JQL-dedupe open twins (Relates oldest). Crop + attach PNG.",
        "LIQA Perfect-100 (PF-59486) stays the execution bar. This pack only adapts language, titles, people, and FusionX environment.",
        "Confluence 'QA Process' is a diagram; do not hallucinate its boxes. Re-open the page in headed browser if the diagram is needed.",
        "The working engineers are the people on live PF Tests/Stories/Bugs (Theeksha stories, Sigiri Tests, Janani Autobots bugs, Asirimath Shielders). Train from those tickets. Teams chat is not the method.",
        "Squad hashtags on bugs: TestCrafters (Sigiri/Theeksha), Autobots (Janani CASH), Shielders (Asirimath), GlobalSupport (live).",
    ]


def status() -> dict[str, Any]:
    return {
        "ok": True,
        "pack": "lolc-fusionx",
        "version": PACK_VERSION,
        "separate_from": "LIQA Perfect-100 (still required)",
        "pack_root": str(PACK_ROOT),
        "pack_exists": PACK_ROOT.exists(),
        "skill": str(SKILL_PATH),
        "agency_rule": str(AGENCY_RULE),
        "site": SITE,
        "gold": GOLD,
        "qa_engineers_observed": QA_ENGINEERS,
        "next": "Call liqa_lolc_laws then follow packaging/lolc/PROCESS.md as a new hire.",
    }


def laws() -> dict[str, Any]:
    return {
        "ok": True,
        "pack": "lolc-fusionx",
        "version": PACK_VERSION,
        "laws": _laws_list(),
        "gold": GOLD,
        "confluence": CONFLUENCE,
        "forbidden_on_pf": [
            "[TD] [Module][FP] - Validate that …",
            "Title: [Module] [Submodule][Feature][FP]",
            "Editing or deleting existing Xray Tests",
            "Inventing OTP / loan / receipt numbers",
            "Marking Done after Book1-only without headed proof",
        ],
    }


def environment() -> dict[str, Any]:
    return {"ok": True, "site": SITE, "environments": ENVIRONMENTS, "gold": GOLD}


def people() -> dict[str, Any]:
    return {
        "ok": True,
        "role": "new LOLC FusionX QA employee",
        "learn_from": QA_ENGINEERS,
        "training_source": "jira_pf",
        "people_count": len(QA_ENGINEERS),
        "squads": SQUADS,
        "gold_writer": "SIGIRI JAYASEKARA (PF-59194)",
        "gold_story_reporter": "Theeksha Dumini (PF-55248)",
        "gold_autobots_bug": "Janani Kariyawasam (PF-59268)",
        "gold_shielders_bug": "Asirimath Karunathilake (PF-35696)",
        "process_page_author": "Nilmie Gamhewa",
        "guideline_page_author": "Abdur Rahman",
        "checker_example": "Methmi Buwanekaba / MethmiB",
        "note": "Study their PF tickets. Do not overwrite their existing Tests. Training source is Jira, not Teams.",
    }


def onboard() -> dict[str, Any]:
    steps = [
        "liqa_boot + liqa_lolc_status (this pack).",
        "Confirm Atlassian identity is thejanad@lolctech.com on lolcgroupdev (never print password).",
        "Read gold: PF-59194 (Sigiri Test), PF-55248 (Theeksha story), PF-59174 (Sigiri bug), PF-59268 (Janani Autobots), PF-35696 (Asirimath Shielders), PF-50325 (path-split Tests).",
        "Read 10 recent PF Tests by other engineers (Udari, Chamoda, Kamila, Yehan, Piyumi, Theeksha, Sigiri) — titles are pipes; Jira description is empty; steps are in Xray.",
        "Read 5 squad bugs (TestCrafters / Autobots / Shielders / GlobalSupport) — hashtag titles + Issue/Steps/Actual/Expected or screenshot + Verified in UAT.",
        "Open Confluence QA Process diagram headed if needed (API has no text).",
        "For a new KEY: liqa_fresh_task → harvest Cloners/Relates/feature attachments → path-split → Sigiri steps → UI RPA CSV import.",
        "Execute headed on Kenya UAT FusionX (maker then checker). Book1 SHARE. Dedupe bugs.",
        "Comment closeout on the Story in the same honest tone as PF-55248 comments (NOT Done until headed proof exists).",
        "Drop the Book1 SHARE xlsx into Teams group AI QA Agent the same way the 22 already do (PF-59462 / PF-59472).",
    ]
    return {
        "ok": True,
        "identity": "new employee onboarding to LOLC QA",
        "steps": steps,
        "folders": [
            str(PACK_ROOT),
            str(WORKSPACE / "knowledgeBase" / "LOLC-QA-ADAPT"),
        ],
    }


def check_test_title(title: str) -> dict[str, Any]:
    t = (title or "").strip()
    reasons: list[str] = []
    if not t:
        reasons.append("empty")
    if FP_TITLE.search(t):
        reasons.append("bracket [FP] title is forbidden on FusionX PF (use pipes)")
    if "Validate that" in t:
        reasons.append("ISTQB-lecture 'Validate that' is not Sigiri/PF tone")
    if t and not PIPE.search(t):
        reasons.append("PF Tests use Module | Feature | … pipes")
    ok = not reasons
    return {
        "ok": ok,
        "kind": "pf_test_title",
        "title": t,
        "reasons": reasons,
        "example_gold": "Lending Module | Receipt behaviors for migrated contracts  | Testcase writing and execution",
    }


def check_bug_title(title: str) -> dict[str, Any]:
    t = (title or "").strip()
    reasons: list[str] = []
    if not t:
        reasons.append("empty")
    if FP_TITLE.search(t):
        reasons.append("do not use [FP] titles on PF bugs")
    if t and not HASHTAG_BUG.search(t) and not PIPE.search(t):
        reasons.append("TestCrafters bugs usually start with #TestCrafters/#UAT/#Live tags then a pipe + failure sentence")
    ok = not reasons
    return {
        "ok": ok,
        "kind": "pf_bug_title",
        "title": t,
        "reasons": reasons,
        "example_gold": "#TestCrafters#Lending Module#UAT#cNwNb | When User Try To Proceed Cancellation Request With Internal Transfer Recipt Do Not Allow To Do The Cancellation",
    }


def knowledge_graph() -> dict[str, Any]:
    path = PACK_ROOT / "KNOWLEDGE-GRAPH.json"
    if path.exists():
        try:
            return {"ok": True, "graph": json.loads(path.read_text(encoding="utf-8"))}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e), "path": str(path)}
    return {"ok": False, "error": "graph missing", "path": str(path)}


def manifest() -> dict[str, Any]:
    files = []
    if PACK_ROOT.exists():
        files = sorted(str(p.relative_to(PACK_ROOT)).replace("\\", "/") for p in PACK_ROOT.rglob("*") if p.is_file())
    return {
        "ok": True,
        "version": PACK_VERSION,
        "root": str(PACK_ROOT),
        "files": files,
        "mcp_tools": [
            "liqa_lolc_status",
            "liqa_lolc_laws",
            "liqa_lolc_onboard",
            "liqa_lolc_environment",
            "liqa_lolc_people",
            "liqa_lolc_check_test_title",
            "liqa_lolc_check_bug_title",
            "liqa_lolc_graph",
        ],
    }
