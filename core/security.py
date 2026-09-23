"""
Module de Sécurité & Authentification — Agent Baay-Faal.
100 % Python Standard Library (os, json, secrets, pathlib).

Gère les clés d'API et la vérification constante par comparaison à temps constant (secrets.compare_digest).
"""

import json
import os
import secrets
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
SECURITY_FILE = CONFIG_DIR / "security.json"


def get_security_config() -> dict:
    """Lit la configuration de sécurité depuis l'environnement ou config/security.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    env_key = os.environ.get("BAAY_WEB_API_KEY")
    if env_key:
        return {
            "auth_enabled": env_key.lower() != "none",
            "api_key": env_key
        }

    if SECURITY_FILE.exists():
        try:
            return json.loads(SECURITY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Configuration par défaut
    default_config = {
        "auth_enabled": False,
        "api_key": ""
    }
    return default_config


def save_security_config(auth_enabled: bool, api_key: str) -> bool:
    """Enregistre la configuration de sécurité dans config/security.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = {
        "auth_enabled": auth_enabled,
        "api_key": api_key.strip()
    }
    try:
        SECURITY_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception as e:
        print(f"[ERREUR SÉCURITÉ] Impossible de sauvegarder security.json : {e}")
        return False


def verify_api_key(provided_key: Optional[str]) -> bool:
    """
    Vérifie la clé fournie en comparaison à temps constant.
    Retourne True si l'auth est désactivée ou si la clé est valide.
    """
    config = get_security_config()
    if not config.get("auth_enabled", False):
        return True

    expected_key = config.get("api_key", "").strip()
    if not expected_key:
        # Auth activée mais aucune clé définie -> accès refusé par sécurité
        return False

    if not provided_key:
        return False

    return secrets.compare_digest(provided_key.strip(), expected_key)


def generate_secure_key(length: int = 32) -> str:
    """Génère une clé d'API aléatoire de haute entropie."""
    return secrets.token_hex(length // 2)
