"""
Banc de Tests Unitaires — Module de Sécurité & Authentification Web (core/security.py).
100 % Python Standard Library (unittest).
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.security import (
    get_security_config,
    save_security_config,
    verify_api_key,
    generate_secure_key,
    SECURITY_FILE
)


class TestSecurity(unittest.TestCase):

    def setUp(self):
        # Sauvegarde de la config originale si présente
        self.backup_existed = SECURITY_FILE.exists()
        self.original_content = SECURITY_FILE.read_text(encoding="utf-8") if self.backup_existed else None

    def tearDown(self):
        # Restauration de l'état initial
        if self.backup_existed and self.original_content:
            SECURITY_FILE.write_text(self.original_content, encoding="utf-8")
        elif SECURITY_FILE.exists():
            SECURITY_FILE.unlink()

    def test_01_verify_api_key_disabled_by_default(self):
        save_security_config(auth_enabled=False, api_key="")
        self.assertTrue(verify_api_key(None))
        self.assertTrue(verify_api_key("some_key"))

    def test_02_verify_api_key_enabled(self):
        test_key = "baay_faal_secret_test_key_99"
        save_security_config(auth_enabled=True, api_key=test_key)

        self.assertTrue(verify_api_key(test_key))
        self.assertTrue(verify_api_key(f"  {test_key}  "))
        self.assertFalse(verify_api_key("wrong_key"))
        self.assertFalse(verify_api_key(None))
        self.assertFalse(verify_api_key(""))

    def test_03_generate_secure_key(self):
        key1 = generate_secure_key(32)
        key2 = generate_secure_key(32)
        self.assertEqual(len(key1), 32)
        self.assertNotEqual(key1, key2)


if __name__ == "__main__":
    unittest.main()
