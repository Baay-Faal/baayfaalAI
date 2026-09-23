"""
Connecteur natif vers le serveur local Ollama.
100 % Python Standard Library (urllib.request + json).
Zéro dépendance externe.
"""

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


class OllamaClient:
    """
    Client HTTP minimaliste et robuste pour interagir avec l'API locale d'Ollama.
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5-coder:1.5b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        format_json: bool = False
    ) -> Optional[str]:
        """
        Envoie un historique de messages au modèle local et renvoie sa réponse textuelle.
        """
        endpoint = f"{self.base_url}/api/chat"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        if format_json:
            payload["format"] = "json"

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("message", {}).get("content", "").strip()
        except urllib.error.URLError as e:
            print(f"[ERREUR OLLAMA] Impossible de joindre le serveur local ({endpoint}) : {e}")
            return None
        except Exception as e:
            print(f"[ERREUR] Erreur inattendue lors de l'appel LLM : {e}")
            return None


if __name__ == "__main__":
    client = OllamaClient()
    print("--- Test du connecteur Ollama en Python natif ---")
    test_msgs = [
        {"role": "system", "content": "Tu es un assistant concis."},
        {"role": "user", "content": "Dis en 4 mots que tu es prêt."}
    ]
    rep = client.chat(test_msgs)
    print(f"Réponse reçue : {rep}")
