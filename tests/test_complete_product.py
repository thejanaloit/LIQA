import json
import sys
import unittest
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "worker"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "control"))

import book1  # noqa: E402
import dpi  # noqa: E402
import honesty  # noqa: E402
import intent  # noqa: E402
import policy  # noqa: E402
import server  # noqa: E402


class PolicyTests(unittest.TestCase):
    def test_stuffing(self):
        self.assertFalse(policy.check_task("create 100 accounts")["ok"])

    def test_otp(self):
        self.assertFalse(policy.check_task("invent otp for facebook")["ok"])

    def test_ok_shop(self):
        self.assertTrue(policy.check_task("shop and read reviews then order to 12 Lake")["ok"])


class IntentSi(unittest.TestCase):
    def test_si_shop(self):
        p = intent.predict("කඩේ ගිහින් හොඳම එක ඇණවුම කරන්න")
        self.assertEqual(p["kind"], "shop_and_order")

    def test_unclear(self):
        p = intent.predict("hi")
        self.assertTrue(p.get("ask_user"))


class DpiBook1(unittest.TestCase):
    def test_scale(self):
        pl = dpi.scale_plan(1920, 1080)
        self.assertTrue(pl["ok"])
        x, y = dpi.to_screen(100, 100, pl)
        self.assertGreater(x, 100)

    def test_book1(self):
        r = book1.generate_book1("story", 110)
        self.assertTrue(r["ok"])
        v = book1.validate_book1(110)
        self.assertTrue(v["ok"])


class HonestyLabels(unittest.TestCase):
    def test_no_fake_order(self):
        r = honesty.refuse_fake("order_placed", {})
        self.assertFalse(r["ok"])

    def test_next3(self):
        n = honesty.next_three(["a", "b"])
        self.assertEqual(len(n), 3)


class AssignHeaded(unittest.TestCase):
    def test_job_assign_fields(self):
        class _Req(server.Handler):
            def __init__(self):
                self.path = "/v1/jobs"
                self.headers = {"Content-Length": "2"}
                self.rfile = BytesIO(b"{}")
                self.wfile = BytesIO()
                self.client_address = ("127.0.0.1", 0)
                self._code = None

            def send_response(self, code, message=None):
                self._code = code

            def send_header(self, k, v):
                pass

            def end_headers(self):
                pass

            def log_message(self, fmt, *args):
                pass

        r = _Req()
        r.do_POST()
        self.assertEqual(r._code, 201)
        r.wfile.seek(0)
        body = json.loads(r.wfile.read().decode())
        self.assertIn("assignedWorker", body)
        self.assertEqual(body["mode"], "headed")


class OpenApiAndSecrets(unittest.TestCase):
    def test_openapi_gates(self):
        p = Path(__file__).resolve().parents[1] / "docs" / "openapi.yaml"
        self.assertIn("/v1/gates", p.read_text(encoding="utf-8"))

    def test_no_key_in_env_example(self):
        t = Path(__file__).resolve().parents[1] / ".env.example"
        self.assertNotRegex(t.read_text(encoding="utf-8"), r"crsr_[a-f0-9]{20,}")

    def test_lock_headed_off(self):
        import os
        from health import headed_health

        os.environ["LIQA_HEADED"] = "0"
        try:
            h = headed_health()
            self.assertFalse(h["ok"])
        finally:
            os.environ["LIQA_HEADED"] = "1"


if __name__ == "__main__":
    unittest.main()
