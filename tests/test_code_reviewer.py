"""
Banc de Tests Unitaires — Module de Revue de Code (core/code_reviewer.py).
100 % Python Standard Library (unittest).
"""

import unittest
from core.code_reviewer import PythonCodeReviewer, MultiLanguageCodeReviewer, review_code_snippet


class TestCodeReviewer(unittest.TestCase):

    def setUp(self):
        self.reviewer = PythonCodeReviewer()

    def test_empty_code(self):
        res = self.reviewer.review("")
        self.assertEqual(res["score"], 0.0)
        self.assertIn("Le code fourni est vide.", res["recommendations"])

    def test_perfect_code_O1(self):
        code = '''def calculer_budget(revenu: int, depenses: int) -> int:
    """Calcule le solde budgétaire disponible."""
    return revenu - depenses
'''
        res = self.reviewer.review(code)
        self.assertEqual(res["complexity"], "O(1)")
        self.assertEqual(res["score"], 10.0)
        self.assertEqual(len(res["pep8_issues"]), 0)
        self.assertEqual(len(res["security_issues"]), 0)

    def test_complexity_On(self):
        code = '''def trouver_max(nombres):
    """Trouve la valeur maximale dans une liste."""
    max_val = nombres[0]
    for n in nombres:
        if n > max_val:
            max_val = n
    return max_val
'''
        res = self.reviewer.review(code)
        self.assertEqual(res["complexity"], "O(n)")
        self.assertEqual(res["metrics"]["max_loop_depth"], 1)

    def test_complexity_On2(self):
        code = '''def tri_a_bulles(liste):
    """Tri a bulles classique O(n2)."""
    n = len(liste)
    for i in range(n):
        for j in range(0, n-i-1):
            if liste[j] > liste[j+1]:
                liste[j], liste[j+1] = liste[j+1], liste[j]
    return liste
'''
        res = self.reviewer.review(code)
        self.assertEqual(res["complexity"], "O(n²)")
        self.assertEqual(res["metrics"]["max_loop_depth"], 2)

    def test_pep8_and_security(self):
        code = '''def MauvaiseFonction():
    password = "secret1234_insecure"
    eval("print('danger')")
    try:
        x = 1 / 0
    except:
        pass
'''
        res = self.reviewer.review(code)
        self.assertLess(res["score"], 5.0)
        self.assertTrue(any("snake_case" in issue for issue in res["pep8_issues"]))
        self.assertTrue(any("eval()" in issue for issue in res["security_issues"]))
        self.assertTrue(any("Secret" in issue for issue in res["security_issues"]))

    def test_syntax_error(self):
        code = "def ma_fonction("
        res = self.reviewer.review(code)
        self.assertEqual(res["score"], 0.0)
        self.assertTrue(any("Erreur de syntaxe" in issue for issue in res["security_issues"]))

    def test_multilanguage_router(self):
        res = review_code_snippet("x = 10", "python")
        self.assertEqual(res["language"], "python")

        res_unknown = review_code_snippet("console.log('test')", "cobol")
        self.assertIn("non supporté", res_unknown.get("error", ""))


if __name__ == '__main__':
    unittest.main()
