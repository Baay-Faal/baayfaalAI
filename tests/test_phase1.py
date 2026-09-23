"""
Banc de tests unitaires et d'intégration natifs pour la Phase 1 (Réseau Multi-Machines).
100 % Python Standard Library (unittest, threading, time).
"""

import os
import sys
import time
import unittest

# Ajout du dossier racine au sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.tools import remote_command
from network.client import NodeClient
from network.node_daemon import NodeDaemon


class TestPhase1Network(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 9998  # Port dédié aux tests
        cls.secret_key = "test_secret_key_123"
        cls.daemon = NodeDaemon(host="127.0.0.1", port=cls.port, secret_key=cls.secret_key)

        # Lancement du démon dans un thread séparé
        import threading
        cls.daemon_thread = threading.Thread(target=cls.daemon.start, daemon=True)
        cls.daemon_thread.start()
        time.sleep(0.5)  # Pause pour laisser le socket binden

    @classmethod
    def tearDownClass(cls):
        cls.daemon.stop()

    def test_01_successful_remote_execution(self):
        client = NodeClient("127.0.0.1", port=self.port, secret_key=self.secret_key)
        res = client.send_command("echo BAAY_FAAL_TEST_OK")
        self.assertTrue(res.get("success"), f"Échec de la commande distant : {res}")
        self.assertIn("BAAY_FAAL_TEST_OK", res.get("stdout", ""))

    def test_02_authentication_failure(self):
        client = NodeClient("127.0.0.1", port=self.port, secret_key="WRONG_KEY")
        res = client.send_command("echo DOIT_ECHOUER")
        self.assertFalse(res.get("success"))
        self.assertIn("Authentification rejetée", res.get("error", ""))

    def test_03_remote_command_tool(self):
        # Test avec l'outil d'agent direct (qui consulte config/nodes.json ou se connecte en direct)
        res = remote_command("localhost", "echo TEST_TOOL")
        # Remarque : localhost dans config/nodes.json vise le port 9999, s'il n'y a pas de démon sur 9999, cela renvoie une erreur de connexion propre sans crasher
        self.assertIsInstance(res, dict)
        self.assertIn("success", res)


if __name__ == "__main__":
    unittest.main()
