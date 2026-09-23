"""
Boucle ReAct autonome (Reason + Act) pour l'Agent local Baay-Faal.
100 % Python Standard Library (Vanilla First).
Orchestre la réflexion du LLM et l'exécution automatique des outils locaux.
"""

import json
import re
from typing import Any, Dict, List, Optional
from core.llm import OllamaClient
from core.memory import BaayMemory
from core.tools import TOOL_REGISTRY, TOOL_SCHEMAS


SYSTEM_PROMPT = """Tu es BAAY-AGENT, un agent d'ingénierie logiciel autonome fonctionnant à 100% en local.
Tu es rigoureux, méthodique et orienté vers l'action concrète ("Jëf Jël").

Voici la liste exacte des outils à ta disposition :
1. "system_info" : pour connaître l'OS, la version Python et le dossier courant. args: {}
2. "list_directory" : pour lister les fichiers d'un dossier. args: {"path": "."}
3. "read_file" : pour lire un fichier existant. args: {"path": "chemin/du/fichier"}
4. "write_file" : pour écrire/créer un fichier. args: {"path": "chemin", "content": "contenu"}
5. "execute_command" : pour lancer une commande shell locale. args: {"command": "..."}
6. "remote_command" : pour exécuter une commande à distance sur une machine du réseau (ex: 'localhost' ou 'serveur_principal'). args: {"node": "...", "command": "..."}
7. "recall_memory" : pour chercher dans ta mémoire longue terme (faits appris ou actions passées). args: {"query": "..."}
8. "remember_fact" : pour mémoriser un fait important (ex: adresse IP, mot de passe, préférence). args: {"key": "...", "value": "..."}
9. "jef_jel_doctor" : JËF-JËL DOCTOR (Analyseur & Correcteur de Bugs). args: {"error_log": "..."}
10. "tak_jouk_generator" : TAK-JOUK GENERATOR (Générateur & Refactoriseur PEP 8). args: {"spec": "..."}
11. "yite_cleaner" : YITÉ CLEANER (Libérateur de Ports & Gestionnaire de Cache). args: {"port": 8000}
12. "ndigel_scaffolder" : NDIGËL SCAFFOLDER (Générateur d'Architecture selon Directive). args: {"project_name": "..."}
13. "njabot_deployer" : NJABOT DEPLOYER (Assistant Git & Déploiement Réseau). args: {"node": "...", "action": "..."}

RÈGLES D'OR DU FORMAT :
Tu DOIS obligatoirement répondre UNIQUEMENT avec un objet JSON valide, sans aucun texte autour.

Exemple pour appeler un outil :
{{
    "thought": "J'ai besoin de connaître le système d'exploitation.",
    "action": "call_tool",
    "tool": "system_info",
    "args": {{}}
}}

Exemple pour donner la réponse finale quand la tâche est terminée :
{{
    "thought": "Toutes les étapes sont achevées.",
    "action": "final_answer",
    "answer": "Voici les informations du système..."
}}
"""


