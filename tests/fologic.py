import unittest

from adder import fologic
from adder.problem import FAILURE

class UnifyTests(unittest.TestCase):

    def assert_unification(self, first, second, expected):
        self.assertEqual(fologic.unify(first, second), expected)

    def test_propositionals(self):
        self.assert_unification("A", "A", {})
        self.assert_unification("x", "A", {"x": "A"})
        self.assert_unification("Knows(John, x)", "Knows(John, Jane)", {"x": "Jane" })
        self.assert_unification("Knows(John, x)", "Knows(y, Bill)", {"x": "Bill", "y": "John"})
        self.assert_unification("Knows(John, x)", "Knows(y, Mother(y))", {"x": "Mother(y)", "y": "John"})
        self.assert_unification("Knows(x, John)", "Knows(y, Mother(y))", FAILURE)
        self.assert_unification("Knows(John, x)", "Knows(x, Elizabeth)", FAILURE)

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