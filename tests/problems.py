# Depends on: adder
from adder import problem
import os
import unittest

import tests.config as config

class NQueensTest(unittest.TestCase):
    def print_state(self, state):
        size = len(state)
        for row in range(size):
            print("".join("X" if state[col] == row else "-" for col in range(size)))

    def assertHeuristic(self, state, expected_value):
        factory = problem.ProblemFactory()
        size = len(state)
        queens = factory.from_nqueens(size, initial=state)
        self.assertEqual(problem._NQueensProblem.attacking(queens.initial.state), expected_value)

    def assertActions(self, state):
        factory = problem.ProblemFactory()
        size = len(state)
        queens = factory.from_nqueens(size, initial=state)
        actions_len = sum(1 for _ in queens.actions_iter(queens.initial.state))
        self.assertEqual(actions_len, size * (size - 1))
    
    def test_heuristic(self):
        self.assertHeuristic((4, 5, 6, 3, 4, 5, 6, 5), 17)
        self.assertHeuristic((7, 2, 6, 3, 1, 4, 0, 5), 1)


    def test_actions(self):
        self.assertActions((4, 5, 6, 3, 4, 5, 6, 5))
        self.assertActions((7, 2, 6, 3, 1, 4, 0, 5))

        
if __name__ == "__main__":
    unittest.main()