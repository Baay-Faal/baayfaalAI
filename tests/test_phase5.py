"""
Banc de tests unitaires pour la Phase 5 (Déploiement Autonome & Services).
100 % Python Standard Library (unittest, pathlib).
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEPLOYMENT_DIR = PROJECT_ROOT / "deployment"


class TestPhase5Deployment(unittest.TestCase):
    def test_01_deployment_files_exist(self):
        expected_files = [
            DEPLOYMENT_DIR / "install_windows_service.ps1",
            DEPLOYMENT_DIR / "baay-agent.service",
            DEPLOYMENT_DIR / "Dockerfile",
            DEPLOYMENT_DIR / "docker-compose.yml"
        ]

        for file_path in expected_files:
            self.assertTrue(file_path.exists(), f"Le fichier de déploiement n'existe pas : {file_path}")

    def test_02_dockerfile_syntax(self):
        dockerfile = DEPLOYMENT_DIR / "Dockerfile"
        content = dockerfile.read_text(encoding="utf-8")

        self.assertIn("FROM python:", content)
        self.assertIn("ENTRYPOINT", content)
        self.assertIn("main.py", content)

    def test_03_systemd_service_syntax(self):
        service_file = DEPLOYMENT_DIR / "baay-agent.service"
        content = service_file.read_text(encoding="utf-8")

        self.assertIn("[Unit]", content)
        self.assertIn("[Service]", content)
        self.assertIn("ExecStart=", content)
        self.assertIn("Restart=always", content)

    def test_04_powershell_script_syntax(self):
        ps_file = DEPLOYMENT_DIR / "install_windows_service.ps1"
        content = ps_file.read_text(encoding="utf-8")

        self.assertIn("Register-ScheduledTask", content)
        self.assertIn("BaayFaalAgentService", content)


if __name__ == "__main__":
    unittest.main()
