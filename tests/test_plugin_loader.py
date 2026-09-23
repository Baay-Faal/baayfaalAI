"""
Banc de Tests Unitaires — Module du Chargeur de Plugins Modulaire (core/plugin_loader.py).
100 % Python Standard Library (unittest).
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.plugin_loader import PluginLoader, plugin_loader_engine, load_all_plugins
from core.tools import list_loaded_plugins, reload_plugins, TOOL_REGISTRY, TOOL_SCHEMAS


class TestPluginLoader(unittest.TestCase):

    def setUp(self):
        self.loader = PluginLoader()

    def test_01_discover_sample_plugin(self):
        plugins = self.loader.discover_and_load()
        self.assertIn("comprimer_fichier_zip", plugins)
        manifest = plugins["comprimer_fichier_zip"]
        self.assertEqual(manifest.name, "comprimer_fichier_zip")
        self.assertTrue(callable(manifest.function))

    def test_02_plugin_manifest_to_dict(self):
        status = self.loader.get_status()
        self.assertEqual(status["plugins_dir"], "plugins")
        self.assertGreaterEqual(status["count"], 1)

    def test_03_sample_plugin_execution(self):
        # Création d'un fichier temporaire à comprimer
        test_file = Path(__file__).parent / "temp_plugin_test.txt"
        test_file.write_text("Contenu test pour plugin zip", encoding="utf-8")

        try:
            from plugins.sample_plugin import comprimer_fichier_zip
            res = comprimer_fichier_zip(str(test_file), "test_archive.zip")
            self.assertTrue(res["success"])
            self.assertTrue(Path(res["archive_path"]).exists())
            
            # Nettoyage archive
            if Path(res["archive_path"]).exists():
                Path(res["archive_path"]).unlink()
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_04_tools_integration_and_reload(self):
        res = list_loaded_plugins()
        self.assertTrue(res["count"] >= 1)
        self.assertIn("comprimer_fichier_zip", TOOL_REGISTRY)

        reload_res = reload_plugins()
        self.assertTrue(reload_res["count"] >= 1)


if __name__ == '__main__':
    unittest.main()
