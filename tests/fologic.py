import unittest

from adder import fologic
from adder.problem import FAILURE

class HelperTests(unittest.TestCase):

    def assert_unification(self, first, second, expected):
        self.assertEqual(fologic.unify(first, second), expected)

    def assert_standardize(self, expression, expected, var="x", index=0):
        self.assertEqual(fologic.standardize_variables(expression, var, index), expected)

    def test_unification(self):
        self.assert_unification("A", "A", {})
        self.assert_unification("x", "A", {"x": "A"})
        self.assert_unification("Knows(John, x)", "Knows(John, Jane)", {"x": "Jane" })
        self.assert_unification("Knows(John, x)", "Knows(y, Bill)", {"x": "Bill", "y": "John"})
        self.assert_unification("Knows(John, x)", "Knows(y, Mother(y))", {"x": "Mother(y)", "y": "John"})
        self.assert_unification("Knows(x, John)", "Knows(y, Mother(y))", FAILURE)
        self.assert_unification("Knows(John, x)", "Knows(x, Elizabeth)", FAILURE)

    def test_skolemization(self):
        self.fail()

    def test_standardize(self):
        self.assert_standardize("V x: E y: P(x) & Q(y)", "V x0: E x1: P(x0) & Q(x1)")
        

class ChainingTests(unittest.TestCase):
    pass
#    def __init__(self, *args):
#        unittest.TestCase.__init__(self, *args)
#        self.kb = fologic.DefiniteKnowledgeBase("""
#            American(x) & Weapon(y) & Sells(x, y,z) & Hostile(z) => Criminal(x)
#            Owns(Nono, M1)
#            Missile(M1)
#            Missile(x) & Owns(Nono, x ) => Sells( West,x, Nono)
#            Missile(x) => Weapon(x)
#            Enemy(x, America) => Hosti!e(x)
#            American(West)
#            Enemy(Nono, America)
#            """)

#    def forward_chaining(self):
#        print(self.kb.ask("Criminal(West)"))