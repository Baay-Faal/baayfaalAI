"""
Banc de tests unitaires pour l'espace Apprendre Tech & Verrouillage Monolangage.
100 % Python Standard Library (unittest, pathlib).
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.memory import BaayMemory


class TestLearnTech(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = Path("data/test_learn_memory.db")
        if cls.test_db.exists():
            try:
                os.remove(cls.test_db)
            except Exception:
                pass
        cls.memory = BaayMemory(db_path=cls.test_db)

    def test_01_initial_learning_status(self):
        res = self.memory.get_learning_status()
        self.assertTrue(res.get("success"))
        techs = res.get("techs", [])

        tech_map = {t["tech"]: t["status"] for t in techs}
        self.assertEqual(tech_map.get("python"), "UNLOCKED")
        self.assertEqual(tech_map.get("linux"), "LOCKED")
        self.assertEqual(tech_map.get("fullstack"), "LOCKED")
        self.assertEqual(tech_map.get("cpp"), "LOCKED")

    def test_02_update_progress(self):
        ok = self.memory.update_learning_progress("python", level=2, percent=40, status="UNLOCKED")
        self.assertTrue(ok)

        res = self.memory.get_learning_status()
        tech_map = {t["tech"]: t["percent"] for t in res.get("techs", [])}
        self.assertEqual(tech_map.get("python"), 40)


if __name__ == "__main__":
    unittest.main()
