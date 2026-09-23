"""
Module de Synthèse Vocale Locale (Text-to-Speech) pour l'Agent Baay-Faal.
100 % Python Standard Library (subprocess, platform, re, threading).

Convertit les réponses textuelles de l'Agent en voix parlée sans aucun service cloud.
"""

import platform
import re
import subprocess
import threading
from typing import Optional


def clean_text_for_speech(text: str) -> str:
    """
    Nettoie le texte des balises markdown, des blocs de code et des caractères spéciaux
    pour une lecture audio fluide et naturelle.
    """
    if not text:
        return ""

    # Suppression des blocs de code ```...```
    cleaned = re.sub(r"```[\s\S]*?```", " Bloc de code omis. ", text)
    # Suppression du code inline `code`
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    # Suppression des titres #, ##
    cleaned = re.sub(r"#+\s*", "", cleaned)
    # Suppression des liens [texte](url)
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)
    # Suppression des caractères markdown (étoiles, tildes, tirets de puces)
    cleaned = re.sub(r"[\*\_~>|-]", " ", cleaned)
    # Réduction des espaces multiples
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


class BaaySpeaker:
    """
    Moteur TTS natif hors-ligne s'appuyant sur les capacités audio du système d'exploitation.
    """

    def __init__(self, rate: int = 0, volume: int = 100):
        self.os_type = platform.system()
        self.rate = rate      # Vitesse de lecture
        self.volume = volume  # Volume (0-100)

    def _speak_windows(self, text: str):
        """
        Synthèse vocale native Windows via PowerShell (System.Speech.Synthesis).
        """
        # Échappement des guillemets pour PowerShell
        escaped_text = text.replace('"', '""').replace("'", "''")
        ps_command = (
            f"Add-Type -AssemblyName System.Speech; "
            f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$synth.Rate = {self.rate}; "
            f"$synth.Volume = {self.volume}; "
            f"$synth.Speak('{escaped_text}');"
        )
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_command],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        except Exception as e:
            print(f"[ERREUR VOCALE] Échec PowerShell TTS : {e}")

    def _speak_linux(self, text: str):
        """
        Synthèse vocale Linux via espeak ou piper (si disponible).
        """
        try:
            subprocess.run(
                ["espeak", "-v", "fr", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        except Exception:
            print("[AVERTISSEMENT VOCAL] espeak introuvable sur le système Linux.")

    def _speak_mac(self, text: str):
        """
        Synthèse vocale macOS via la commande native 'say'.
        """
        try:
            subprocess.run(
                ["say", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        except Exception as e:
            print(f"[ERREUR VOCALE] Échec macOS say : {e}")

    def speak(self, text: str, block: bool = False):
        """
        Vocalise le texte fourni. Si block=False, s'exécute dans un thread d'arrière-plan sans bloquer la console.
        """
        cleaned_text = clean_text_for_speech(text)
        if not cleaned_text:
            return

        def _worker():
            if self.os_type == "Windows":
                self._speak_windows(cleaned_text)
            elif self.os_type == "Linux":
                self._speak_linux(cleaned_text)
            elif self.os_type == "Darwin":
                self._speak_mac(cleaned_text)
            else:
                print(f"[AVERTISSEMENT VOCAL] Système d'exploitation non pris en charge : {self.os_type}")

        if block:
            _worker()
        else:
            threading.Thread(target=_worker, daemon=True).start()


if __name__ == "__main__":
    print("--- Test rapide de la Synthèse Vocale Locale ---")
    speaker = BaaySpeaker()
    msg = "Bonjour ! Je suis l'agent Baay-Faal. Le système vocal natif est opérationnel."
    print(f"Lecture audio : '{msg}'")
    speaker.speak(msg, block=True)
    print("Test achevé.")
