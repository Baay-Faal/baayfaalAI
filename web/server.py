"""
Serveur Web HTTP & API REST natif pour l'Agent Baay-Faal.
100 % Python Standard Library (http.server, json, urllib, pathlib, sys).

Expose l'interface Command Center et les endpoints d'exécution / monitoring.
"""

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict

# Ajout du dossier racine au sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.agent import BaayAgent
from core.curriculum import PYTHON_CURRICULUM, get_lesson_by_index
from core.memory import BaayMemory, SQLITE_DB_PATH
from core.tools import system_info
from voice.speaker import BaaySpeaker

STATIC_DIR = PROJECT_ROOT / "web" / "static"
PORT = 8000


class BaayWebHandler(SimpleHTTPRequestHandler):
    """
    Gestionnaire de requêtes HTTP et API REST pour l'Agent Baay-Faal.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def _send_json(self, data: Dict[str, Any], status_code: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        """
        Routage des requêtes GET statiques et API.
        """
        if self.path == "/" or self.path == "/index.html":
            self.path = "/index.html"
            return super().do_GET()

        if self.path == "/api/status":
            mem = BaayMemory()
            sys_data = system_info()
            
            nodes_count = 0
            config_nodes = PROJECT_ROOT / "config" / "nodes.json"
            if config_nodes.exists():
                try:
                    nodes_data = json.loads(config_nodes.read_text(encoding="utf-8"))
                    nodes_count = len(nodes_data)
                except Exception:
                    pass

            status_payload = {
                "success": True,
                "agent_status": "ONLINE",
                "memory_engine": mem.engine_type,
                "system": sys_data,
                "nodes_registered": nodes_count
            }
            self._send_json(status_payload)
            return

        if self.path.startswith("/api/memory"):
            mem = BaayMemory()
            search_res = mem.search_memory("", limit=10)
            self._send_json(search_res)
            return

        if self.path.startswith("/api/learn/lesson"):
            from urllib.parse import parse_qs, urlparse
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)

            mem = BaayMemory()
            current = mem.get_learning_status()
            python_level = 1
            for t in current.get("techs", []):
                if t["tech"] == "python":
                    python_level = t.get("level", 1)
                    break

            max_unlocked_idx = max(0, python_level - 1)

            if "index" in query:
                try:
                    requested_idx = int(query["index"][0])
                except Exception:
                    requested_idx = max_unlocked_idx
            else:
                requested_idx = max_unlocked_idx

            lesson_data = get_lesson_by_index(requested_idx)

            all_lessons = [
                {
                    "index": i,
                    "id": l["id"],
                    "title": l["title"],
                    "exercise_title": l["exercise_title"],
                    "unlocked": i <= max_unlocked_idx
                } for i, l in enumerate(PYTHON_CURRICULUM)
            ]

            self._send_json({
                "success": True,
                "lesson": lesson_data,
                "current_unlocked_index": max_unlocked_idx,
                "all_lessons": all_lessons
            })
            return

        if self.path == "/api/learn/status" or self.path.startswith("/api/learn"):
            mem = BaayMemory()
            learn_data = mem.get_learning_status()
            self._send_json(learn_data)
            return

        # Interception de sécurité : Si l'URL commence par /api/ et n'existe pas, renvoyer du JSON 404 au lieu de chercher un fichier statique
        if self.path.startswith("/api/"):
            self._send_json({"success": False, "error": f"Endpoint API non trouvé : {self.path}"}, status_code=404)
            return

        # Fichiers statiques CSS / JS / Assets
        return super().do_GET()

    def do_POST(self):
        """
        Traitement des requêtes POST API.
        """
        if self.path == "/api/run":
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length).decode("utf-8")

            try:
                payload = json.loads(raw_body)
                goal = payload.get("goal", "").strip()
                use_voice = payload.get("voice", False)

                if not goal:
                    self._send_json({"success": False, "error": "L'objectif ne peut pas être vide."}, status_code=400)
                    return

                agent = BaayAgent()
                answer = agent.run(goal)

                if use_voice:
                    speaker = BaaySpeaker()
                    speaker.speak(answer, block=False)

                self._send_json({
                    "success": True,
                    "goal": goal,
                    "answer": answer
                })
            except Exception as e:
                self._send_json({"success": False, "error": f"Erreur d'exécution : {str(e)}"}, status_code=500)
            return

        if self.path == "/api/learn/verify":
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length).decode("utf-8")

            try:
                payload = json.loads(raw_body)
                tech = payload.get("tech", "python")
                user_code = payload.get("code", "")

                if tech != "python":
                    self._send_json({
                        "success": False,
                        "blocked": True,
                        "error": f"[RÈGLE D'ACIER JËF JËL] La technologie '{tech.upper()}' est verrouillée. Vous devez valider le parcours Python à 100% avant d'y accéder !"
                    })
                    return

                mem = BaayMemory()
                current = mem.get_learning_status()
                python_level = 1
                for t in current.get("techs", []):
                    if t["tech"] == "python":
                        python_level = t.get("level", 1)
                        break

                current_idx = max(0, python_level - 1)
                lesson = get_lesson_by_index(current_idx)

                # Sauvegarde du code soumis et création du runner d'isolation
                exo_dir = PROJECT_ROOT / "exercices"
                exo_dir.mkdir(exist_ok=True)

                user_file = exo_dir / "user_submission.py"
                user_file.write_text(user_code, encoding="utf-8")

                runner_file = exo_dir / "test_runner.py"
                runner_code = f"""import sys
