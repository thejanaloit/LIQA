import json
import sys
import unittest
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "control"))
import server  # noqa: E402


class _Req(server.Handler):
    def __init__(self, path: str):
        self.path = path
        self.command = "GET"
        self.headers = {}
        self.rfile = BytesIO()
        self.wfile = BytesIO()
        self.request_version = "HTTP/1.1"
        self.client_address = ("127.0.0.1", 0)
        self._code = None

    def send_response(self, code, message=None):
        self._code = code

    def send_header(self, keyword, value):
        pass

    def end_headers(self):
        pass

    def log_message(self, fmt, *args):
        pass


class ControlHealth(unittest.TestCase):
    def test_health(self):
        r = _Req("/health")
        r.do_GET()
        self.assertEqual(r._code, 200)
        r.wfile.seek(0)
        body = json.loads(r.wfile.read().decode())
        self.assertTrue(body["ok"])
        self.assertEqual(body["component"], "control")


if __name__ == "__main__":
    unittest.main()
