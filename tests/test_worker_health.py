import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "worker"))
from health import headed_health  # noqa: E402


class WorkerHealth(unittest.TestCase):
    def test_shape(self):
        h = headed_health()
        self.assertEqual(h["product"], "LIQA")
        self.assertFalse(h["headless_allowed"])
        self.assertEqual(h["mode"], "headed")
        self.assertIn("ok", h)
        self.assertIn("reasons", h)

    def test_headed_off_rejected(self):
        os.environ["LIQA_HEADED"] = "0"
        try:
            h = headed_health()
            self.assertFalse(h["ok"])
            self.assertTrue(any("headed=0" in r for r in h["reasons"]))
        finally:
            os.environ["LIQA_HEADED"] = "1"


if __name__ == "__main__":
    unittest.main()
