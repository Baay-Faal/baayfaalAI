"""
Module de Sécurité, Garde-Fous et Mode Human-in-the-Loop pour l'Agent Baay-Faal.
100 % Python Standard Library (re, sys, os).

Filtre les commandes shell destructrices et requiert une confirmation humaine pour les actions sensibles.
"""

import os
import re
import sys
from typing import Optional, Tuple

# Commandes STRICTEMENT BLOQUÉES (Interdictions absolues)
BLOCKED_PATTERNS = [
    (r"rm\s+-(?:r|f|rf|fr)\s+[/~*]", "Suppression récursive critique de système de fichiers (rm -rf /)"),
    (r"format\s+[c-z]:", "Formatage de lecteur Windows (format C:)"),
    (r"del\s+/[sS]\s+/[qQ]", "Suppression de répertoires Windows en masse (del /s /q)"),
    (r"mkfs", "Formatage système Linux (mkfs)"),
    (r"drop\s+database", "Suppression de base de données (DROP DATABASE)"),
    (r"shutdown", "Extinction du système (shutdown)"),
    (r"reboot", "Redémarrage du système (reboot)"),
    (r"dd\s+if=", "Écriture directe de bloc bas niveau (dd if=)"),
    (r">\s*/dev/sd[a-z]", "Écriture directe sur périphérique disque")
]

# Commandes SENSIBLES (Nécessitent une validation humaine préalable)
SENSITIVE_PATTERNS = [
    (r"rm\s+", "Suppression de fichier (rm)"),
    (r"del\s+", "Suppression de fichier (del)"),
    (r"systemctl\s+(?:stop|restart|disable)", "Modification de service système Linux (systemctl)"),
    (r"net\s+stop", "Arrêt de service Windows (net stop)"),
    (r"kill\s+-9", "Arrêt forcé de processus (kill -9)"),
    (r"taskkill\s+/[fF]", "Arrêt forcé de processus Windows (taskkill /f)"),
    (r"git\s+reset\s+--hard", "Réinitialisation stricte du dépôt Git (git reset --hard)")
]


def analyze_command_safety(command: str) -> Tuple[str, Optional[str]]:
    """
    Analyse une commande et retourne son statut de sécurité ('BLOCKED', 'SENSITIVE', 'SAFE') ainsi que le motif.
    """
    cmd_lower = command.lower().strip()

    # 1. Vérification dans la liste noire des commandes bloquées
    for pattern, description in BLOCKED_PATTERNS:
        if re.search(pattern, cmd_lower, re.IGNORECASE):
            return "BLOCKED", f"Action strictement interdite : {description}"

    # 2. Vérification dans la liste des commandes sensibles
    for pattern, description in SENSITIVE_PATTERNS:
        if re.search(pattern, cmd_lower, re.IGNORECASE):
            return "SENSITIVE", f"Action sensible nécessitant confirmation : {description}"

    return "SAFE", None


def request_human_confirmation(command: str, reason: str, node_info: str = "locale") -> bool:
    """
    Demande une confirmation humaine interactive sur le terminal (Human-in-the-Loop).
    Si l'environnement n'est pas TTY (ex: test automatisé), refuse par sécurité sauf si explicitement autorisé.
    """
    # Si mode non-interactif forcé par variable d'environnement (ex: CI/Test)
    if os.environ.get("BAAY_AUTO_APPROVE") == "1":
        print(f"[GARDE-FOU AUTO-APPROVE] Action sensible autorisée automatiquement : `{command}`")
        return True

    print("\n" + "⚠️ " * 15)
    print(f" [ATTENTION GARDE-FOU BAAY-FAAL]")
    print(f" L'Agent souhaite exécuter une commande sensible sur la machine ({node_info}) :")
    print(f"   ► Commande : `{command}`")
    print(f"   ► Motif     : {reason}")
    print("⚠️ " * 15)

    # Si pas en mode console TTY interactif, on refuse
    if not sys.stdin.isatty():
        print("[GARDE-FOU] Refus automatique : Session non-interactive détectée sans BAAY_AUTO_APPROVE=1.")
        return False

    try:
        choice = input("\nAutorisez-vous l'exécution de cette commande ? (o/N) : ").strip().lower()
        if choice in ["o", "oui", "y", "yes"]:
            print("[GARDE-FOU] Action confirmée par l'utilisateur.")
            return True
        else:
            print("[GARDE-FOU] Action refusée par l'utilisateur.")
            return False
    except KeyboardInterrupt:
        print("\n[GARDE-FOU] Interruption : Action refusée.")
        return False


if __name__ == "__main__":
    print("--- Test rapide du module Guardrails ---")
    st, reas = analyze_command_safety("rm -rf /")
    print("Test rm -rf / :", st, "|", reas)

    st2, reas2 = analyze_command_safety("git status")
    print("Test git status :", st2, "|", reas2)

    st3, reas3 = analyze_command_safety("del /s /q temp.txt")
    print("Test del temp :", st3, "|", reas3)