class BaayAgent:
    """
    Agent autonome capable de raisonner, choisir des outils et les exécuter en boucle ReAct.
    """

    def __init__(self, model: str = "qwen2.5-coder:1.5b", max_steps: int = 8):
        self.client = OllamaClient(model=model)
        self.memory = BaayMemory()
        self.max_steps = max_steps
        self.system_prompt = SYSTEM_PROMPT
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extrait un bloc JSON même si le modèle a inclus des balises markdown ou du texte parasite.
        """
        # Nettoyage des balises markdown
        cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned.strip())

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Recherche du premier bloc { ... }
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        return None

    def run(self, user_goal: str) -> str:
        """
        Exécute la boucle ReAct pour atteindre l'objectif fixé par l'utilisateur.
        """
        print(f"\n[OBJECTIF] {user_goal}")
        session_id = self.memory.start_session(user_goal)
        print(f"[MÉMOIRE] Session démarrée : {session_id} (Engine: {self.memory.engine_type})")

        self.messages.append({"role": "user", "content": user_goal})

        step = 0
        while step < self.max_steps:
            step += 1
            print(f"\n--- Étape {step}/{self.max_steps} : Réflexion de l'Agent ---")

            raw_response = self.client.chat(self.messages, temperature=0.1, format_json=True)
            if not raw_response:
                # Mode Fallback Souverain : Si Ollama n'est pas encore démarré en tâche de fond,
                # l'Agent Baay-Faal utilise son moteur de secours natif pour exécuter la tâche.
                fallback_ans = self._run_native_fallback(user_goal, session_id)
                return fallback_ans

            decision = self._extract_json(raw_response)
            if not decision or "action" not in decision:
                # Si le format n'est pas respecté, on relance en rappelant la contrainte
                self.messages.append({
                    "role": "user",
                    "content": "Erreur : Ta réponse doit être un JSON valide avec 'action': 'call_tool' ou 'final_answer'."
                })
                continue

            thought = decision.get("thought", "")
            action = decision.get("action")

            if thought:
                print(f"[PENSÉE] {thought}")

            # Cas 1 : Réponse finale
            if action == "final_answer":
                final_answer = decision.get("answer", "Mission accomplie.")
                self.memory.log_action(session_id, step, thought, action, "final_answer", {}, final_answer)
                self.messages.append({"role": "assistant", "content": raw_response})
                return final_answer

            # Cas 2 : Appel d'outil
            if action == "call_tool":
                tool_name = decision.get("tool")
                args = decision.get("args", {})

                print(f"[ACTION] Appel de l'outil '{tool_name}' avec {json.dumps(args, ensure_ascii=False)}")

                if tool_name not in TOOL_REGISTRY:
                    obs = f"Erreur : L'outil '{tool_name}' n'existe pas dans le registre."
                else:
                    try:
                        func = TOOL_REGISTRY[tool_name]
                        result = func(**args)
                        obs = json.dumps(result, ensure_ascii=False) if not isinstance(result, str) else result
                    except Exception as e:
                        obs = f"Erreur lors de l'exécution de l'outil : {str(e)}"

                print(f"[RÉSULTAT] {obs[:300]}{'...' if len(obs) > 300 else ''}")

                # Journalisation en mémoire persistante
                self.memory.log_action(session_id, step, thought, action, tool_name, args, obs)

                # Ajout de l'historique pour la prochaine itération
                self.messages.append({"role": "assistant", "content": raw_response})
                self.messages.append({
                    "role": "user",
                    "content": f"OBSERVATION DE L'OUTIL '{tool_name}' :\n{obs}"
                })

        return "Fin d'exécution : Nombre maximal d'étapes atteint sans conclusion."

    def _run_native_fallback(self, goal: str, session_id: str) -> str:
        """
        Moteur d'exécution natif souverain utilisé lorsque le daemon Ollama est hors-ligne.
        Analyse l'intention et exécute les outils locaux natifs de manière autonome.
        """
        goal_lower = goal.lower()

        if any(w in goal_lower for w in ["system", "os", "version", "inspect", "statut", "status", "rep", "dossier"]):
            from core.tools import system_info
            res = system_info()
            info_str = f"OS: {res['os']} ({res['os_version']})\nPython: {res['python_version']}\nArchitecture: {res['architecture']}\nRépertoire: {res['current_directory']}"
            self.memory.log_action(session_id, 1, "Inspection système native", "call_tool", "system_info", {}, info_str)
            return f"[MOTEUR SOUVERAIN NATIF]\n\n{info_str}\n\nConseil : Pour activer le raisonnement ReAct LLM avancé, lancez 'ollama serve' en arrière-plan."

        if "memoir" in goal_lower or "memory" in goal_lower or "cherche" in goal_lower:
            res = self.memory.search_memory(goal)
            self.memory.log_action(session_id, 1, "Recherche mémoire native", "call_tool", "recall_memory", {"query": goal}, res)
            return f"[MÉMOIRE VAULT NATIF]\n\nFaits trouvés : {json.dumps(res.get('knowledge', []), ensure_ascii=False, indent=2)}"

        if "doctor" in goal_lower or "jëf" in goal_lower or "jef" in goal_lower or "bug" in goal_lower or "crash" in goal_lower:
            from core.tools import jef_jel_doctor
            res = jef_jel_doctor(error_log=goal)
            self.memory.log_action(session_id, 1, "Analyse Jëf-Jël Doctor", "call_tool", "jef_jel_doctor", {"error_log": goal}, res)
            return f"[JËF-JËL DOCTOR]\n\nDiagnostic : {res['diagnosis']}\nRecommandation : {res['recommendation']}"

        if "tak" in goal_lower or "generator" in goal_lower or "generate" in goal_lower or "code" in goal_lower:
            from core.tools import tak_jouk_generator
            res = tak_jouk_generator(spec=goal)
            self.memory.log_action(session_id, 1, "Génération Tak-Jouk Generator", "call_tool", "tak_jouk_generator", {"spec": goal}, res)
            return f"[TAK-JOUK GENERATOR]\n\nCode généré (PEP 8 Natif) :\n```python\n{res['code_generated']}\n```"

        if any(w in goal_lower for w in ["yité", "yite", "clean", "nettoy", "port", "youtube", "l'idée", "ité", "unité"]):
            from core.tools import yite_cleaner
            res = yite_cleaner(port=8000)
            self.memory.log_action(session_id, 1, "Nettoyage Yité Cleaner", "call_tool", "yite_cleaner", {"port": 8000}, res)
            return f"[YITÉ CLEANER]\n\n{res['message']}\nCaches nettoyés : {len(res['pycache_found'])}"

        if "ndigël" in goal_lower or "ndigel" in goal_lower or "scaffold" in goal_lower or "architecture" in goal_lower or "projet" in goal_lower:
            from core.tools import ndigel_scaffolder
            res = ndigel_scaffolder(project_name="mon_nouveau_projet")
            self.memory.log_action(session_id, 1, "Scaffolding Ndigël", "call_tool", "ndigel_scaffolder", {"project_name": "mon_nouveau_projet"}, res)
            return f"[NDIGËL SCAFFOLDER]\n\n{res['message']}\nStructure :\n- " + "\n- ".join(res['structure_created'])

        if "njabot" in goal_lower or "deploy" in goal_lower or "git" in goal_lower or "reseau" in goal_lower:
            from core.tools import njabot_deployer
            res = njabot_deployer(node="localhost", action="status")
            self.memory.log_action(session_id, 1, "Déploiement Njabot", "call_tool", "njabot_deployer", {"node": "localhost"}, res)
            return f"[NJABOT DEPLOYER]\n\n{res['message']}\nStatut Git :\n{res['git_status']}"

        from core.tools import execute_command
        res = execute_command(goal)
        self.memory.log_action(session_id, 1, "Exécution de commande native", "call_tool", "execute_command", {"command": goal}, res)
        return f"[EXÉCUTION NATIVE SOUVERAINE]\n\n{res.get('stdout') or res.get('stderr') or 'Commande exécutée.'}"
