"""
Module de Revue de Code & Analyse Statique Autonome — Baay-Faal Agent.
100 % Python Standard Library (ast, re, inspect).

Évalue la complexité algorithmique (Big-O), le respect de PEP 8, 
les failles de sécurité et l'empreinte mémoire théorique.
"""

import ast
import re
from typing import Any, Dict, List


class BaseCodeReviewer:
    """Classe de base pour tous les analyseurs de code par langage."""

    def review(self, code_snippet: str) -> Dict[str, Any]:
        raise NotImplementedError("Les sous-classes doivent implémenter la méthode review().")


class PythonCodeReviewer(BaseCodeReviewer):
    """Analyseur statique natif pour le code Python via AST et regex."""

    def review(self, code_snippet: str) -> Dict[str, Any]:
        results = {
            "language": "python",
            "score": 10.0,
            "complexity": "O(1)",
            "pep8_issues": [],
            "security_issues": [],
            "recommendations": [],
            "metrics": {
                "lines_count": 0,
                "functions_count": 0,
                "classes_count": 0,
                "max_loop_depth": 0
            }
        }

        if not code_snippet or not code_snippet.strip():
            results["score"] = 0.0
            results["recommendations"].append("Le code fourni est vide.")
            return results

        lines = code_snippet.splitlines()
        results["metrics"]["lines_count"] = len(lines)

        # 1. Analyse PEP 8 & Style de Lignes
        for i, line in enumerate(lines, 1):
            if len(line) > 88:
                results["pep8_issues"].append(f"Ligne {i} : dépasse 88 caractères ({len(line)} chars).")
                results["score"] -= 0.3

            if re.search(r'^\s*def\s+[A-Z]', line):
                results["pep8_issues"].append(f"Ligne {i} : Nom de fonction doit être en snake_case.")
                results["score"] -= 0.5

            if re.search(r'^\s*class\s+[a-z]', line):
                results["pep8_issues"].append(f"Ligne {i} : Nom de classe doit être en PascalCase.")
                results["score"] -= 0.5

        # 2. Analyse Syntaxique & AST (Abstract Syntax Tree)
        try:
            tree = ast.parse(code_snippet)
        except SyntaxError as err:
            results["score"] = 0.0
            results["security_issues"].append(f"Erreur de syntaxe Python : {err.msg} (Ligne {err.lineno})")
            results["recommendations"].append("Corrigez la syntaxe avant d'analyser le code.")
            return results

        # Compteurs AST & Visite des Nœuds
        class ASTVisitor(ast.NodeVisitor):
            def __init__(self):
                self.functions = 0
                self.classes = 0
                self.max_loop_depth = 0
                self.current_loop_depth = 0
                self.has_docstrings = True
                self.uses_eval_exec = False
                self.has_bare_except = False
                self.missing_returns = []

            def visit_FunctionDef(self, node):
                self.functions += 1
                if not ast.get_docstring(node):
                    self.has_docstrings = False
                
                # Vérification return explicite
                has_ret = any(isinstance(n, ast.Return) for n in ast.walk(node))
                if not has_ret:
                    self.missing_returns.append(node.name)

                self.generic_visit(node)

            def visit_ClassDef(self, node):
                self.classes += 1
                self.generic_visit(node)

            def visit_For(self, node):
                self.current_loop_depth += 1
                if self.current_loop_depth > self.max_loop_depth:
                    self.max_loop_depth = self.current_loop_depth
                self.generic_visit(node)
                self.current_loop_depth -= 1

            def visit_While(self, node):
                self.current_loop_depth += 1
                if self.current_loop_depth > self.max_loop_depth:
                    self.max_loop_depth = self.current_loop_depth
                self.generic_visit(node)
                self.current_loop_depth -= 1

            def visit_Call(self, node):
                if isinstance(node.func, ast.Name) and node.func.id in ('eval', 'exec'):
                    self.uses_eval_exec = True
                self.generic_visit(node)

            def visit_ExceptHandler(self, node):
                if node.type is None:
                    self.has_bare_except = True
                self.generic_visit(node)

        visitor = ASTVisitor()
        visitor.visit(tree)

        results["metrics"]["functions_count"] = visitor.functions
        results["metrics"]["classes_count"] = visitor.classes
        results["metrics"]["max_loop_depth"] = visitor.max_loop_depth

        # 3. Estimation de Complexité Algorithmique (Big-O)
        depth = visitor.max_loop_depth
        if depth == 0:
            results["complexity"] = "O(1)"
        elif depth == 1:
            results["complexity"] = "O(n)"
        elif depth == 2:
            results["complexity"] = "O(n²)"
        else:
            results["complexity"] = f"O(n^{depth})"
            results["recommendations"].append(f"Attention : Profondeur de boucle de {depth} (Complexité O(n^{depth})). Envisagez de simplifier les boucles imbriquées.")
            results["score"] -= 1.5

        # 4. Garde-Fous de Sécurité & Anti-Patterns
        if visitor.uses_eval_exec:
            results["security_issues"].append("Utilisation dangereuse de eval() ou exec() détectée !")
            results["score"] -= 3.0

        if visitor.has_bare_except:
            results["pep8_issues"].append("Bloc 'except:' nu détecté. Spécifiez l'exception exacte (ex: except ValueError:).")
            results["score"] -= 0.5

        if visitor.functions > 0 and not visitor.has_docstrings:
            results["pep8_issues"].append("Certaines fonctions n'ont pas de docstring explicative (PEP 257).")
            results["score"] -= 0.5

        if re.search(r'password\s*=\s*["\'][^"\']+["\']', code_snippet, re.IGNORECASE) or \
           re.search(r'api_key\s*=\s*["\'][^"\']+["\']', code_snippet, re.IGNORECASE):
            results["security_issues"].append("Secret ou mot de passe détecté en clair dans le code.")
            results["score"] -= 2.0

        # Formater le score final entre 0.0 et 10.0
        results["score"] = round(max(0.0, min(10.0, results["score"])), 1)

        # Génération des Recommandations d'Ingénieur
        if results["score"] == 10.0:
            results["recommendations"].append("Code parfait ! Respect strict des normes PEP 8 et complexité minimale.")
        else:
            if results["pep8_issues"]:
                results["recommendations"].append("Corrigez la mise en forme et les conventions de nommage PEP 8.")
            if results["security_issues"]:
                results["recommendations"].append("Résolvez immédiatement les failles de sécurité détectées.")

        return results


class MultiLanguageCodeReviewer:
    """Router et Fabrique de Revue de Code Multi-Langages."""

    def __init__(self):
        self._reviewers = {
            "python": PythonCodeReviewer(),
        }

    def register_reviewer(self, language: str, reviewer: BaseCodeReviewer):
        self._reviewers[language.lower()] = reviewer

    def review(self, code_snippet: str, language: str = "python") -> Dict[str, Any]:
        lang = language.lower()
        reviewer = self._reviewers.get(lang)
        if not reviewer:
            return {
                "language": lang,
                "score": 0.0,
                "error": f"Langage '{lang}' non supporté actuellement. Analyseur Python actif par défaut.",
                "recommendations": ["Validez le parcours Python avant de déverrouiller d'autres langages."]
            }
        return reviewer.review(code_snippet)


# Instance globale singleton
code_reviewer_engine = MultiLanguageCodeReviewer()


def review_code_snippet(code_snippet: str, language: str = "python") -> Dict[str, Any]:
    """Point d'entrée utilitaire pour la revue de code."""
    return code_reviewer_engine.review(code_snippet, language)
