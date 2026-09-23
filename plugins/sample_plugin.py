"""
Plugin Exemple pour l'Agent Baay-Faal : Compresseur de Fichiers & Répertoire.
100 % Python Standard Library (zipfile).
"""

import zipfile
from pathlib import Path
from typing import Any, Dict


def comprimer_fichier_zip(chemin_source: str, nom_archive: str = "archive.zip") -> Dict[str, Any]:
    """
    Comprime un fichier ou dossier local en fichier d'archive ZIP.
    """
    source = Path(chemin_source).resolve()
    if not source.exists():
        return {"success": False, "error": f"Fichier ou dossier source introuvable : {chemin_source}"}

    target_zip = source.parent / nom_archive
    try:
        with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if source.is_file():
                zipf.write(source, arcname=source.name)
            else:
                for root, _, files in os.walk(source):
                    for file in files:
                        full_path = Path(root) / file
                        arcname = full_path.relative_to(source.parent)
                        zipf.write(full_path, arcname=arcname)

        return {
            "success": True,
            "archive_path": str(target_zip),
            "size_bytes": target_zip.stat().st_size,
            "message": f"Archive ZIP créée avec succès : {target_zip.name}"
        }
    except Exception as e:
        return {"success": False, "error": f"Échec de compression : {str(e)}"}


import os

# Manifeste officiel d'enregistrement pour le PluginLoader Baay-Faal
PLUGIN_MANIFEST = {
    "name": "comprimer_fichier_zip",
    "description": "📦 PLUGIN ZIP COMPRESSOR : Comprime n'importe quel fichier ou dossier local au format ZIP.",
    "parameters": {
        "chemin_source": "string (chemin du fichier ou dossier à comprimer)",
        "nom_archive": "string (optionnel, 'archive.zip' par défaut)"
    },
    "function": comprimer_fichier_zip
}
