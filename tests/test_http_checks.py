"""HTTP checker tests talk only to an ephemeral loopback server."""
import http.server
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import urllib.request
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_citations import entities, fetch, match_ratio, save_source_check, suggestion
from common import sha256_file
from integrity import timestamp


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/source")
            self.end_headers()
            return
        if self.path == "/missing":
            self.send_error(404)
            return
        body = (b'x' * 3_000_010 if self.path == "/big" else
                b'<html><meta property="article:published_time" content="2026-01-01"><p>The fixture value is 31.</p></html>')
        self.send_response(200)
        self.send_header("Content-Type", "text/plain" if self.path == "/big" else "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class HttpChecksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.addClassCleanup(cls.close_server)
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def close_server(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()

    def local_fetch(self, path):
        # Explicitly bypass proxies, so these requests cannot leave loopback.
        with patch("urllib.request.urlopen", urllib.request.build_opener(urllib.request.ProxyHandler({})).open):
            return fetch(self.base + path, 2)

    def test_redirect_snapshot_metadata_and_number_match(self):
        result = self.local_fetch("/redirect")
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["final_url"], self.base + "/source")
        self.assertTrue(result["published"].startswith("2026-01-01"))
        self.assertEqual(match_ratio(*entities("The fixture value is 31."), result["text"]), "1.00")
        timestamp(result["checked_at"])
        with tempfile.TemporaryDirectory() as directory:
            save_source_check(directory, self.base + "/redirect", result, 1)
            self.assertEqual(sha256_file(result["snapshot_file"]), result["snapshot_sha256"])
            metadata = json.loads(next(Path(directory).glob("*.json")).read_text())
            self.assertEqual(metadata["requested_url"], self.base + "/redirect")
            self.assertNotIn("body", metadata)

    def test_unavailable_attempts_are_preserved_not_proven_fabrications(self):
        with tempfile.TemporaryDirectory() as directory:
            for attempt in (1, 2):
                result = self.local_fetch("/missing")
                self.assertEqual(result["status"], 404)
                self.assertIn("ověřit ručně", suggestion(result))
                save_source_check(directory, self.base + "/missing", result, attempt)
            self.assertEqual(len(list(Path(directory).glob("*.snapshot"))), 2)
            with self.assertRaises(FileExistsError):
                save_source_check(directory, self.base + "/missing", self.local_fetch("/missing"), 1)

    def test_large_response_is_explicitly_truncated(self):
        result = self.local_fetch("/big")
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["body"]), 3_000_000)


if __name__ == "__main__":
    unittest.main()
