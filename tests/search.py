# Depends on: adder, tests.config

from adder import graphs
from adder import problem
from adder import search
from tests import config

import functools
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
        
    def run_search(self, search_algorithm, graph_file_name, start_node, end_node):    
        loader = graphs.GraphLoader()
        graph = loader.from_file(config.TEST_DATA[graph_file_name])
        
        factory = problem.ProblemFactory()
        problem_instance = factory.from_graph(graph, start_node, end_node)
        
        solution = search_algorithm(problem_instance)
        return (problem_instance, solution)
        
    def assert_cost(self, problem_instance, solution, expected):        
        # Compare the expected cost with the actual cost
        actual_cost = problem_instance.solution_cost(solution)
        expected_cost = 0
        for i in range(len(expected) - 1):
            expected_cost += problem_instance.step_cost(expected[i][0], expected[i + 1][0])
            
        self.assertEqual(expected_cost, actual_cost)
        
    def assert_solution(self, search_algorithm, graph_file_name, start_node, end_node, expected_sequence):
        expected = self.sequence_to_solution_format(expected_sequence)
        problem_instance, solution = self.run_search(search_algorithm, 
                                        graph_file_name, 
                                        start_node, 
                                        end_node)
        
        # If we expect failure and failure is returned, all is well
        if solution == expected_sequence == problem.FAILURE or \
           solution == expected_sequence == problem.SOLUTION_UNKNOWN:
            return
        # Else, assert that the solution matches the expected
        self.assertSequenceEqual(solution, expected)
        self.assert_cost(problem_instance, solution, expected)
        
    def assert_nondeterministic_solution(self, search_algorithm, graph_file_name, start_node, end_node, expected_sequences):
        expected = list(map(self.sequence_to_solution_format, expected_sequences))
        has_passed = False
        # Assert all outcomes. If they fail, catch the exceptions and move on.
        # This test passes iff at least one assertion passes
        for expected_outcome in expected:
            try:
                problem_instance, solution = self.run_search(search_algorithm, 
                                                graph_file_name, 
                                                start_node, 
                                                end_node)
                self.assert_cost(problem_instance, solution, expected_outcome)
                self.assertSequenceEqual(solution, expected_outcome)
            except AssertionError:
                pass
            else:
                has_passed = True
        self.assertTrue(has_passed, "Nondeterministic test failed for all sequences")
            
    
    def assert_bulgaria_disconnected(self, search_algorithm):   
        assert_disconnected = functools.partial(self.assert_solution, search_algorithm, "bulgaria_disconnected_map")
        assert_disconnected("Pernik", "Varna", problem.FAILURE)
        assert_disconnected("Varna", "Sofia", problem.FAILURE)
        assert_disconnected("Burgas", "Kustendil", problem.FAILURE)
            
class BfsTests(SearchTests):
    def test_bulgaria_disconnected(self):   
        self.assert_bulgaria_disconnected(search.bfs)
        
    def test_germany(self):   
        assert_bfs = functools.partial(self.assert_solution, search.bfs, "germany_map")
        assert_bfs("Frankfurt", "Karlsruhe", ["Frankfurt", "Mannheim", "Karlsruhe"])
        assert_bfs("Frankfurt", "Munchen", ["Frankfurt", "Kassel", "Munchen"])
        assert_bfs("Stuttgart", "Erfurt", ["Stuttgart", "Nurnberg", "Wurzburg", "Erfurt"])
        assert_bfs("Kassel", "Erfurt", ["Kassel", "Frankfurt", "Wurzburg", "Erfurt"])
        assert_bfs("Kassel", "Kassel", ["Kassel"])
        
        # Some nondetermined outcomes
        assert_bfs_nondeterministic = functools.partial(
                                        self.assert_nondeterministic_solution, 
                                        search.bfs, 
                                        "germany_map")
        solutions = [
            ["Frankfurt", "Mannheim", "Karlsruhe", "Augsburg"],
            ["Frankfurt", "Kassel", "Munchen", "Augsburg"]
        ]
        
        assert_bfs_nondeterministic("Frankfurt", "Augsburg", solutions)
        
    def test_romania(self):  
        assert_bfs = functools.partial(self.assert_solution, search.bfs, "romania_map")
        assert_bfs("Arad", "Bucharest", ["Arad", "Sibiu", "Fagaras", "Bucharest"])
        
        # Some nondetermined outcomes
        assert_bfs_nondeterministic = functools.partial(
                                        self.assert_nondeterministic_solution, 
                                        search.bfs, 
                                        "romania_map")
        solutions_rv_lugoj = [
            ["RimnicuVilcea", "Craiova", "Drobeta", "Mehadia", "Lugoj"],
            ["RimnicuVilcea", "Sibiu", "Arad", "Timisoara", "Lugoj"]
        ]
        solutions_oradea_lugoj = [
            ["Oradea", "Zerind", "Arad", "Timisoara", "Lugoj"],
            ["Oradea", "Sibiu", "Arad", "Timisoara", "Lugoj"],        
        ]
        
        assert_bfs_nondeterministic("RimnicuVilcea", "Lugoj", solutions_rv_lugoj)
        assert_bfs_nondeterministic("Oradea", "Lugoj", solutions_oradea_lugoj)
        
