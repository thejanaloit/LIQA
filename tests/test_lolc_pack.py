import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp"))

import lolc_pack  # noqa: E402


class LolcPackTests(unittest.TestCase):
    def test_status(self):
        s = lolc_pack.status()
        self.assertTrue(s["ok"])
        self.assertEqual(s["pack"], "lolc-fusionx")
        self.assertFalse(s.get("replaces_perfect100", False))

    def test_sigiri_pipe_title_ok(self):
        r = lolc_pack.check_test_title(
            "Lending Module | Receipt behaviors for migrated contracts  | Testcase writing and execution"
        )
        self.assertTrue(r["ok"], r)

    def test_fp_title_rejected(self):
        r = lolc_pack.check_test_title(
            "[TD] [OwnerTransferHistory][FP] - Validate that PF-58398 Manage Account 403 is not reproduced"
        )
        self.assertFalse(r["ok"])
        self.assertTrue(any("FP" in x for x in r["reasons"]))

    def test_bug_title_ok(self):
        r = lolc_pack.check_bug_title(
            "#TestCrafters#Lending Module#UAT#cNwNb | When User Try To Proceed Cancellation Request"
        )
        self.assertTrue(r["ok"], r)

    def test_laws_mentions_pipes(self):
        laws = " ".join(lolc_pack.laws()["laws"])
        self.assertIn("PIPE", laws.upper())
        self.assertIn("TestCrafters", laws)

    def test_people_from_jira(self):
        p = lolc_pack.people()
        self.assertEqual(p["training_source"], "jira_pf")
        self.assertIn("AutoBots", p["squads"])
        self.assertIn("SIGIRI JAYASEKARA", p["learn_from"])
        self.assertIn("Jira", p["note"])

    def test_autobots_bug_title_ok(self):
        r = lolc_pack.check_bug_title(
            "#Autobots#CASH#UAT | When user tries cash withdrawal Y happens"
        )
        self.assertTrue(r["ok"], r)


if __name__ == "__main__":
    unittest.main()
