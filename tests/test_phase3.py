"""
Banc de tests unitaires pour la Phase 3 (Sécurité & Garde-Fous).
100 % Python Standard Library (unittest, os).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.guardrails import analyze_command_safety, request_human_confirmation
from core.tools import execute_command


class TestPhase3Guardrails(unittest.TestCase):
    def test_01_blocked_dangerous_commands(self):
        dangerous_cmds = [
            "rm -rf /",
            "format c:",
            "del /s /q C:\\Windows",
            "DROP DATABASE production;",
            "shutdown -h now"
        ]

        for cmd in dangerous_cmds:
            status, reason = analyze_command_safety(cmd)
            self.assertEqual(status, "BLOCKED", f"La commande '{cmd}' aurait dû être BLOQUÉE mais a renvoyé {status}")
            self.assertIsNotNone(reason)

    def test_02_sensitive_commands(self):
        sensitive_cmds = [
            "rm temporary_file.txt",
            "del old_log.txt",
            "systemctl stop nginx",
            "kill -9 1234",
            "git reset --hard HEAD~1"
        ]

        for cmd in sensitive_cmds:
            status, reason = analyze_command_safety(cmd)
            self.assertEqual(status, "SENSITIVE", f"La commande '{cmd}' aurait dû être SENSIBLE mais a renvoyé {status}")

    def test_03_safe_commands(self):
        safe_cmds = [
            "python --version",
            "echo Hello Baay-Faal",
            "dir",
            "ls -la"
        ]

        for cmd in safe_cmds:
            status, reason = analyze_command_safety(cmd)
            self.assertEqual(status, "SAFE", f"La commande '{cmd}' aurait dû être SAFE mais a renvoyé {status}")

    def test_04_execution_blocked_by_guardrails(self):
        res = execute_command("rm -rf /")
        self.assertFalse(res["success"])
        self.assertIn("[GARDE-FOU BLOQUÉ]", res["stderr"])

    def test_05_auto_approve_environment_variable(self):
        os.environ["BAAY_AUTO_APPROVE"] = "1"
        try:
            confirmed = request_human_confirmation("rm temp_file.txt", "Test auto-approve")
            self.assertTrue(confirmed)
        finally:
            del os.environ["BAAY_AUTO_APPROVE"]


if __name__ == "__main__":
    unittest.main()
