import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "worker"))
import cycle  # noqa: E402


class Cycle20(unittest.TestCase):
    def test_twenty_eyes_off(self):
        r = cycle.run_cycle("open notepad and type hello", rounds=20, eyes=False, check_health=False)
        self.assertEqual(r["roundsCompleted"], 20)
        self.assertEqual(r["roundsTarget"], 20)
        self.assertEqual(len(r["log"]), 20)

    def test_tick_shape(self):
        rec = cycle.tick("open notepad and type hello", 3, rounds=20, eyes=False, use_hands=False, ocr=False)
        self.assertEqual(rec["round"], 3)
        self.assertEqual(rec["of"], 20)
