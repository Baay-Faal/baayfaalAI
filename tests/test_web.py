"""
Banc de tests unitaires et d'intégration pour l'Interface Web Command Center.
100 % Python Standard Library (unittest, urllib.request, threading, time).
"""

import json
import os
import sys
import time
import unittest
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.memory
TEST_WEB_DB = Path(__file__).parent.parent / "data" / "test_web_memory.db"
if TEST_WEB_DB.exists():
    try:
        TEST_WEB_DB.unlink()
    except Exception:
        pass
core.memory.SQLITE_DB_PATH = TEST_WEB_DB

from web.server import BaayWebHandler, PORT, run_server
from http.server import HTTPServer
import threading


class TestWebCommandCenter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = TEST_WEB_DB

        cls.test_port = 8089
        cls.server_address = ("", cls.test_port)
        cls.httpd = HTTPServer(cls.server_address, BaayWebHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        if hasattr(cls, 'test_db') and cls.test_db.exists():
            try:
                cls.test_db.unlink()
            except Exception:
                pass

    def test_01_index_html_static_serving(self):
        url = f"http://127.0.0.1:{self.test_port}/"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            content = response.read().decode("utf-8")
            self.assertIn("BAAY-FAAL", content)
            self.assertIn("Poppins", content)

    def test_02_api_status_endpoint(self):
        url = f"http://127.0.0.1:{self.test_port}/api/status"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertTrue(data.get("success"))
            self.assertEqual(data.get("agent_status"), "ONLINE")

    def test_03_api_memory_endpoint(self):
        url = f"http://127.0.0.1:{self.test_port}/api/memory"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertTrue(data.get("success"))

    def test_04_api_learn_status(self):
        url = f"http://127.0.0.1:{self.test_port}/api/learn/status"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertTrue(data.get("success"))
            self.assertGreaterEqual(len(data.get("techs", [])), 1)

    def test_05_api_learn_verify_code_execution(self):
        from core.memory import BaayMemory
        mem = BaayMemory(db_path=self.test_db)
        mem.update_learning_progress("python", 1, 0, "UNLOCKED")

        url = f"http://127.0.0.1:{self.test_port}/api/learn/verify"
        code_solution = "def calculer_budget(revenu, depenses):\n    return revenu - depenses\n"
        payload = json.dumps({
            "tech": "python",
            "code": code_solution
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertTrue(data.get("success"), f"Échec de vérification du code : {data}")
            self.assertEqual(data.get("new_percent"), 8)


if __name__ == "__main__":
    unittest.main()
