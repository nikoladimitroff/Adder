import unittest

from adder import logic, fologic, proplogic, cnfparser
from adder.problem import FAILURE

class HelperTests(unittest.TestCase):
    def assert_unification(self, first, second, expected, theta={}):
        #print(logic.unify(first, second, theta))
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
        self.assert_unification("Sells(West, M1, x2)", "Sells(West, x3, Nono)", {'x0': 'West', 'x1': 'x4', 'x4': 'M1', "x2": "Nono", "x3": "M1"}, theta={'x0': 'West', 'x1': 'x4', 'x4': 'M1'})
        self.assert_unification("Knows(John, x)", "Knows(y, Bill)", {"x": "Bill", "y": "John"})
        self.assert_unification("Knows(John, x)", "Knows(y, Mother(y))", {"x": "Mother(y)", "y": "John"})
        self.assert_unification("Knows(x, John)", "Knows(y, Mother(y))", FAILURE)
        self.assert_unification("Knows(John, x)", "Knows(x, Elizabeth)", FAILURE)
        self.assert_unification("P(x, Y, Z)", "P(X, y, z)", {"x":"X", "y":"Y", "z":"Z"})
        self.assert_unification("Sells(West, M1, x)", "Sells(y, M1, Nono)",
                                {"x": "Nono", "y": "West"})
        self.assert_unification("F(u, G(v, T(x, y), z), p)",
                                "F(U, G(V, T(X, Y), Z), P)",
                                {var: var.upper() for var in list("uvxyzp")})

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
        self.assert_standardize("V x(E y(P(x) & Q(y)))", "V x0(E x1(P(x0) & Q(x1)))")


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

        self.equalsKB = fologic.DefiniteKnowledgeBase("""
            =(x, x)
            =(x, y) & =(y, z) => =(x, z)
            =(x, y) => =(y, x)
            =(Turing, Klenee)
            =(Klenee, Church)
         """)

    def assert_query(self, kb, query, expected):
        self.assertEqual(kb.ask(query), expected)

    def test_backward_chaining(self):
        self.assert_query(self.criminalKB, "Criminal(x)", {"x": "West"})
        self.assert_query(self.criminalKB, "Enemy(x, America)", {"x": "Nono"})
        self.assert_query(self.natKB, "Nat(Plus1(Plus1(0)))", {})
        self.assert_query(self.natKB, "Nat(2)", FAILURE)
        self.assert_query(self.equalsKB, "=(Turing, Church)", {})
        self.assert_query(self.equalsKB, "=(Church, Turing)", {})
        self.assert_query(self.equalsKB, "=(Turing, Turing)", {})


class CnfTests(unittest.TestCase):
    # This class uses Square braces [] instead of () for grouping disjunctions
    # in tests
    def assert_cnf(self, sentence, expected):
        result = cnfparser.parse_fo_sentence(sentence)
        for i, cnf in enumerate(expected):
            expected[i] = [{symbol.strip() for symbol in
                             conjunct.replace("[", "").replace("]", "").split("|")
                            }
                            for conjunct in cnf.split("&")
                            if len(conjunct) != 0
                           ]
            expected[i] = set(frozenset(s) for s in expected[i])
        result = set(result)
        self.assertIn(result, expected)

    def test_cnf(self):
        tests = {
            "V x(V y(Animal(y) => Loves(x, y)) => E z(Loves(z, x)))": [
                "[Animal(SF1(x)) | Loves(SF2(x), x)] & [!Loves(x, SF1(x)) | Loves(SF2(x), x)]",
                "[Animal(SF2(x)) | Loves(SF1(x), x)] & [!Loves(x, SF2(x)) | Loves(SF1(x), x)]",
            ],
            "P(A) => Q(B)": [
                "[!P(A) | Q(B)]",
            ],
            "E x(P(x)) => V y(Q(y))": [
                "!P(x) | Q(y)"
            ]
        }
        for formula, expected in tests.items():
            self.assert_cnf(formula, expected)


class ResolutionTests(unittest.TestCase):
    def test_criminal(self):
        kb = fologic.KnowledgeBase("""
            V x(American(x) & Weapon(y) & Sells(x, y, z) & Hostile(z) => Criminal(x))
            Owns(Nono, M1)
            Missile(M1)
            V x(Missile(x) & Owns(Nono, x) => Sells(West, x, Nono))
            V x(Missile(x) => Weapon(x))
            V x(Enemy(x, America) => Hostile(x))
            American(West)
            Enemy(Nono, America)
        """, 5, False)

        self.assertTrue(kb.ask("Criminal(West)"))

        kb = fologic.KnowledgeBase("""
            V x(V y(Animal(y) => Loves(x, y)) => E z(Loves(z, x)))
            V x(E y(Animal(y) & Kills(x, y)) => V z(!Loves(z, x)))
            V x(Animal(x) => Loves(x, Jack))
            Cat(Tuna)
            Kills(Jack, Tuna) | Kills(Curiosity, Tuna)
            V x(Cat(x) => Animal(x))
        """, 3, False)

        self.assertTrue(kb.ask("Kills(Curiosity, Tuna)"))
        self.assertFalse(kb.ask("!Kills(Curiosity, Tuna)"))
        self.assertFalse(kb.ask("Kills(Jack, Tuna)"))
        self.assertTrue(kb.ask("!Kills(Jack, Tuna)"))