class DlsTests(SearchTests):
    def test_bulgaria_disconnected(self):   
        search_algo = lambda problem: search.depth_limited_search(problem, 5)
        self.assert_bulgaria_disconnected(search_algo)
        
    def test_germany(self):   
        assert_dls_0 = functools.partial(self.assert_solution, 
                        lambda problem: search.depth_limited_search(problem, 0), 
                        "germany_map")
        assert_dls_2 = functools.partial(self.assert_solution, 
                        lambda problem: search.depth_limited_search(problem, 2), 
                        "germany_map")
                        
        assert_dls_0("Frankfurt", "Karlsruhe", problem.SOLUTION_UNKNOWN)
        assert_dls_0("Frankfurt", "Frankfurt", ["Frankfurt"])
        assert_dls_2("Stuttgart", "Augsburg", problem.SOLUTION_UNKNOWN)
        assert_dls_2("Stuttgart", "Wurzburg", ["Stuttgart", "Nurnberg", "Wurzburg"])
        
        
    def test_romania(self):  
        assert_dls_0 = functools.partial(self.assert_solution, 
                        lambda problem: search.depth_limited_search(problem, 0), 
                        "romania_map")
        assert_dls_2 = functools.partial(self.assert_solution, 
                        lambda problem: search.depth_limited_search(problem, 2), 
                        "romania_map")
        assert_dls_0("Arad", "Sibiu", problem.SOLUTION_UNKNOWN)
        assert_dls_0("Urziceni", "Urziceni", ["Urziceni"])
        assert_dls_2("Bucharest", "Oradea", problem.SOLUTION_UNKNOWN)
        assert_dls_2("Arad", "RimnicuVilcea", ["Arad", "Sibiu", "RimnicuVilcea"])
        
        
class AStarTests(SearchTests):
    def test_bulgaria_disconnected(self):   
        heuristic_dict = { "Pernik": 20, "Sofia": 20, "Varna": 120, "Burgas": 120, "Dupnica": 35, "Kustendil": 35 }
        heuristic = lambda source: heuristic_dict[source]
        search_algo = lambda problem: search.astar(problem, heuristic)
        self.assert_bulgaria_disconnected(search_algo)
        
    def test_romania(self):  
        # Distances to Bucharest
        heuristic_dict = { "Arad": 366, "Bucharest": 0, "Craiova": 160,
            "Drobeta": 242, "Eforie": 161, "Fagaras": 176,
            "Giurgiu": 77, "Hirsova": 151, "Iasi": 226, "Lugoj": 244,
            "Mehadia": 241, "Neamt": 234, "Oradea": 380, "Pitesti": 100,
            "RimnicuVilcea": 193, "Sibiu": 253, "Timisoara": 329,
            "Urziceni": 80, "Vaslui": 199, "Zerind": 374
        }
        heuristic = lambda source: heuristic_dict[source]
        assert_astar = functools.partial(self.assert_solution, 
                        lambda problem: search.astar(problem, heuristic), 
                        "romania_map")
        assert_astar("Arad", "Bucharest", ["Arad", "Sibiu", "RimnicuVilcea", "Pitesti", "Bucharest"])
        
    def test_bulgaria(self):
        # Straight line distances to Pernik
        # source http://distance.bg360.net/
        pernik_dist = { "Sofia": 25.4, "Pernik": 0, "Kustendil": 45.3, "Dupnica": 38, "Blagoevgrad": 65, 
            "Sandanski": 117, "Kulata": 138, "Botevgrad": 70, "Vraca": 80, "Montana": 90, "Belogradchik": 117, 
            "Lom": 136, "Vidin": 155, "Lovech": 149, "Pleven": 156, "Tarnovo": 217, "Biala": 239, "Ruse": 274,
            "Razgrad": 303, "Shumen": 326, "Dobrich": 403, "Silistra": 381, "Varna": 402, "Burgas": 362.9, 
            "Iambol": 284, "Plovdiv": 149, "Karlovo": 144, "StaraZagora": 214, "Kazanlak": 192, "Gabrovo": 188, 
            "Haskovo": 220, "Kardzhali": 221, "Smolian": 178, "Pazardzhik": 116, "Pirdop": 93, "Troian": 140, "Sliven": 269
        }
        
        heuristic = lambda town: pernik_dist[town]
        assert_astar = functools.partial(self.assert_solution,
                        lambda problem: search.astar(problem, heuristic),
                        "bulgaria_map")
                        
        assert_astar("Varna", "Pernik", ['Varna', 'Shumen', 'Tarnovo', 'Botevgrad', 'Sofia', 'Pernik'])
        assert_astar("Vidin", "Pernik", ['Vidin', 'Montana', 'Sofia', 'Pernik'])
        assert_astar("Silistra", "Pernik", ['Silistra', 'Ruse', 'Biala', 'Lovech', 'Botevgrad', 'Sofia', 'Pernik'])


class AStarNPuzzleTests(SearchTests):    
    def assert_npuzzle(self, heuristic, initial, goal, expected_solution_length):
        problem_factory = problem.ProblemFactory()
        problem_instance = problem_factory.from_npuzzle(initial, goal)
        h = functools.partial(heuristic, problem_instance)
        solution = search.astar(problem_instance, h)
        self.assertEqual(len(solution), expected_solution_length)

    def test_npuzzle(self): 
        def manhattan_heuristic(problem_instance,state):
           scoords = [problem_instance.coords_of(state, num) for num in state.split()]
           gcoords = [problem_instance.coords_of(state, num) for num in problem_instance.goal.split()]
           diff = [abs(scoords[i][0] - gcoords[i][0]) + abs(scoords[i][1] - gcoords[i][1]) for i in range(0, len(state.split()) - 1)]
           s = sum(diff)
           return s

        self.assert_npuzzle(manhattan_heuristic, "6 4 8 0 1 2 10 11 5 13 3 14 15 7 12 9", " 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0", 35)
        self.assert_npuzzle(manhattan_heuristic, "8 3 0 4 2 6 1 5 7", "0 1 2 3 4 5 6 7 8", 27)
        self.assert_npuzzle(manhattan_heuristic, "4 2 5 3 6 8 1 7 0", "0 1 2 3 4 5 6 7 8", 15)


if __name__ == "__main__":
    unittest.main()