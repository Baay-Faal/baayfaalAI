"""
Banc de Tests Unitaires — Module du Planificateur de Tâches Autonome (core/scheduler.py).
100 % Python Standard Library (unittest).
"""

import os
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.scheduler import (
    TaskScheduler,
    ScheduledTask,
    task_backup_database,
    task_check_nodes_health,
    task_cleanup_temp_files,
    BACKUP_DIR
)


class TestTaskScheduler(unittest.TestCase):

    def setUp(self):
        self.scheduler = TaskScheduler()

    def test_01_singleton_and_defaults(self):
        s2 = TaskScheduler()
        self.assertIs(self.scheduler, s2)
        status = self.scheduler.get_status()
        self.assertGreaterEqual(status["tasks_count"], 3)

    def test_02_task_execution(self):
        executed = []

        def sample_job():
            executed.append(True)

        task = ScheduledTask("test_job", 10, sample_job)
        res = task.execute()
        self.assertTrue(res)
        self.assertEqual(len(executed), 1)
        self.assertEqual(task.run_count, 1)
        self.assertEqual(task.last_status, "SUCCESS")

    def test_03_backup_database_task(self):
        task_backup_database()
        self.assertTrue(BACKUP_DIR.exists())
        backups = list(BACKUP_DIR.glob("memory_backup_*.db"))
        self.assertGreaterEqual(len(backups), 1)

    def test_04_check_nodes_health_task(self):
        results = task_check_nodes_health()
        self.assertIsInstance(results, dict)

    def test_05_cleanup_temp_files_task(self):
        task_cleanup_temp_files()

    def test_06_add_remove_run_now(self):
        flag = {"done": False}

        def custom_task():
            flag["done"] = True

        self.scheduler.add_task("custom_unit_test_task", 100, custom_task)
        self.assertIn("custom_unit_test_task", self.scheduler.tasks)

        ok = self.scheduler.run_now("custom_unit_test_task")
        self.assertTrue(ok)
        self.assertTrue(flag["done"])

        removed = self.scheduler.remove_task("custom_unit_test_task")
        self.assertTrue(removed)
        self.assertNotIn("custom_unit_test_task", self.scheduler.tasks)


if __name__ == '__main__':
    unittest.main()