import unittest
from pathlib import Path

sys.path.insert(0, r"{str(exo_dir)}")

import user_submission

for attr in dir(user_submission):
    if not attr.startswith("__"):
        globals()[attr] = getattr(user_submission, attr)

{lesson.get("test_suite", "")}
"""
                runner_file.write_text(runner_code, encoding="utf-8")

                # Exécution contrôlée du banc de tests natif
                import subprocess
                res = subprocess.run(
                    [sys.executable, str(runner_file)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    encoding="utf-8",
                    errors="replace"
                )

                is_success = (res.returncode == 0)
                new_percent = lesson.get("percent", 0)
                next_lesson = lesson

                if is_success:
                    next_idx = current_idx + 1
                    total_lessons = len(PYTHON_CURRICULUM)
                    new_percent = min(100, int((next_idx / total_lessons) * 100))
                    new_level = next_idx + 1
                    new_status = "COMPLETED" if new_percent >= 100 else "UNLOCKED"
                    mem.update_learning_progress("python", new_level, new_percent, new_status)

                    if new_percent >= 100:
                        mem.update_learning_progress("linux", 1, 0, "UNLOCKED")

                    next_lesson = get_lesson_by_index(next_idx)

                self._send_json({
                    "success": is_success,
                    "stdout": res.stdout,
                    "stderr": res.stderr if not is_success else "",
                    "exit_code": res.returncode,
                    "new_percent": new_percent,
                    "next_lesson": next_lesson,
                    "hint": lesson.get("hint", "") if not is_success else ""
                })

            except Exception as e:
                self._send_json({"success": False, "error": f"Erreur de vérification de code : {str(e)}"}, status_code=500)
            return

        if self.path == "/api/learn/review":
            try:
                content_len = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_len).decode('utf-8')
                data = json.loads(body)
                code_snippet = data.get("code", "")
                language = data.get("language", "python")

                from core.code_reviewer import review_code_snippet
                review_results = review_code_snippet(code_snippet, language)

                self._send_json({"success": True, "review": review_results})
            except Exception as e:
                self._send_json({"success": False, "error": f"Erreur d'analyse de code : {str(e)}"}, status_code=500)
            return

        self._send_json({"success": False, "error": "Endpoint introuvable."}, status_code=404)


def run_server(port: int = PORT):
    server_address = ("", port)
    httpd = HTTPServer(server_address, BaayWebHandler)
    print("=" * 65)
    print("      BAAY-FAAL TAKK JOUK ")
    print(f"  Disponible sur : http://localhost:{port}")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVEUR WEB] Arrêt du serveur Web.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
