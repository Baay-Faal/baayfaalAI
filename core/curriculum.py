"""
Programme Académique & Curriculum Technologique pour l'Agent Baay-Faal.
100 % Python Standard Library — Basé sur la Documentation Officielle Python (Python Docs & PEP 8).

4 Modules d'Ingénierie x 3 Exercices Pratiques par Module = 12 Exercices au total.
"""

from typing import Any, Dict, List, Optional

PYTHON_CURRICULUM: List[Dict[str, Any]] = [
    # =========================================================================
    # MODULE 1 : FONDATIONS & ALGORITHMIQUE NATIF (3 Exercices)
    # =========================================================================
    {
        "id": "py_1_1",
        "module_number": 1,
        "module_title": "MODULE 1 : FONDATIONS & ALGORITHMIQUE NATIF",
        "exercise_number": 1,
        "exercise_title": "Exo 1/3 : Variables, Fonctions & Arithmétique Natif",
        "title": "1.1 : Variables & Arithmétique Natif",
        "course_content": """
<h3>📖 DOCUMENTATION OFFICIELLE : VARIABLES, TYPES PRIMITIFS & FONCTIONS</h3>

<h4>1. Déclaration & Modèle Mémoire en Python</h4>
<p>En Python, les variables ne sont pas des conteneurs de type fixe, mais des <strong>références nommées (étiquettes)</strong> pointant vers des objets en mémoire. Les types numériques fondamentaux sont <code>int</code> (entier de précision illimitée) et <code>float</code> (nombre à virgule flottante IEEE 754).</p>

<h4>2. Définition de Fonctions (PEP 8)</h4>
<p>Une fonction s'initialise avec le mot-clé <code>def</code>, suivi du nom en <code>snake_case</code>, des paramètres entre parenthèses et de 4 espaces d'indentation. Le mot-clé <code>return</code> met fin à l'exécution et renvoie l'objet résultant.</p>

<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--accent-amber); padding: 8px 12px; margin: 10px 0;">
  <strong>💡 Analogie du monde réel :</strong> Une fonction est comme une calculatrice programmable d'entreprise : vous lui injectez des données brutes en entrée (revenu, dépenses), elle applique l'instruction arithmétique et vous affiche la fiche de bilan finale sur l'écran (<code>return</code>).
</div>

<h4>⚠️ PIÈGE CLASSIQUE À ÉVITER :</h4>
<pre><code class="language-python"># ❌ ANTI-PATTERN : Oublier le 'return' (renvoie 'None' par défaut)
def calculer_budget(revenu, depenses):
    solde = revenu - depenses
    print(solde)  # N'enregistre aucune valeur de retour !

# ✅ BONNE PRATIQUE (PEP 8) :
def calculer_budget(revenu, depenses):
    return revenu - depenses
</code></pre>

<h4>📌 Syntaxe de référence officielle :</h4>
<pre><code class="language-python">def nom_fonction(param1, param2):
    resultat = param1 - param2
    return resultat
</code></pre>
""",
        "objective": "Créez une fonction 'calculer_budget(revenu, depenses)' qui prend deux nombres en arguments et retourne le solde disponible (revenu - depenses).",
        "starter_code": """# EXO 1/3 : VARIABLES & ARITHMÉTIQUE NATIF
# TODO : Écrivez la fonction 'calculer_budget(revenu, depenses)' qui retourne la différence (revenu - depenses).

def calculer_budget(revenu, depenses):
    pass

if __name__ == "__main__":
    print("Test local :", calculer_budget(2500, 1800))
""",
        "test_suite": """
import unittest

class TestLesson1_1(unittest.TestCase):
    def test_budget(self):
        self.assertEqual(calculer_budget(2500, 1800), 700)
        self.assertEqual(calculer_budget(1000, 1000), 0)
        self.assertEqual(calculer_budget(500, 800), -300)

if __name__ == '__main__':
    unittest.main()
""",
        "hint": "Déclarez `def calculer_budget(revenu, depenses):` puis effectuez `return revenu - depenses`."
    },
    {
        "id": "py_1_2",
        "module_number": 1,
        "module_title": "MODULE 1 : FONDATIONS & ALGORITHMIQUE NATIF",
        "exercise_number": 2,
        "exercise_title": "Exo 2/3 : Structures Conditionnelles & Contrôle d'Accès",
        "title": "1.2 : Conditions & Logique Bouléenne",
        "course_content": """
<h3>📖 DOCUMENTATION OFFICIELLE : LOGIQUE BOULÉENNE & CONTROL FLOW</h3>

<h4>1. Instructions Conditionnelles (<code>if</code>, <code>elif</code>, <code>else</code>)</h4>
<p>Les structures conditionnelles évaluent des expressions booléennes (<code>True</code> ou <code>False</code>). Les opérateurs de comparaison sont : <code>==</code> (égalité), <code>!=</code> (inégalité), <code>>=</code> (supérieur ou égal), <code><=</code> (inférieur ou égal).</p>

<h4>2. Opérateurs Logiques et Évaluation en Court-Circuit (Short-Circuit Evaluation)</h4>
<ul>
  <li><code>and</code> : Retourne <code>True</code> SSI les deux expressions sont vraies. Si la première est fausse, Python n'évalue même pas la seconde.</li>
  <li><code>or</code> : Retourne <code>True</code> dès qu'une expression est vraie.</li>
  <li><code>in</code> : Opérateur d'appartenance d'une séquence (ex: <code>role in ('admin', 'dev')</code>).</li>
</ul>

<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--accent-amber); padding: 8px 12px; margin: 10px 0;">
  <strong>💡 Analogie du monde réel :</strong> C'est le sas de sécurité automatisé d'un datacenter : la porte ne s'ouvre que si le scanner confirme que le badge est valide (âge >= 18) ET que l'autorisation d'accès est de type 'admin' ou 'dev'.
</div>

<h4>⚠️ LE PIÈGE CLASSIQUE D'INGÉNIEUR À ÉVITER :</h4>
<pre><code class="language-python"># ❌ ANTI-PATTERN (ERREUR CRITIQUE DE SÉCURITÉ) :
# En Python, 'dev' est une chaîne non vide (évaluée à True). 'admin' or 'dev' renvoie toujours True !
if role == 'admin' or 'dev':
    return True  # 💥 Laisse passer absolument tout le monde !

# ✅ BONNE PRATIQUE (PYTHON DOCS & PEP 8) :
if age >= 18 and role in ('admin', 'dev'):
    return True
return False
</code></pre>
""",
        "objective": "Créez une fonction 'filtrer_acces(age, role)' qui retourne True si l'âge est >= 18 ET que le rôle est 'admin' ou 'dev'. Sinon, elle retourne False.",
        "starter_code": """# EXO 2/3 : CONDITIONS & GARDE-FOUS
# TODO : Écrivez la fonction 'filtrer_acces(age, role)' d'après le cahier des charges.

def filtrer_acces(age, role):
    pass

if __name__ == "__main__":
    print("Accès :", filtrer_acces(20, "dev"))
""",
        "test_suite": """
import unittest

class TestLesson1_2(unittest.TestCase):
    def test_acces(self):
        self.assertTrue(filtrer_acces(18, "admin"))
        self.assertTrue(filtrer_acces(25, "dev"))
        self.assertFalse(filtrer_acces(17, "admin"))
        self.assertFalse(filtrer_acces(30, "guest"))

if __name__ == '__main__':
    unittest.main()
""",
        "hint": "Utilisez `if age >= 18 and role in ['admin', 'dev']:`."
    },
    {
        "id": "py_1_3",
        "module_number": 1,
        "module_title": "MODULE 1 : FONDATIONS & ALGORITHMIQUE NATIF",
        "exercise_number": 3,
        "exercise_title": "Exo 3/3 : Boucles & Agrégation Statistiques",
        "title": "1.3 : Iterations & Exception Handling",
        "course_content": """
<h3>📖 DOCUMENTATION OFFICIELLE : BOUCLES & LEVÉE D'EXCEPTIONS</h3>

<h4>1. Parcours de Collections avec <code>for</code> et <code>sum()</code></h4>
<p>Les boucles parcourent les objets itérables (listes, tuples, dictionnaires). Les fonctions intégrées <code>sum(liste)</code> et <code>len(liste)</code> permettent de calculer la somme et le nombre d'éléments en temps $O(n)$.</p>

<h4>2. Robuste d'Ingénierie & Levée d'Exceptions Explicites</h4>
<p>Pour éviter la division par zéro (<code>ZeroDivisionError</code>) sur une liste vide, un code d'ingénieur vérifie la précondition et lève une exception dédiée avec <code>raise ValueError("Message")</code>.</p>

<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--accent-amber); padding: 8px 12px; margin: 10px 0;">
  <strong>💡 Analogie du monde réel :</strong> C'est comme le voyant d'avertissement d'un moteur d'avion : si le réservoir de carburant (la liste de notes) est vide, le système déclenche immédiatement une alarme explicite au lieu de tenter de faire tourner la pompe à vide.
</div>

<h4>⚠️ PIÈGE CLASSIQUE À ÉVITER :</h4>
<pre><code class="language-python"># ❌ ANTI-PATTERN : Tenter la division sans vérifier la taille
def calculer_moyenne(notes):
    return sum(notes) / len(notes)  # 💥 Crash ZeroDivisionError si notes == [] !

# ✅ BONNE PRATIQUE (DOCS PYTHON) :
def calculer_moyenne(notes):
    if not notes:
        raise ValueError("La liste de notes ne peut pas être vide")
    return sum(notes) / len(notes)
</code></pre>
""",
        "objective": "Créez une fonction 'calculer_moyenne(notes)' qui retourne la moyenne (float) d'une liste de nombres. Si la liste est vide, le programme doit lever une exception ValueError.",
        "starter_code": """# EXO 3/3 : BOUCLES & EXCEPTIONS NATIVES
# TODO : Implémentez 'calculer_moyenne(notes)' qui calcule la moyenne ou lève ValueError si vide.

def calculer_moyenne(notes):
    pass

if __name__ == "__main__":
    print("Moyenne :", calculer_moyenne([14, 16, 18, 20]))
""",
        "test_suite": """
import unittest

class TestLesson1_3(unittest.TestCase):
    def test_moyenne(self):
        self.assertAlmostEqual(calculer_moyenne([10, 20, 30]), 20.0)
        self.assertAlmostEqual(calculer_moyenne([15]), 15.0)
        with self.assertRaises(ValueError):
            calculer_moyenne([])

if __name__ == '__main__':
    unittest.main()
""",
        "hint": "Vérifiez d'abord `if not notes: raise ValueError('Liste vide')` puis retournez `sum(notes) / len(notes)`."
    },

    # =========================================================================
    # MODULE 2 : STRUCTURES DE DONNÉES & PARSERS (3 Exercices)
    # =========================================================================
    {
        "id": "py_2_1",
        "module_number": 2,
        "module_title": "MODULE 2 : STRUCTURES DE DONNÉES & PARSERS",
        "exercise_number": 1,
        "exercise_title": "Exo 1/3 : Dictionnaires & Parseur de Logs",
        "title": "2.1 : Dictionnaires & Agrégation de logs",
        "course_content": """
<h3>📖 DOCUMENTATION OFFICIELLE : DICTIONNAIRES & ANNOTATIONS DE LOGS</h3>

<h4>1. Structure Table de Hachage (Dict en Python)</h4>
<p>En Python, les dictionnaires sont des tables de hachage optimisées en C ($O(1)$ moyen pour la recherche et l'insertion). La méthode <code>d.get(key, default)</code> permet de récupérer une valeur de manière sûre sans provoquer de KeyError.</p>

<h4>2. Traitement de Chaînes de Caractères (String Parsing)</h4>
<p>Les méthodes natives <code>str.startswith(prefix)</code> et <code>str.split(sep)</code> découpent et analysent les flux textuels (ex: journaux de systèmes Linux ou logs HTTP).</p>

<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--accent-amber); padding: 8px 12px; margin: 10px 0;">
  <strong>💡 Analogie du monde réel :</strong> C'est le tableau de tri postal d'un centre logistique : chaque colis arrivant porte un tampon ('INFO', 'WARN', 'ERROR') et le trieur incrémente le compteur correspondant.
</div>

<h4>📌 Syntaxe de référence officielle :</h4>
<pre><code class="language-python">compteur = {"INFO": 0, "WARN": 0, "ERROR": 0}
for log in logs:
    for niveau in compteur:
        if log.startswith(niveau):
            compteur[niveau] += 1
</code></pre>
""",
        "objective": "Créez une fonction 'analyser_logs(logs)' qui prend une liste de chaînes de logs (ex: 'INFO: démarrage', 'ERROR: fail') et retourne un dictionnaire avec le nombre exact d'occurrences pour 'INFO', 'WARN' et 'ERROR'.",
        "starter_code": """# EXO 1/3 : DICTIONNAIRES & PARSEUR DE LOGS
# TODO : Implémentez 'analyser_logs(logs)' pour compter les occurrences de logs.

def analyser_logs(logs):
    pass

if __name__ == "__main__":
    sample = ["INFO: démarrage", "ERROR: crash DB", "INFO: relance", "WARN: RAM faible"]
    print("Résultat :", analyser_logs(sample))
""",
        "test_suite": """
import unittest

class TestLesson2_1(unittest.TestCase):
    def test_logs(self):
        logs = ["INFO: start", "ERROR: db fail", "INFO: retry", "WARN: high ram", "ERROR: fatal"]
        res = analyser_logs(logs)
        self.assertEqual(res.get("INFO"), 2)
        self.assertEqual(res.get("WARN"), 1)
        self.assertEqual(res.get("ERROR"), 2)

if __name__ == '__main__':
    unittest.main()
""",
        "hint": "Initialisez `compteur = {'INFO': 0, 'WARN': 0, 'ERROR': 0}` et découpez chaque log avec `log.split(':')`."
    },
    {
        "id": "py_2_2",
        "module_number": 2,
        "module_title": "MODULE 2 : STRUCTURES DE DONNÉES & PARSERS",
        "exercise_number": 2,
        "exercise_title": "Exo 2/3 : Listes & Déduplication d'Ordre",
        "title": "2.2 : Listes & Préservation de l'Ordre",
        "course_content": """
<h3>📖 DOCUMENTATION OFFICIELLE : LISTES & PRÉSERVATION D'ORDRE SÉQUENTIEL</h3>

<h4>1. Séquences Ordonnées vs Ensembles Non Ordonnés</h4>
<p>Les listes préservent l'ordre chronologique des insertions. Convertir une liste via <code>list(set(l))</code> élimine les doublons mais <strong>détruit irrémédiablement l'ordre initial</strong>.</p>

<h4>2. Algorithme de Déduplication Stable</h4>
<p>Pour éliminer les doublons tout en maintenant l'ordre exact de première apparition, on maintient un registre des éléments déjà rencontrés.</p>

<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--accent-amber); padding: 8px 12px; margin: 10px 0;">
  <strong>💡 Analogie du monde réel :</strong> C'est le registre des arrivées d'un hôtel : si un client régulier revient se présenter à la réception plusieurs fois dans la journée, vous ne conservez que la première heure d'enregistrement initiale sur le registre.
</div>

<h4>📌 Syntaxe de référence officielle :</h4>
<pre><code class="language-python">def nettoyer_doublons(elements):
    resultat = []
    for item in elements:
        if item not in resultat:
            resultat.append(item)
    return resultat
</code></pre>
""",
        "objective": "Créez une fonction 'nettoyer_doublons(elements)' qui prend une liste et élimine les doublons tout en conservant l'ordre de première apparition des éléments.",
        "starter_code": """# EXO 2/3 : LISTES & DÉDUPLICATION D'ORDRE
# TODO : Implémentez 'nettoyer_doublons(elements)' en préservant l'ordre initial.

def nettoyer_doublons(elements):
    pass

if __name__ == "__main__":
    print("Résultat :", nettoyer_doublons(["python", "c++", "python", "linux", "c++"]))
""",
        "test_suite": """
import unittest

class TestLesson2_2(unittest.TestCase):
    def test_dedup(self):
        src = ["a", "b", "a", "c", "b", "d"]
        self.assertEqual(nettoyer_doublons(src), ["a", "b", "c", "d"])

if __name__ == '__main__':
    unittest.main()
""",
        "hint": "Utilisez une liste vide `result = []` et ajoutez un élément uniquement s'il n'est pas déjà présent (`if item not in result:`)."
    },
    {
        "id": "py_2_3",
        "module_number": 2,
        "module_title": "MODULE 2 : STRUCTURES DE DONNÉES & PARSERS",
        "exercise_number": 3,
        "exercise_title": "Exo 3/3 : List Comprehensions & Optimisation",
        "title": "2.3 : List Comprehensions Pythoniques",
        "course_content": """
<h3>📖 DOCUMENTATION OFFICIELLE : COMPRÉHENSION DE LISTES & PERFORMANCE</h3>

<h4>1. Syntaxe Idiomatique (List Comprehension)</h4>
<p>La compréhension de liste est la manière officielle et recommandée par la PEP 8 pour construire de nouvelles listes. Elle est exécutée directement au niveau du bytecode C-Python (plus rapide qu'une boucle `for` classique avec `append`).</p>

<h4>2. Filtrage & Transformation Combinés</h4>
<p>Elle s'articule autour de la formule : <code>[expression for item in iterable if condition]</code>.</p>

<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--accent-amber); padding: 8px 12px; margin: 10px 0;">
  <strong>💡 Analogie du monde réel :</strong> C'est un tapis roulant de tri optique dans un centre de recyclage : il identifie au vol les bouteilles en verre (condition pair) et les transforme instantanément en granulés (élévation au carré).
</div>

<h4>📌 Syntaxe de référence officielle :</h4>
<pre><code class="language-python"># [transformation for n in nombres if condition]
return [n ** 2 for n in nombres if n % 2 == 0]
</code></pre>
""",
        "objective": "Créez une fonction 'carres_nombres_pairs(nombres)' qui filtre les nombres pairs d'une liste et retourne une nouvelle liste contenant leurs carrés (n²).",
        "starter_code": """# EXO 3/3 : LIST COMPREHENSIONS (PERFORMANCE)
# TODO : Implémentez 'carres_nombres_pairs(nombres)' à l'aide d'une comprehension de liste.

def carres_nombres_pairs(nombres):
    pass

if __name__ == "__main__":
    print("Résultat :", carres_nombres_pairs([1, 2, 3, 4, 5, 6]))
""",
        "test_suite": """
import unittest

class TestLesson2_3(unittest.TestCase):
    def test_comprehension(self):
        self.assertEqual(carres_nombres_pairs([1, 2, 3, 4, 5, 6]), [4, 16, 36])
        self.assertEqual(carres_nombres_pairs([1, 3, 5]), [])

if __name__ == '__main__':
    unittest.main()
""",
        "hint": "Écrivez `return [n**2 for n in nombres if n % 2 == 0]`."
    },

    # =========================================================================
    # MODULE 3 : POO, JSON & SÉCURITÉ (3 Exercices)
    # =========================================================================
    {
        "id": "py_3_1",
        "module_number": 3,
        "module_title": "MODULE 3 : POO, JSON & SÉCURITÉ",
        "exercise_number": 1,
        "exercise_title": "Exo 1/3 : Programmation Orientée Objet (POO)",
        "title": "3.1 : POO & Encapsulation Natifs",
        "course_content": """
<h3>📖 DOCUMENTATION OFFICIELLE : CLASSES & ENCAPSULATION EN PYTHON</h3>

<h4>1. Classes & Instanciation</h4>
<p>La méthode spéciale <code>__init__(self)</code> est le constructeur appelé lors de la création d'un objet. Le paramètre <code>self</code> représente l'instance de classe en cours de manipulation.</p>

<h4>2. Encapsulation & Attributs Privés (Convention PEP 8)</h4>
<p>En Python, les attributs préfixés d'un souligné (<code>self._data</code>) sont considérés comme protégés. Les méthodes de classe contrôlent l'accès aux données internes.</p>

<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--accent-amber); padding: 8px 12px; margin: 10px 0;">
  <strong>💡 Analogie du monde réel :</strong> C'est la mémoire vive d'un assistant virtuel : la classe est l'architecture du composant mémoire, et chaque méthode (`store_fact`, `get_fact`) permet d'écrire ou de lire dans le coffre interne de l'agent.
</div>

<h4>📌 Syntaxe de référence officielle :</h4>
<pre><code class="language-python">class AgentMemory:
    def __init__(self):
        self._data = {}

    def store_fact(self, key, value):
        self._data[key] = value

    def get_fact(self, key):
        return self._data.get(key, None)
</code></pre>
""",
        "objective": "Créez une classe 'AgentMemory' avec les méthodes `store_fact(key, value)` et `get_fact(key)` (qui retourne None si la clé n'existe pas).",
        "starter_code": """# EXO 1/3 : POO & ENCAPSULATION
# TODO : Définissez la classe 'AgentMemory' et ses méthodes store_fact et get_fact.

class AgentMemory:
    def __init__(self):
        self._data = {}

    def store_fact(self, key, value):
        pass

    def get_fact(self, key):
        pass

if __name__ == "__main__":
    mem = AgentMemory()
    mem.store_fact("node_ip", "10.0.0.1")
    print("Valeur :", mem.get_fact("node_ip"))
""",
        "test_suite": """
import unittest

class TestLesson3_1(unittest.TestCase):
    def test_poo(self):
        mem = AgentMemory()
        mem.store_fact("version", "2.5")
        self.assertEqual(mem.get_fact("version"), "2.5")
        self.assertIsNone(mem.get_fact("inconnu"))

if __name__ == '__main__':
    unittest.main()
""",
        "hint": "Dans `store_fact` : `self._data[key] = value`. Dans `get_fact` : `return self._data.get(key, None)`."
    },
    {
        "id": "py_3_2",
        "module_number": 3,
        "module_title": "MODULE 3 : POO, JSON & SÉCURITÉ",
        "exercise_number": 2,
        "exercise_title": "Exo 2/3 : Exceptions & Parsing JSON Sécurisé",
        "title": "3.2 : Exceptions & Sécurisation JSON",
        "course_content": """
<h3>📖 DOCUMENTATION OFFICIELLE : GESTION D'EXCEPTIONS & DÉSÉRIALISATION JSON</h3>

<h4>1. Le Module Natif <code>json</code></h4>
<p>Le module <code>json</code> sérialise et désérialise les données interchangeables du Web (JSON ➔ Dictionnaires / Listes Python). La fonction <code>json.loads(s)</code> désérialise une chaîne de caractères.</p>

<h4>2. Gestion des Exceptions Réseau (<code>try...except</code>)</h4>
<p>Si la chaîne entrée est malformée ou nulle, <code>json.loads()</code> lève des exceptions (<code>json.JSONDecodeError</code>, <code>TypeError</code>). Capturer ces erreurs garantit qu'un payload malveillant ou corrompu ne plante pas le serveur Web.</p>

<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--accent-amber); padding: 8px 12px; margin: 10px 0;">
  <strong>💡 Analogie du monde réel :</strong> C'est le sas de décontamination d'un laboratoire de recherche : si le colis reçu est corrompu ou illisible, le sas se ferme hermétiquement et renvoie un récipient vide (`{}`), évitant la propagation de l'erreur.
</div>

<h4>📌 Syntaxe de référence officielle :</h4>
<pre><code class="language-python">import json

def charger_json_securise(chaine_json):
    try:
        return json.loads(chaine_json)
    except Exception:
        return {}
</code></pre>
""",
        "objective": "Créez une fonction 'charger_json_securise(chaine_json)' qui tente de parser une chaîne JSON avec json.loads(). En cas d'erreur de syntaxe ou type invalide, elle retourne un dictionnaire vide {} sans crasher.",
        "starter_code": """# EXO 2/3 : EXCEPTIONS & PARSING JSON SÉCURISÉ
# TODO : Implémentez 'charger_json_securise(chaine_json)' avec try/except.

import json

def charger_json_securise(chaine_json):
    pass

if __name__ == "__main__":
    print("Valide :", charger_json_securise('{"status": "ok"}'))
    print("Invalide :", charger_json_securise("bad json"))
""",
        "test_suite": """
import unittest

class TestLesson3_2(unittest.TestCase):
    def test_json(self):
        self.assertEqual(charger_json_securise('{"key": "val"}'), {"key": "val"})
        self.assertEqual(charger_json_securise("invalid json"), {})
        self.assertEqual(charger_json_securise(None), {})

if __name__ == '__main__':
    unittest.main()
""",
        "hint": "Utilisez `try: return json.loads(chaine_json) except Exception: return {}`."
    },
    {
        "id": "py_3_3",
        "module_number": 3,
        "module_title": "MODULE 3 : POO, JSON & SÉCURITÉ",
        "exercise_number": 3,
        "exercise_title": "Exo 3/3 : Cryptographie & Empreintes SHA-256",
        "title": "3.3 : Cryptographie Natif & SHA-256",
        "course_content": """
<h3>📖 DOCUMENTATION OFFICIELLE : CRYPTOGRAPHIE & HACHAGE SHA-256</h3>

<h4>1. Hachage Unidirectionnel (Module <code>hashlib</code>)</h4>
<p>Le module natif <code>hashlib</code> fournit les algorithmes de hachage standard (SHA-256, SHA-512, MD5). Une fonction de hachage prend une suite d'octets et produit une empreinte fixe de 64 caractères hexadécimaux.</p>

<h4>2. Encodage d'Octets (<code>str.encode("utf-8")</code>)</h4>
<p>Les fonctions de hachage travaillent exclusivement sur des octets (<code>bytes</code>). Il est donc indispensable de convertir la chaîne de caractères UTF-8 avec <code>.encode("utf-8")</code> avant le calcul.</p>

<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--accent-amber); padding: 8px 12px; margin: 10px 0;">
  <strong>💡 Analogie du monde réel :</strong> C'est le scellé de sécurité numéroté d'un conteneur maritime : si le moindre octet du contenu est altéré pendant le transport, le numéro du scellé d'arrivée devient complètement incohérent.
</div>

<h4>📌 Syntaxe de référence officielle :</h4>
<pre><code class="language-python">import hashlib

def generer_empreinte_sha256(texte):
    octets = texte.encode("utf-8")
    return hashlib.sha256(octets).hexdigest()
</code></pre>
""",
        "objective": "Créez une fonction 'generer_empreinte_sha256(texte)' qui retourne l'empreinte SHA-256 hexadécimale de n'importe quel texte avec le module natif hashlib.",
        "starter_code": """# EXO 3/3 : CRYPTOGRAPHIE & EMPREINTE SHA-256
# TODO : Implémentez 'generer_empreinte_sha256(texte)' avec le module hashlib.

import hashlib

def generer_empreinte_sha256(texte):
    pass

if __name__ == "__main__":
    print("Empreinte :", generer_empreinte_sha256("BAAY_FAAL_SOVEREIGN"))
""",
        "test_suite": """
import unittest
import hashlib

class TestLesson3_3(unittest.TestCase):
    def test_hash(self):
        expected = hashlib.sha256("test".encode('utf-8')).hexdigest()
        self.assertEqual(generer_empreinte_sha256("test"), expected)

if __name__ == '__main__':
    unittest.main()
""",
        "hint": "Convertissez d'abord `texte.encode('utf-8')` puis déduisez `hashlib.sha256(...).hexdigest()`."
    },

    # =========================================================================
    # MODULE 4 : NETWORK PROTOCOL & BOSS CAPSTONE ENGINE (3 Exercices)
    # =========================================================================
    {
        "id": "py_4_1",
        "module_number": 4,
        "module_title": "MODULE 4 : NETWORK PROTOCOL & CAPSTONE ENGINE",
        "exercise_number": 1,
        "exercise_title": "Exo 1/3 : Formateur d'En-têtes HTTP Natif",
        "title": "4.1 : Protocoles Réseau & En-têtes HTTP",
        "course_content": """
<h3>📖 DOCUMENTATION OFFICIELLE : SPÉCIFICATION RÉSEAU HTTP/1.1</h3>

<h4>1. Structure d'un En-tête HTTP (RFC 7230)</h4>
<p>Le protocole HTTP/1.1 est un protocole réseau textuel. Les lignes d'en-tête sont séparées par la séquence de saut de ligne standard internet <code>\\r\\n</code> (CRLF).</p>

<h4>2. Rôle des En-têtes <code>Content-Type</code> et <code>Content-Length</code></h4>
<ul>
  <li><code>Content-Type</code> : Spécifie le type MIME du corps (ex: <code>application/json</code>).</li>
  <li><code>Content-Length</code> : Indique la taille exacte en octets du corps de la réponse.</li>
</ul>

<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--accent-amber); padding: 8px 12px; margin: 10px 0;">
  <strong>💡 Analogie du monde réel :</strong> C'est le bordereau d'expédition recommandé de la Poste : il indique au navigateur client le format de la marchandise et sa taille exacte avant de commencer le téléchargement du paquet.
</div>

<h4>📌 Syntaxe de référence officielle :</h4>
<pre><code class="language-python">def formater_entete_http(content_type, length):
    return f"Content-Type: {content_type}\\r\\nContent-Length: {length}"
</code></pre>
""",
        "objective": "Créez une fonction 'formater_entete_http(content_type, length)' qui retourne la chaîne d'en-tête HTTP formatée exactement : 'Content-Type: <content_type>\\r\\nContent-Length: <length>'.",
        "starter_code": """# EXO 1/3 : FORMATEUR D'EN-TÊTES HTTP
# TODO : Implémentez 'formater_entete_http(content_type, length)'.

def formater_entete_http(content_type, length):
    pass

if __name__ == "__main__":
    print(repr(formater_entete_http("application/json", 42)))
""",
        "test_suite": """
import unittest

class TestLesson4_1(unittest.TestCase):
    def test_headers(self):
        self.assertEqual(formater_entete_http("application/json", 42), "Content-Type: application/json\\r\\nContent-Length: 42")

if __name__ == '__main__':
    unittest.main()
""",
        "hint": "Formatez avec une f-string : `f'Content-Type: {content_type}\\r\\nContent-Length: {length}'`."
    },
    {
        "id": "py_4_2",
        "module_number": 4,
        "module_title": "MODULE 4 : NETWORK PROTOCOL & CAPSTONE ENGINE",
        "exercise_number": 2,
        "exercise_title": "Exo 2/3 : Décodeur de Payloads Réseau",
        "title": "4.2 : Sérialisation & Payloads Réseau",
        "course_content": """
<h3>📖 DOCUMENTATION OFFICIELLE : PARSING & DECODAGE DE PAYLOADS REST</h3>

<h4>1. Extraction et Validation des Requêtes JSON</h4>
<p>Les API REST reçoivent des requêtes HTTP brutes. L'agent doit extraire le JSON reçu, le désérialiser et vérifier l'existence des paramètres requis.</p>

<h4>2. Protection contre les données manquantes</h4>
<p>Utiliser <code>data.get("goal", "")</code> permet d'extraire la propriété recherchée de façon sécurisée en évitant d'interrompre le serveur si la propriété est absente.</p>

<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--accent-amber); padding: 8px 12px; margin: 10px 0;">
  <strong>💡 Analogie du monde réel :</strong> C'est le trieur automatique de commandes d'une banque : il ouvre le fichier d'ordre de virement, vérifie la clé 'goal' et transmet l'instruction au processeur central.
</div>

<h4>📌 Syntaxe de référence officielle :</h4>
<pre><code class="language-python">import json

def decoder_payload_goal(raw_json):
    try:
        data = json.loads(raw_json)
        return data.get("goal", "")
    except Exception:
        return ""
</code></pre>
""",
        "objective": "Créez 'decoder_payload_goal(raw_json)' qui prend une chaîne JSON brute et retourne la valeur de la clé 'goal' (ou une chaîne vide '' si la clé est absente ou le JSON invalide).",
        "starter_code": """# EXO 2/3 : DÉCODEUR DE PAYLOADS RÉSEAU
# TODO : Implémentez 'decoder_payload_goal(raw_json)'.

import json

def decoder_payload_goal(raw_json):
    pass

if __name__ == "__main__":
    print("Goal :", decoder_payload_goal('{"goal": "Build Agent"}'))
""",
        "test_suite": """
import unittest

class TestLesson4_2(unittest.TestCase):
    def test_payload(self):
        self.assertEqual(decoder_payload_goal('{"goal": "Build Agent"}'), "Build Agent")
        self.assertEqual(decoder_payload_goal('{"other": 1}'), "")
        self.assertEqual(decoder_payload_goal('invalid'), "")

if __name__ == '__main__':
    unittest.main()
""",
        "hint": "Utilisez `try: return json.loads(raw_json).get('goal', '') except Exception: return ''`."
    },
    {
        "id": "py_4_3",
        "module_number": 4,
        "module_title": "MODULE 4 : NETWORK PROTOCOL & CAPSTONE ENGINE",
        "exercise_number": 3,
        "exercise_title": "Exo 3/3 : Boss Capstone — Serveur HTTP/1.1 Natif",
        "title": "4.3 : Boss Capstone Project — Serveur HTTP Natif",
        "course_content": """
<h3>🏆 DOCUMENTATION OFFICIELLE : PROJET CAPSTONE — SERVEUR HTTP/1.1 NATIF</h3>
<p>Vous êtes arrivé au <strong>Projet Capstone d'Ingénierie Python</strong>. Vous allez fabriquer le composant fondamental utilisé par tous les serveurs Web autonomes (http.server, Flask, FastAPI) pour construire des réponses HTTP/1.1 conformes.</p>

<h4>Structure Officielle d'une Réponse HTTP/1.1 :</h4>
<pre><code class="language-http">HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: &lt;longueur&gt;\r\n\r\n&lt;corps_json&gt;</code></pre>

<div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--accent-amber); padding: 8px 12px; margin: 10px 0;">
  <strong>💡 Analogie du monde réel :</strong> Vous construisez ici le moteur d'assemblage d'usine qui scelle la réponse officielle du serveur avant d'émettre les paquets TCP vers le navigateur du client.
</div>

<h4>📌 Syntaxe de référence officielle :</h4>
<pre><code class="language-python">import json

def construire_reponse_http(status_code, body_dict):
    body_str = json.dumps(body_dict)
    length = len(body_str)
    headers = f"HTTP/1.1 {status_code} OK\\r\\nContent-Type: application/json\\r\\nContent-Length: {length}\\r\\n\\r\\n"
    return headers + body_str
</code></pre>
""",
        "objective": "Projet Capstone : Créez 'construire_reponse_http(status_code, body_dict)' qui sérialise le dictionnaire body_dict en JSON, calcule sa longueur, et produit une réponse HTTP/1.1 textuelle complète et conforme.",
        "starter_code": """# EXO 3/3 : BOSS CAPSTONE PROJECT — SERVEUR HTTP/1.1 NATIF
# TODO : Implémentez 'construire_reponse_http(status_code, body_dict)' d'après la spécification HTTP.

import json

def construire_reponse_http(status_code, body_dict):
    pass

if __name__ == "__main__":
    print(repr(construire_reponse_http(200, {"status": "ok"})))
""",
        "test_suite": """
import unittest
import json

class TestLesson4_3(unittest.TestCase):
    def test_http_resp(self):
        resp = construire_reponse_http(200, {"status": "ok"})
        self.assertTrue(resp.startswith("HTTP/1.1 200 OK"))
        self.assertIn("Content-Type: application/json", resp)
        body = json.dumps({"status": "ok"})
        self.assertIn(f"Content-Length: {len(body)}", resp)
        self.assertTrue(resp.endswith(body))

if __name__ == '__main__':
    unittest.main()
""",
        "hint": "Convertissez d'abord `body_str = json.dumps(body_dict)` puis formatez `f'HTTP/1.1 {status_code} OK\\r\\nContent-Type: application/json\\r\\nContent-Length: {len(body_str)}\\r\\n\\r\\n{body_str}'`."
    }
]


def get_lesson_by_index(index: int) -> Dict[str, Any]:
    """
    Récupère l'exercice correspondant à l'index (0-based, de 0 à 11).
    """
    total = len(PYTHON_CURRICULUM)
    if index >= total:
        last = PYTHON_CURRICULUM[-1].copy()
        last["is_completed_all"] = True
        last["percent"] = 100
        return last

    lesson = PYTHON_CURRICULUM[index].copy()
    lesson["total_lessons"] = total
    lesson["percent"] = int((index / total) * 100)
    return lesson
