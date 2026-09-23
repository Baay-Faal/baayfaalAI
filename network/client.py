"""
Client réseau pour l'Agent Baay-Faal.
100 % Python Standard Library (socket, hmac, hashlib, json).

Permet d'interroger et d'exécuter des commandes à distance sur un démon de nœud distant.
"""

import hashlib
import hmac
import json
import socket
from typing import Any, Dict, Optional


class NodeClient:
    """
    Client TCP pour communiquer de façon sécurisée avec un Node Daemon Baay-Faal.
    """

    def __init__(self, host: str, port: int = 9999, secret_key: str = "baay_faal_secret_key_change_me", timeout: int = 30):
        self.host = host
        self.port = port
        self.secret_key = secret_key.encode("utf-8")
        self.timeout = timeout

    def send_command(self, command: str) -> Dict[str, Any]:
        """
        Se connecte au démon distant, authentifie la session par HMAC et exécute la commande.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(float(self.timeout))

        try:
            sock.connect((self.host, self.port))

            # 1. Réception du challenge du serveur
            raw_challenge = sock.recv(4096).decode("utf-8").strip()
            if not raw_challenge:
                return {"success": False, "error": "Le serveur n'a renvoyé aucun challenge d'authentification."}

            challenge_payload = json.loads(raw_challenge)
            if challenge_payload.get("status") != "AUTH_CHALLENGE":
                return {"success": False, "error": f"Statut initial invalide du serveur : {challenge_payload}"}

            nonce_hex = challenge_payload.get("nonce", "")
            nonce = bytes.fromhex(nonce_hex)

            # 2. Calcul et envoi de la signature HMAC-SHA256
            client_signature = hmac.new(self.secret_key, nonce, hashlib.sha256).hexdigest()
            auth_msg = json.dumps({"signature": client_signature}) + "\n"
            sock.sendall(auth_msg.encode("utf-8"))

            # 3. Réception de la réponse d'auth
            raw_auth_res = sock.recv(4096).decode("utf-8").strip()
            if not raw_auth_res:
                return {"success": False, "error": "Pas de réponse après l'envoi de la signature."}

            auth_res = json.loads(raw_auth_res)
            if auth_res.get("status") != "AUTH_OK":
                return {"success": False, "error": f"Authentification rejetée par le démon : {auth_res.get('error', 'Inconnue')}"}

            # 4. Envoi de l'ordre à exécuter
            cmd_msg = json.dumps({"action": "execute", "command": command, "timeout": self.timeout}) + "\n"
            sock.sendall(cmd_msg.encode("utf-8"))

            # 5. Réception du résultat
            res_chunks = []
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                res_chunks.append(chunk)

            raw_res = b"".join(res_chunks).decode("utf-8").strip()
            if not raw_res:
                return {"success": False, "error": "Aucune donnée de résultat reçue."}

            result_payload = json.loads(raw_res)
            return result_payload

        except socket.timeout:
            return {"success": False, "error": f"Timeout de connexion vers {self.host}:{self.port} ({self.timeout}s)."}
        except ConnectionRefusedError:
            return {"success": False, "error": f"Connexion refusée par le nœud distant ({self.host}:{self.port}). Le démon est-il démarré ?"}
        except Exception as e:
            return {"success": False, "error": f"Erreur réseau / protocole : {str(e)}"}
        finally:
            sock.close()


if __name__ == "__main__":
    print("--- Test rapide du NodeClient vers localhost:9999 ---")
    client = NodeClient("127.0.0.1", 9999)
    res = client.send_command("echo Hello depuis le NodeClient natif Baay-Faal!")
    print("Résultat reçu :", res)
