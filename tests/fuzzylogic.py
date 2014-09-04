import unittest

from adder.fuzzylogic import KnowledgeBase, MembershipSets as sets

class FuzzyLogicTests(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        rules = """
            distance is Far & ammo is Plenty => desire is Desirable
            distance is Far & ammo is Ok => desire is Undesirable
            distance is Far & ammo is Low => desire is Undesirable
            distance is Medium & ammo is Plenty => desire is VeryDesirable
            distance is Medium & ammo is Ok => desire is VeryDesirable
            distance is Medium & ammo is Low => desire is Desirable
            distance is Close & ammo is Plenty => desire is Undesirable
            distance is Close & ammo is Ok => desire is Undesirable
            distance is Close & ammo is Low => desire is Undesirable
        """

        variables = {
            "desire": [
                ("VeryDesirable", sets.shoulder(75, 50)),
                ("Desirable", sets.triangle(25, 50, 75)),
                ("Undesirable", sets.shoulder(25, 50)),
            ],
            "distance": [
                ("Far", sets.shoulder(300, 150)),
                ("Medium", sets.triangle(10, 150, 300)),
                ("Close", sets.shoulder(10, 150)),
            ],
            "ammo": [
                ("Plenty", sets.shoulder(30, 10)),
                ("Ok", sets.triangle(0, 10, 30)),
                ("Low", sets.shoulder(0, 10))
            ],
        }

        max_values = {"desire": 100, "distance": 400, "ammo": 40}
        self.kb = KnowledgeBase(rules, variables, max_values, accuracy=1000)

    def test_inference(self):
        result = self.kb.ask(({"distance": 200, "ammo": 8}, "desire"))
        self.assertAlmostEqual(result, 57.49, 2)


    def assert_membership_test(self, var, value, tests):
        for member_set, expected in tests:
            self.assertAlmostEqual(self.kb.vars[var][member_set](value),
                                    expected)

    def test_membership_sets(self):
        distance_tests = [
            ("Far", 1/3),
        ]

        ammo_tests = [
            ("Plenty", 0),
            ("Ok", 0.8),
            ("Low", 0.2)
        ]

        distance, ammo = 200, 8
        self.assert_membership_test("distance", distance, distance_tests)
        self.assert_membership_test("ammo", ammo, ammo_tests)
