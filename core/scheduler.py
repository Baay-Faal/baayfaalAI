"""
Module de Planification de Tâches Autonome & Cron Natif — Baay-Faal Agent.
100 % Python Standard Library (threading, time, datetime, shutil, pathlib, socket).

Exécute des tâches d'arrière-plan périodiques (sauvegardes, surveillance réseau, nettoyage) 24h/24.
"""

import json
import os
import shutil
import socket
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BACKUP_DIR = DATA_DIR / "backups"
CONFIG_NODES = PROJECT_ROOT / "config" / "nodes.json"
EXERCICES_DIR = PROJECT_ROOT / "exercices"


class ScheduledTask:
    """Représente une tâche planifiée individuelle."""

    def __init__(self, name: str, interval_seconds: int, func: Callable[..., Any], args: tuple = ()):
        self.name = name
        self.interval_seconds = interval_seconds
        self.func = func
        self.args = args
        self.last_run: Optional[str] = None
        self.next_run: float = time.time() + interval_seconds
        self.run_count: int = 0
        self.last_status: str = "PENDING"
        self.last_error: Optional[str] = None

    def execute(self) -> bool:
        try:
            self.func(*self.args)
            self.run_count += 1
            self.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.next_run = time.time() + self.interval_seconds
            self.last_status = "SUCCESS"
            self.last_error = None
            return True
        except Exception as e:
            self.run_count += 1
            self.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.next_run = time.time() + self.interval_seconds
            self.last_status = "FAILED"
            self.last_error = str(e)
            return False

    def to_dict(self) -> Dict[str, Any]:
        remaining = max(0, int(self.next_run - time.time()))
        return {
            "name": self.name,
            "interval_seconds": self.interval_seconds,
            "last_run": self.last_run or "Jamais",
            "next_run_in_seconds": remaining,
            "run_count": self.run_count,
            "last_status": self.last_status,
            "last_error": self.last_error
        }


# --- Routines Natives Prédéfinies ---

def task_backup_database():
    """Sauvegarde automatique de la base de données SQLite."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    db_source = DATA_DIR / "memory.db"
    if db_source.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_target = BACKUP_DIR / f"memory_backup_{timestamp}.db"
        shutil.copy2(db_source, backup_target)
        
        # Conserver uniquement les 10 plus récentes sauvegardes
        backups = sorted(BACKUP_DIR.glob("memory_backup_*.db"), key=os.path.getmtime)
        if len(backups) > 10:
            for old_b in backups[:-10]:
                try:
                    old_b.unlink()
                except Exception:
                    pass


def task_check_nodes_health() -> Dict[str, Any]:
    """Vérification réseau (Socket TCP) des nœuds listés dans config/nodes.json."""
    results = {}
    if not CONFIG_NODES.exists():
        return results

    try:
        nodes_data = json.loads(CONFIG_NODES.read_text(encoding="utf-8"))
        for node_id, info in nodes_data.items():
            ip = info.get("ip", "127.0.0.1")
            port = info.get("port", 9999)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            try:
                res = sock.connect_ex((ip, port))
                is_online = (res == 0)
                results[node_id] = "ONLINE" if is_online else "OFFLINE"
            except Exception:
                results[node_id] = "ERROR"
            finally:
                sock.close()
    except Exception as e:
        results["error"] = str(e)

    return results


def task_cleanup_temp_files():
    """Nettoyage automatique des fichiers de runner temporaires."""
    if EXERCICES_DIR.exists():
        for item in EXERCICES_DIR.glob("*.py"):
            if item.name.startswith("test_runner") or item.name.startswith("user_submission"):
                try:
                    # Si le fichier est plus vieux que 30 minutes
                    if time.time() - item.stat().st_mtime > 1800:
                        item.unlink()
                except Exception:
                    pass


class TaskScheduler:
    """Gestionnaire Singleton de Planification de Tâches en Arrière-Plan."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskScheduler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Enregistrement des routines récurrentes par défaut
        self.add_task("backup_database", 3600, task_backup_database)       # Toutes les heures
        self.add_task("check_nodes_health", 300, task_check_nodes_health)  # Toutes les 5 minutes
        self.add_task("cleanup_temp_files", 1800, task_cleanup_temp_files) # Toutes les 30 minutes

    def add_task(self, name: str, interval_seconds: int, func: Callable[..., Any], args: tuple = ()):
        task = ScheduledTask(name, interval_seconds, func, args)
        self.tasks[name] = task

    def remove_task(self, name: str) -> bool:
        if name in self.tasks:
            del self.tasks[name]
            return True
        return False

    def run_now(self, name: str) -> bool:
        if name in self.tasks:
            return self.tasks[name].execute()
        return False

    def _loop(self):
        while self._running:
            now = time.time()
            for task in list(self.tasks.values()):
                if now >= task.next_run:
                    task.execute()
            time.sleep(1.0)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="BaaySchedulerThread")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self._running,
            "tasks_count": len(self.tasks),
            "tasks": [task.to_dict() for task in self.tasks.values()]
        }


# Instance globale unique
scheduler_engine = TaskScheduler()
