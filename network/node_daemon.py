"""
Démon de nœud distant (Node Daemon) pour l'Agent Baay-Faal.
100 % Python Standard Library (socket, threading, hmac, hashlib, subprocess).

Permet à l'Agent de piloter cette machine à distance de manière sécurisée via TCP.
"""

import argparse
import hashlib
import hmac
import json
import os
import socket
import subprocess
import sys
import threading
from typing import Tuple

DEFAULT_PORT = 9999
DEFAULT_SECRET = "baay_faal_secret_key_change_me"


def execute_command_raw(command: str, timeout: int = 30) -> dict:
    """
    Exécute une commande shell locale et retourne le résultat.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace"
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Délai d'exécution dépassé ({timeout}s).",
            "exit_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Erreur système : {str(e)}",
            "exit_code": -1
        }


class NodeDaemon:
    """
    Serveur TCP léger écoutant les ordres entrants et exécutant les commandes après authentification HMAC.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = DEFAULT_PORT, secret_key: str = DEFAULT_SECRET):
        self.host = host
        self.port = port
        self.secret_key = secret_key.encode("utf-8")
        self.is_running = False
        self.server_socket = None

    def _handle_client(self, client_socket: socket.socket, addr: Tuple[str, int]):
        """
        Gère la connexion d'un client : Handshake HMAC -> Réception d'ordre -> Exécution -> Réponse.
        """
        print(f"[DÉMON] Connexion reçue depuis {addr[0]}:{addr[1]}")
        client_socket.settimeout(30.0)

        try:
            # Step 1 : Envoi du Challenge HMAC (nonce aléatoire 32 octets)
            nonce = os.urandom(32)
            challenge_msg = json.dumps({
                "status": "AUTH_CHALLENGE",
                "nonce": nonce.hex()
            }) + "\n"
            client_socket.sendall(challenge_msg.encode("utf-8"))

            # Step 2 : Attente de la signature HMAC du client
            response_data = client_socket.recv(4096).decode("utf-8").strip()
            if not response_data:
                print(f"[DÉMON] {addr[0]} s'est déconnecté avant l'auth.")
                return

            auth_payload = json.loads(response_data)
            client_signature = auth_payload.get("signature", "")

            # Calcul de la signature attendue
            expected_signature = hmac.new(self.secret_key, nonce, hashlib.sha256).hexdigest()

            if not hmac.compare_digest(client_signature, expected_signature):
                print(f"[REJET DÉMON] Échec d'authentification HMAC pour {addr[0]}")
                err_msg = json.dumps({"status": "AUTH_FAILED", "error": "Clé secrète invalide."}) + "\n"
                client_socket.sendall(err_msg.encode("utf-8"))
                return

            # Auth OK
            ok_msg = json.dumps({"status": "AUTH_OK", "message": "Authentification réussie."}) + "\n"
            client_socket.sendall(ok_msg.encode("utf-8"))
            print(f"[DÉMON] Client {addr[0]} authentifié avec succès.")

            # Step 3 : Réception et exécution de la commande
            cmd_data = client_socket.recv(8192).decode("utf-8").strip()
            if not cmd_data:
                return

            cmd_payload = json.loads(cmd_data)
            command = cmd_payload.get("command", "")
            timeout = cmd_payload.get("timeout", 30)

            print(f"[DÉMON EXÉCUTION] Ordre reçu de {addr[0]} : `{command}`")
            result = execute_command_raw(command, timeout=timeout)

            # Renvoi du résultat
            res_msg = json.dumps(result, ensure_ascii=False) + "\n"
            client_socket.sendall(res_msg.encode("utf-8"))
            print(f"[DÉMON] Résultat envoyé à {addr[0]} (Code: {result['exit_code']})")

        except Exception as e:
            print(f"[ERREUR DÉMON] Exception avec {addr[0]} : {e}")
            try:
                err_payload = json.dumps({"success": False, "error": str(e), "exit_code": -1}) + "\n"
                client_socket.sendall(err_payload.encode("utf-8"))
            except Exception:
                pass
        finally:
            client_socket.close()

    def start(self):
        """
        Démarre la boucle principale du serveur TCP.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.is_running = True

        print("=" * 60)
        print(f"  BAAY-FAAL NODE DAEMON (Nœud Distant Autonome)")
        print(f"  Écoute sur {self.host}:{self.port} | Auth HMAC-SHA256 active")
        print("=" * 60)

        try:
            while self.is_running:
                client_sock, addr = self.server_socket.accept()
                thread = threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            print("\n[DÉMON] Arrêt du démon demandé.")
        finally:
            self.stop()

    def stop(self):
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
            print("[DÉMON] Socket serveur fermé.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Baay-Faal Remote Node Daemon")
    parser.add_argument("--host", default="0.0.0.0", help="Adresse d'écoute (0.0.0.0 par défaut)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port TCP d'écoute (9999 par défaut)")
    parser.add_argument("--secret", default=DEFAULT_SECRET, help="Clé secrète partagée HMAC")
    args = parser.parse_args()

    daemon = NodeDaemon(host=args.host, port=args.port, secret_key=args.secret)
    daemon.start()
