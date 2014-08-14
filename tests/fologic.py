import unittest

from adder import logic, fologic
from adder.problem import FAILURE

class HelperTests(unittest.TestCase):
    def assert_unification(self, first, second, expected, theta={}):
        self.assertEqual(logic.unify(first, second, theta), expected)

    def assert_standardize(self, expression, expected):
        standart, var_map = logic.standardize_variables(expression, use_global=False)
        self.assertEqual(standart, expected)

    def assert_skolemization(self, expression, expected):
        skolemized = logic.skolemize(expression, logic.Skolemizer())
        self.assertIn(skolemized, expected)

    def test_unification(self):
        self.assert_unification("A", "A", {})
        self.assert_unification("Knows(John, Elizabeth)", "Knows(John, Elizabeth)", {})
        self.assert_unification("x", "A", {"x": "A"})
        self.assert_unification("Knows(John, x)", "Knows(John, Jane)", {"x": "Jane" })
        self.assert_unification("Knows(John, x)", "Knows(y, Bill)", {"x": "Bill", "y": "John"})
        self.assert_unification("Knows(John, x)", "Knows(y, Mother(y))", {"x": "Mother(y)", "y": "John"})
        self.assert_unification("Knows(x, John)", "Knows(y, Mother(y))", FAILURE)
        self.assert_unification("Knows(John, x)", "Knows(x, Elizabeth)", FAILURE)
        self.assert_unification("P(x, Y, Z)", "P(X, y, z)", {"x":"X", "y":"Y", "z":"Z"})
        #self.assert_unification("Sells(West, M1, x2)", "Sells(x, 2M1, Nono)", {},

    def test_skolemization(self):
        tests = {
            "V x(E y(Animal(y) & !Loves(x, y)) | E z(Loves(z, x)))": [
                "V x((Animal(SF1(x)) & !Loves(x, SF1(x))) | (Loves(SF2(x), x)))",
                "V x((Animal(SF2(x)) & !Loves(x, SF2(x))) | (Loves(SF1(x), x)))",
            ],
            "V x(Philo(x) => E y(Book(y) & HasWrote(x, y)))": [
                "V x(Philo(x) => (Book(SF1(x)) & HasWrote(x, SF1(x))))",
            ],
            "E x, y(Philo(x) & Student(y) & Teaches(x, y))": [
                "(Philo(SC1) & Student(SC2) & Teaches(SC1, SC2))",
                "(Philo(SC2) & Student(SC1) & Teaches(SC2, SC1))",
            ],
            "V p, q(S(p, q) <=> E r(r) & E z(z)) & E t(t | V s(s <=> V s1(O(s1))))": [
                "V p, q(S(p, q) <=> (SF1(p, q)) & (SF2(p, q))) & (SC1 | V s(s <=> V s1(O(s1))))",
                "V p, q(S(p, q) <=> (SF2(p, q)) & (SF1(p, q))) & (SC1 | V s(s <=> V s1(O(s1))))",
            ],
            "V x(V y(V z(E u(P(x, y, z, u)))))": [
                "V x(V y(V z((P(x, y, z, SF1(x, y, z))))))"
            ]
        }


        for expression, expected in tests.items():
            self.assert_skolemization(expression, expected)

    def test_standardize(self):
        self.assert_standardize("V x: E y: P(x) & Q(y)", "V x0: E x1: P(x0) & Q(x1)")


class ChainingTests(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.criminalKB = fologic.DefiniteKnowledgeBase("""
            American(x) & Weapon(y) & Sells(x, y, z) & Hostile(z) => Criminal(x)
            Owns(Nono, M1)
            Missile(M1)
            Missile(x) & Owns(Nono, x) => Sells(West, x, Nono)
            Missile(x) => Weapon(x)
            Enemy(x, America) => Hostile(x)
            American(West)
            Enemy(Nono, America)
        """)

        self.natKB = fologic.DefiniteKnowledgeBase("""
            Nat(0)
            Nat(x) => Nat(Plus1(x))
        """)

    def assert_query(self, kb, query, expected):
        self.assertEqual(kb.ask(query), expected)

    def test_backward_chaining(self):
        self.assert_query(self.criminalKB, "Criminal(x)", {"x": "West"})
        self.assert_query(self.criminalKB, "Enemy(x, America)", {"x": "Nono"})
        self.assert_query(self.natKB, "Nat(Plus1(Plus1(0)))", {})
        self.assert_query(self.natKB, "Nat(2)", FAILURE)
