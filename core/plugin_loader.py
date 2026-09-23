"""
Module de Chargeur de Plugins Dynamique & Modulaire — Baay-Faal Agent.
100 % Python Standard Library (importlib.util, inspect, pathlib, sys).

Charge dynamiquement les extensions Python depuis le dossier 'plugins/' 
sans modifier le code source principal de l'agent.
"""

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = PROJECT_ROOT / "plugins"


class PluginManifest:
    """Représente les métadonnées et le point d'entrée d'un plugin validé."""

    def __init__(self, name: str, description: str, parameters: Dict[str, Any], function: Callable[..., Any], file_path: str):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.function = function
        self.file_path = file_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "file_path": self.file_path
        }


class PluginLoader:
    """Chargeur et Gestionnaire de Plugins pour l'Agent Baay-Faal."""

    def __init__(self, plugins_dir: Path = PLUGINS_DIR):
        self.plugins_dir = plugins_dir
        self.loaded_plugins: Dict[str, PluginManifest] = {}

    def discover_and_load(self) -> Dict[str, PluginManifest]:
        """
        Scanne le dossier plugins/ et charge dynamiquement tous les plugins valides.
        """
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_plugins.clear()

        for file_path in self.plugins_dir.glob("*.py"):
            if file_path.name.startswith("_") or file_path.name == "__init__.py":
                continue

            manifest = self._load_single_plugin(file_path)
            if manifest:
                self.loaded_plugins[manifest.name] = manifest

        return self.loaded_plugins

    def _load_single_plugin(self, file_path: Path) -> Optional[PluginManifest]:
        """
        Charge un fichier Python unique via importlib et extrait son PLUGIN_MANIFEST.
        """
        module_name = f"baay_plugin_{file_path.stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Recherche du dictionnaire PLUGIN_MANIFEST
            manifest_dict = getattr(module, "PLUGIN_MANIFEST", None)
            if not manifest_dict or not isinstance(manifest_dict, dict):
                return None

            name = manifest_dict.get("name")
            description = manifest_dict.get("description", "Plugin personnalisé Baay-Faal")
            parameters = manifest_dict.get("parameters", {})
            func = manifest_dict.get("function")

            if not name or not callable(func):
                return None

            try:
                rel_path = str(file_path.relative_to(PROJECT_ROOT))
            except ValueError:
                rel_path = str(file_path)

            return PluginManifest(
                name=name,
                description=description,
                parameters=parameters,
                function=func,
                file_path=rel_path
            )

        except Exception as e:
            print(f"[AERVERTISSEMENT PLUGIN] Échec de chargement du plugin {file_path.name} : {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        if not self.loaded_plugins:
            self.discover_and_load()
        try:
            rel_dir = str(self.plugins_dir.relative_to(PROJECT_ROOT))
        except ValueError:
            rel_dir = str(self.plugins_dir)

        return {
            "plugins_dir": rel_dir,
            "count": len(self.loaded_plugins),
            "plugins": [p.to_dict() for p in self.loaded_plugins.values()]
        }


# Instance singleton globale
plugin_loader_engine = PluginLoader()


def load_all_plugins() -> Dict[str, PluginManifest]:
    """Point d'entrée utilitaire pour charger les plugins."""
    return plugin_loader_engine.discover_and_load()
