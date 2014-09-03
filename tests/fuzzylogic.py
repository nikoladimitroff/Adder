import unittest

from adder.fuzzylogic import KnowledgeBase, MembershipSets as sets

class FuzzyLogicTests(unittest.TestCase):
    def test_inference(self):
        rules = """
            funding is Adequate | staffing is Small => risk is Low
            funding is Marginal & staffing is Large => risk is Normal
            funding is Inadequate => risk is High
        """

        variables = {
            "funding": [
                ("Adequate", sets.shoulder(80, 60)),
                ("Marginal", sets.triangle(20, 50, 80)),
                ("Inadequate", sets.shoulder(20, 30)),
            ],
           # "staffing": [("Small", sets.shoulder(30, , "Large"]
            "risk": ["Low", "Normal"],
        }

    def test_membership_sets(self):
        funding_tests = [
            ("Adequate", sets.shoulder(80, 60), 0),
            ("Marginal", sets.triangle(20, 50, 80), 0.2),
            ("Inadequate", sets.shoulder(20, 30), 0),
        ]
        value = 35
        for test in funding_tests:
            print(test[1](value), test[2])
