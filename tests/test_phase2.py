"""
Banc de tests unitaires pour la Phase 2 (Mémoire Persistante & Hybride).
100 % Python Standard Library (unittest).
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.memory import BaayMemory, SQLITE_DB_PATH
from core.tools import recall_memory, remember_fact


class TestPhase2Memory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = Path("data/test_memory.db")
        if cls.test_db.exists():
            try:
                os.remove(cls.test_db)
            except Exception:
                pass
        cls.memory = BaayMemory(db_path=cls.test_db)

    def test_01_session_creation(self):
        sess_id = self.memory.start_session("Tester la persistance des sessions")
        self.assertTrue(sess_id.startswith("session_"))

    def test_02_action_logging(self):
        sess_id = self.memory.start_session("Session de test log")
        self.memory.log_action(
            session_id=sess_id,
            step=1,
            thought="Inspection système requise",
            action="call_tool",
            tool="system_info",
            args={},
            result={"os": "Windows"}
        )

        res = self.memory.search_memory("Inspection système")
        self.assertTrue(res["success"])
        self.assertGreaterEqual(len(res["past_actions"]), 1)

    def test_03_knowledge_storage(self):
        ok = self.memory.store_knowledge("serveur_db_ip", "192.168.1.200", category="infrastructure")
        self.assertTrue(ok)

        res = self.memory.search_memory("192.168.1.200")
        self.assertTrue(res["success"])
        self.assertEqual(len(res["knowledge"]), 1)
        self.assertEqual(res["knowledge"][0]["key"], "serveur_db_ip")

    def test_04_agent_memory_tools(self):
        save_res = remember_fact("cle_api_interne", "SECRET_XYZ_999", category="securité")
        self.assertTrue(save_res.get("success"))

        recall_res = recall_memory("SECRET_XYZ_999")
        self.assertTrue(recall_res.get("success"))
        self.assertGreaterEqual(len(recall_res.get("knowledge", [])), 1)


if __name__ == "__main__":
    unittest.main()
