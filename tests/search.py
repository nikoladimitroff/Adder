# Depends on: adder, tests.config

from adder import graphs
from adder import problem
from adder import search
from tests import config
from functools import reduce
import os
import unittest

import tests.config as config

class SearchTests(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)  
        
    
    def sequence_to_solution_format(self, sequence):
        solution = [(state, state) for state in sequence]
        solution[0] = (sequence[0], None)
        return solution
        
    def assert_bfs_solution(self, graph_file_name, start_node, end_node, expected_sequence):
        expected = self.sequence_to_solution_format(expected_sequence)
        loader = graphs.GraphLoader()
        graph = loader.from_file(config.TEST_DATA[graph_file_name])
        
        factory = problem.ProblemFactory()
        problem_instance = factory.from_graph(graph, start_node, end_node)
        
        solution = search.bfs(problem_instance)
        self.assertSequenceEqual(solution, expected)
        
        # Compare the expected cost with the actual cost
        cost = problem_instance.solution_cost(solution)
        actual_cost = 0
        for i in range(len(expected) - 1):
            actual_cost += problem_instance.step_cost(expected[i][0], expected[i + 1][0])
        self.assertEqual(cost, actual_cost)
        
    def test_bfs(self):        
        self.assert_bfs_solution("germany_map", "Frankfurt", "Karlsruhe", ["Frankfurt", "Mannheim", "Karlsruhe"])
        self.assert_bfs_solution("germany_map", "Frankfurt", "Munchen", ["Frankfurt", "Kassel", "Munchen"])
        self.assert_bfs_solution("germany_map", "Stuttgart", "Erfurt", ["Stuttgart", "Nurnberg", "Wurzburg", "Erfurt"])
        self.assert_bfs_solution("germany_map", "Kassel", "Erfurt", ["Kassel", "Frankfurt", "Wurzburg", "Erfurt"])
        self.assert_bfs_solution("germany_map", "Kassel", "Kassel", ["Kassel"])
        
        
if __name__ == "__main__":
    unittest.main()