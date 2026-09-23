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

DOCUMENTS = [
    {
        "html": DOCS_DIR / "rapport_baay_faal.html",
        "pdf": PROJECT_ROOT / "Rapport_Baay_Faal_AI.pdf"
    },
    {
        "html": DOCS_DIR / "guide_utilisation_baay_faal.html",
        "pdf": PROJECT_ROOT / "Guide_Utilisation_Baay_Faal.pdf"
    }
]

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
]


def generate_pdf() -> bool:
    """Génère tous les documents PDF d'ingénierie Baay-Faal."""
    executable = None
    for p in EDGE_PATHS:
        if Path(p).exists():
            executable = p
            break

    if not executable:
        print("[ERREUR PDF] Aucun navigateur Edge/Chrome headless disponible pour la génération PDF.")
        return False

    all_ok = True
    for item in DOCUMENTS:
        html_file = item["html"]
        pdf_file = item["pdf"]

        if not html_file.exists():
            print(f"[ERREUR PDF] Source HTML non trouvée : {html_file}")
            all_ok = False
            continue

        print(f"[GÉNÉRATION PDF] Conversion de {html_file.name} vers {pdf_file.name}...")
        cmd = [
            executable,
            "--headless",
            "--disable-gpu",
            f"--print-to-pdf={pdf_file.resolve()}",
            str(html_file.resolve())
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode == 0 and pdf_file.exists():
                print(f"[SUCCÈS PDF] Document PDF '{pdf_file.name}' généré ({pdf_file.stat().st_size // 1024} Ko).")
            else:
                print(f"[ERREUR PDF] Échec pour {pdf_file.name} : Code {res.returncode}")
                all_ok = False
        except Exception as e:
            print(f"[ERREUR PDF] Exception pour {pdf_file.name} : {e}")
            all_ok = False

    return all_ok


if __name__ == "__main__":
    success = generate_pdf()
    sys.exit(0 if success else 1)
