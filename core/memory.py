"""
Gestionnaire de Mémoire Persistante & Historique Hybride pour l'Agent Baay-Faal.
100 % Python Standard Library (sqlite3) avec tentative de connexion MySQL (XAMPP) et fallback gracieux.

Gère les sessions, les journaux d'actions (actions_log) et les connaissances (knowledge).
"""

import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_DIR = Path("data")
SQLITE_DB_PATH = DB_DIR / "memory.db"

# Configuration MySQL / XAMPP par défaut
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "baay_agent_db"
}


class BaayMemory:
    """
    Gestionnaire de persistance hybride.
    Tente la connexion vers MySQL XAMPP si disponible, sinon se rabat de façon transparente sur SQLite.
    """

    def __init__(self, db_path: Optional[Path] = None, mysql_config: Optional[Dict[str, Any]] = None):
        self.db_path = db_path if db_path is not None else SQLITE_DB_PATH
        self.mysql_config = mysql_config or MYSQL_CONFIG
        self.engine_type = "sqlite"  # 'mysql' ou 'sqlite'
        self.mysql_conn = None

        DB_DIR.mkdir(parents=True, exist_ok=True)
        self._init_backend()

    def _init_backend(self):
        """
        Tente de se connecter à MySQL. En cas d'échec ou d'absence du module, bascule sur SQLite.
        """
        # Tentative MySQL
        try:
            import mysql.connector  # type: ignore
            self.mysql_conn = mysql.connector.connect(
                host=self.mysql_config["host"],
                port=self.mysql_config["port"],
                user=self.mysql_config["user"],
                password=self.mysql_config["password"]
            )
            cursor = self.mysql_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.mysql_config['database']}` CHARACTER SET utf8mb4;")
            self.mysql_conn.database = self.mysql_config['database']
            self.engine_type = "mysql"
            print("[MÉMOIRE] Connecté au serveur MySQL (XAMPP). Engine: MySQL")
        except Exception as e:
            # Fallback SQLite
            self.engine_type = "sqlite"
            print(f"[MÉMOIRE] MySQL indisponible ({e}). Bascule automatique sur SQLite natif ({self.db_path}).")

        self._create_tables()

        # Si MySQL est actif, lancement de la synchronisation SQLite -> MySQL en tâche de fond
        if self.engine_type == "mysql" and self.db_path.exists():
            threading.Thread(target=self._sync_pending_sqlite_data, daemon=True).start()

    def _sync_pending_sqlite_data(self):
        """
        Synchronise en tâche de fond les données accumulées dans SQLite vers MySQL puis réinitialise le tampon SQLite.
        """
        try:
            if not self.db_path.exists():
                return

            sq_conn = sqlite3.connect(str(self.db_path))
            sq_cursor = sq_conn.cursor()

            # 1. Synchro knowledge
            sq_cursor.execute("SELECT key_name, value_text, category FROM knowledge")
            rows_k = sq_cursor.fetchall()

            # 2. Synchro sessions
            sq_cursor.execute("SELECT session_id, goal, created_at, status FROM sessions")
            rows_s = sq_cursor.fetchall()

            # 3. Synchro actions_log
            sq_cursor.execute("SELECT session_id, step, thought, action, tool, args, result, timestamp FROM actions_log")
            rows_a = sq_cursor.fetchall()

            sq_conn.close()

            if not rows_k and not rows_s and not rows_a:
                return

            my_conn = self._get_connection()
            my_cursor = my_conn.cursor()

            # Migration Knowledge
            for r in rows_k:
                my_cursor.execute(
                    "INSERT INTO knowledge (key_name, value_text, category) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE value_text=VALUES(value_text)",
                    (r[0], r[1], r[2])
                )

            # Migration Sessions
            for r in rows_s:
                my_cursor.execute(
                    "INSERT IGNORE INTO sessions (session_id, goal, created_at, status) VALUES (%s, %s, %s, %s)",
                    (r[0], r[1], r[2], r[3])
                )

            # Migration Actions
            for r in rows_a:
                my_cursor.execute(
                    "INSERT IGNORE INTO actions_log (session_id, step, thought, action, tool, args, result, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7])
                )

            my_conn.commit()
            my_cursor.close()
            print(f"[MÉMOIRE SYNCHRO] {len(rows_k)} faits, {len(rows_s)} sessions et {len(rows_a)} actions synchronisés de SQLite vers MySQL.")

        except Exception as e:
            print(f"[AVERTISSEMENT SYNCHRO] Impossible de synchroniser SQLite vers MySQL : {e}")

    def _get_connection(self):
        """
        Retourne une connexion active selon le moteur.
        """
        if self.engine_type == "mysql":
            try:
                import mysql.connector  # type: ignore
                if not self.mysql_conn or not self.mysql_conn.is_connected():
                    self.mysql_conn = mysql.connector.connect(**self.mysql_config)
                return self.mysql_conn
            except Exception:
                # Si MySQL a coupé entre-temps, fallback SQLite
                self.engine_type = "sqlite"
        
        return sqlite3.connect(str(self.db_path))

    def _create_tables(self):
        """
        Crée les schémas SQL pour les sessions, les logs d'action et la base de connaissances.
        """
        if self.engine_type == "sqlite":
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    goal TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'ACTIVE'
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS actions_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    step INTEGER NOT NULL,
                    thought TEXT,
                    action TEXT,
                    tool TEXT,
                    args TEXT,
                    result TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_name TEXT UNIQUE NOT NULL,
                    value_text TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_progress (
                    tech_name TEXT PRIMARY KEY,
                    level INTEGER DEFAULT 1,
                    percent INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'LOCKED',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Initialisation par défaut si vide
            cursor.execute("INSERT OR IGNORE INTO learning_progress (tech_name, level, percent, status) VALUES ('python', 1, 0, 'UNLOCKED')")
            cursor.execute("INSERT OR IGNORE INTO learning_progress (tech_name, level, percent, status) VALUES ('linux', 1, 0, 'LOCKED')")
            cursor.execute("INSERT OR IGNORE INTO learning_progress (tech_name, level, percent, status) VALUES ('fullstack', 1, 0, 'LOCKED')")
            cursor.execute("INSERT OR IGNORE INTO learning_progress (tech_name, level, percent, status) VALUES ('cpp', 1, 0, 'LOCKED')")
            cursor.execute("INSERT OR IGNORE INTO learning_progress (tech_name, level, percent, status) VALUES ('devops', 1, 0, 'LOCKED')")
            conn.commit()
            conn.close()
        else:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id VARCHAR(64) PRIMARY KEY,
                    goal TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(32) DEFAULT 'ACTIVE'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS actions_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(64) NOT NULL,
                    step INT NOT NULL,
                    thought TEXT,
                    action VARCHAR(64),
                    tool VARCHAR(64),
                    args TEXT,
                    result TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    key_name VARCHAR(128) UNIQUE NOT NULL,
                    value_text TEXT NOT NULL,
                    category VARCHAR(64) DEFAULT 'general',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_progress (
                    tech_name VARCHAR(64) PRIMARY KEY,
                    level INT DEFAULT 1,
                    percent INT DEFAULT 0,
                    status VARCHAR(32) DEFAULT 'LOCKED',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cursor.execute("INSERT IGNORE INTO learning_progress (tech_name, level, percent, status) VALUES ('python', 1, 0, 'UNLOCKED')")
            cursor.execute("INSERT IGNORE INTO learning_progress (tech_name, level, percent, status) VALUES ('linux', 1, 0, 'LOCKED')")
            cursor.execute("INSERT IGNORE INTO learning_progress (tech_name, level, percent, status) VALUES ('fullstack', 1, 0, 'LOCKED')")
            cursor.execute("INSERT IGNORE INTO learning_progress (tech_name, level, percent, status) VALUES ('cpp', 1, 0, 'LOCKED')")
            cursor.execute("INSERT IGNORE INTO learning_progress (tech_name, level, percent, status) VALUES ('devops', 1, 0, 'LOCKED')")
            conn.commit()
            cursor.close()

    def start_session(self, goal: str) -> str:
        """
        Enregistre le démarrage d'une nouvelle session de travail.
        """
        session_id = f"session_{int(time.time() * 1000)}"
        conn = self._get_connection()
        cursor = conn.cursor()

        if self.engine_type == "sqlite":
            cursor.execute("INSERT INTO sessions (session_id, goal) VALUES (?, ?)", (session_id, goal))
            conn.commit()
            conn.close()
        else:
            cursor.execute("INSERT INTO sessions (session_id, goal) VALUES (%s, %s)", (session_id, goal))
            conn.commit()
            cursor.close()

        return session_id

    def log_action(
        self,
        session_id: str,
        step: int,
        thought: str,
        action: str,
        tool: str,
        args: Dict[str, Any],
        result: Any
    ):
        """
        Journalise une étape complète de réflexion/action de l'agent.
        """
        args_str = json.dumps(args, ensure_ascii=False)
        res_str = json.dumps(result, ensure_ascii=False) if not isinstance(result, str) else result

        conn = self._get_connection()
        cursor = conn.cursor()

        if self.engine_type == "sqlite":
            cursor.execute(
                """INSERT INTO actions_log (session_id, step, thought, action, tool, args, result)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (session_id, step, thought, action, tool, args_str, res_str)
            )
            conn.commit()
            conn.close()
        else:
            cursor.execute(
                """INSERT INTO actions_log (session_id, step, thought, action, tool, args, result)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (session_id, step, thought, action, tool, args_str, res_str)
            )
            conn.commit()
            cursor.close()

    def store_knowledge(self, key: str, value: str, category: str = "general") -> bool:
        """
        Stocke ou met à jour une connaissance clé/valeur apprise par l'agent.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if self.engine_type == "sqlite":
                cursor.execute(
                    """INSERT INTO knowledge (key_name, value_text, category)
                       VALUES (?, ?, ?)
                       ON CONFLICT(key_name) DO UPDATE SET value_text=excluded.value_text, category=excluded.category""",
                    (key, value, category)
                )
                conn.commit()
                conn.close()
            else:
                cursor.execute(
                    """INSERT INTO knowledge (key_name, value_text, category)
                       VALUES (%s, %s, %s)
                       ON DUPLICATE KEY UPDATE value_text=VALUES(value_text), category=VALUES(category)""",
                    (key, value, category)
                )
                conn.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"[ERREUR MÉMOIRE] Échec du stockage de la connaissance '{key}' : {e}")
            return False

    def search_memory(self, keyword: str, limit: int = 5) -> Dict[str, Any]:
        """
        Recherche un mot-clé dans les faits appris (knowledge) et les actions passées (actions_log).
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        pattern = f"%{keyword}%"

        knowledge_results = []
        action_results = []

        try:
            if self.engine_type == "sqlite":
                # Knowledge
                cursor.execute("SELECT key_name, value_text, category FROM knowledge WHERE key_name LIKE ? OR value_text LIKE ? LIMIT ?", (pattern, pattern, limit))
                for row in cursor.fetchall():
                    knowledge_results.append({"key": row[0], "value": row[1], "category": row[2]})

                # Actions
                cursor.execute("SELECT session_id, step, thought, tool, result FROM actions_log WHERE thought LIKE ? OR result LIKE ? ORDER BY id DESC LIMIT ?", (pattern, pattern, limit))
                for row in cursor.fetchall():
                    action_results.append({"session_id": row[0], "step": row[1], "thought": row[2], "tool": row[3], "result": row[4]})
                conn.close()
            else:
                # MySQL
                cursor.execute("SELECT key_name, value_text, category FROM knowledge WHERE key_name LIKE %s OR value_text LIKE %s LIMIT %s", (pattern, pattern, limit))
                for row in cursor.fetchall():
                    knowledge_results.append({"key": row[0], "value": row[1], "category": row[2]})

                cursor.execute("SELECT session_id, step, thought, tool, result FROM actions_log WHERE thought LIKE %s OR result LIKE %s ORDER BY id DESC LIMIT %s", (pattern, pattern, limit))
                for row in cursor.fetchall():
                    action_results.append({"session_id": row[0], "step": row[1], "thought": row[2], "tool": row[3], "result": row[4]})
                cursor.close()

            return {
                "success": True,
                "engine": self.engine_type,
                "knowledge": knowledge_results,
                "past_actions": action_results
            }
        except Exception as e:
            return {"success": False, "error": str(e), "knowledge": [], "past_actions": []}

    def get_learning_status(self) -> Dict[str, Any]:
        """
        Récupère l'état de progression des langages et technologies.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        techs = []

        try:
            if self.engine_type == "sqlite":
                cursor.execute("SELECT tech_name, level, percent, status FROM learning_progress")
                for row in cursor.fetchall():
                    techs.append({"tech": row[0], "level": row[1], "percent": row[2], "status": row[3]})
                conn.close()
            else:
                cursor.execute("SELECT tech_name, level, percent, status FROM learning_progress")
                for row in cursor.fetchall():
                    techs.append({"tech": row[0], "level": row[1], "percent": row[2], "status": row[3]})
                cursor.close()

            return {"success": True, "techs": techs}
        except Exception as e:
            return {"success": False, "error": str(e), "techs": []}

    def update_learning_progress(self, tech_name: str, level: int, percent: int, status: str = "UNLOCKED") -> bool:
        """
        Met à jour la progression ou le déverrouillage d'une technologie.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if self.engine_type == "sqlite":
                cursor.execute(
                    """INSERT INTO learning_progress (tech_name, level, percent, status)
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT(tech_name) DO UPDATE SET level=excluded.level, percent=excluded.percent, status=excluded.status""",
                    (tech_name, level, percent, status)
                )
                conn.commit()
                conn.close()
            else:
                cursor.execute(
                    """INSERT INTO learning_progress (tech_name, level, percent, status)
                       VALUES (%s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE level=VALUES(level), percent=VALUES(percent), status=VALUES(status)""",
                    (tech_name, level, percent, status)
                )
                conn.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"[ERREUR MÉMOIRE] Échec de mise à jour apprentissage : {e}")
            return False


if __name__ == "__main__":
    print("--- Test rapide du système de mémoire hybride ---")
    mem = BaayMemory()
    sess_id = mem.start_session("Test initial de persistance")
    print(f"[OK] Session créée : {sess_id} (Engine: {mem.engine_type})")

    mem.store_knowledge("serveur_linux_ip", "192.168.1.50", category="réseau")
    res = mem.search_memory("192.168.1.50")
    print("[OK] Recherche mémoire :", res)
