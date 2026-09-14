import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "worker"))
import intent  # noqa: E402
import session  # noqa: E402
from vault import honest_enough  # noqa: E402


class IntentPredict(unittest.TestCase):
    def test_shop(self):
        p = intent.predict("Go to a shop, read reviews, order the best one to 12 Lake Road")
        self.assertEqual(p["kind"], "shop_and_order")
        self.assertEqual(len(p["steps"]), 10)
        self.assertIn("checkbox_captcha", p["honesty"])

    def test_social(self):
        p = intent.predict("Open Facebook with my email and password then make a post")
        self.assertEqual(p["kind"], "social_account")

    def test_qa(self):
        p = intent.predict("Execute the Jira UAT maker checker story")
        self.assertEqual(p["kind"], "manual_qa")

    def test_liqa_word_is_not_manual_qa(self):
        p = intent.predict("Open Notepad and type hello from LIQA 20-round cycle")
        self.assertEqual(p["kind"], "general_pc")

    def test_blocker_checkbox(self):
        self.assertEqual(intent.classify_blocker("I'm not a robot"), "checkbox_captcha")

    def test_blocker_hard(self):
        self.assertEqual(intent.classify_blocker("Select all images with traffic lights"), "hard_captcha")

    def test_vault_missing(self):
        v = honest_enough(["definitely-missing-liqa-vault"])
        self.assertFalse(v["ok"])


class SessionLock(unittest.TestCase):
    def test_goto_forbidden_after_entry(self):
        session.reset()
        session.begin("testhuman01", "https://example.com")
        session.mark_entry_loaded()
        r = session.forbid_goto()
        self.assertFalse(r["ok"])
        session.end("testhuman01")


class ControlJobCancel(unittest.TestCase):
    def test_openapi_exists(self):
        p = Path(__file__).resolve().parents[1] / "docs" / "openapi.yaml"
        self.assertTrue(p.exists())
        self.assertIn("/v1/gates", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
