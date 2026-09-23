"""
Générateur de PDF Souverain Natif — Agent Baay-Faal.
100 % Python Standard Library (subprocess, pathlib, sys).

Convertit le document HTML de rapport en un fichier PDF vectoriel haute définition.
"""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
HTML_SOURCE = DOCS_DIR / "rapport_baay_faal.html"
OUTPUT_PDF = PROJECT_ROOT / "Rapport_Baay_Faal_AI.pdf"

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
]


def generate_pdf() -> bool:
    """Génère le PDF du rapport d'ingénierie Baay-Faal."""
    if not HTML_SOURCE.exists():
        print(f"[ERREUR PDF] Source HTML non trouvée : {HTML_SOURCE}")
        return False

    executable = None
    for p in EDGE_PATHS:
        if Path(p).exists():
            executable = p
            break

    if not executable:
        print("[ERREUR PDF] Aucun navigateur Edge/Chrome headless disponible pour la génération PDF.")
        return False

    print(f"[GÉNÉRATION PDF] Conversion de {HTML_SOURCE.name} vers {OUTPUT_PDF.name}...")
    cmd = [
        executable,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={OUTPUT_PDF.resolve()}",
        str(HTML_SOURCE.resolve())
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode == 0 and OUTPUT_PDF.exists():
            print(f"[SUCCÈS PDF] Document PDF généré avec succès ({OUTPUT_PDF.stat().st_size // 1024} Ko).")
            return True
        else:
            print(f"[ERREUR PDF] Code retour {res.returncode} : {res.stderr}")
            return False
    except Exception as e:
        print(f"[ERREUR PDF] Exception lors de la génération : {e}")
        return False


if __name__ == "__main__":
    success = generate_pdf()
    sys.exit(0 if success else 1)
