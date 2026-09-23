"""
Module de Reconnaissance Vocale & Écoute (Speech-to-Text & Wake Word) pour l'Agent Baay-Faal.
100 % Python Standard Library (re, sys, os).

Permet de détecter le mot-clé d'éveil ("Baay-Faal") et de traiter les entrées vocales ou textuelles.
"""

import os
import re
import sys
from typing import Optional


class BaayListener:
    """
    Gestionnaire d'écoute et de détection de mot-clé d'éveil (Wake Word).
    """

    def __init__(self, wake_word: str = "baay faal"):
        self.wake_word = wake_word.lower()

    def contains_wake_word(self, text: str) -> bool:
        """
        Vérifie si le texte saisi ou transcrit contient le mot-clé d'éveil ("baay faal" ou "bay fall").
        """
        if not text:
            return False

        text_lower = text.lower()
        patterns = [
            r"baay[-_ ]*faal",
            r"baye[-_ ]*fall",
            r"bay[-_ ]*fall",
            r"baay[-_ ]*agent"
        ]

        for pat in patterns:
            if re.search(pat, text_lower):
                return True
        return False

    def listen_prompt(self, prompt_text: str = "[VOICE/TEXT] > ") -> Optional[str]:
        """
        Capture une entrée textuelle ou transcrite de l'utilisateur.
        """
        if not sys.stdin.isatty():
            return None

        try:
            userInput = input(prompt_text).strip()
            return userInput if userInput else None
        except (KeyboardInterrupt, EOFError):
            return None


if __name__ == "__main__":
    print("--- Test rapide de détection du Wake Word ---")
    listener = BaayListener()

    test_samples = [
        "Bonjour Baay Faal, vérifie le système",
        "Dis-moi Baye Fall quelle heure est-il ?",
        "Exécute la commande dir",
        "Baay-Agent est prêt."
    ]

    for sample in test_samples:
        detected = listener.contains_wake_word(sample)
        print(f"Échantillon : '{sample}' -> Mot-clé détecté : {detected}")
