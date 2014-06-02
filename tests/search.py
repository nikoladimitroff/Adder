# Depends on: adder, tests.config
import functools
import os
import unittest
import random

from adder import graphs
from adder import problem
from adder import search
from tests import config

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
        graph = loader.from_file(config.TEST_GRAPHS[graph_file_name])
        
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
        
    def assert_solution(self, 
                        search_algorithm, 
                        graph_file_name, 
                        start_node, 
                        end_node, 
                        expected_sequence):
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
        
    def assert_nondeterministic_solution(self, 
                                         search_algorithm, 
                                         graph_file_name, 
                                         start_node, 
                                         end_node, 
                                         expected_sequences):
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
        heuristic_dict = { 
            "Arad": 366, "Bucharest": 0, "Craiova": 160,
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
        pernik_dist = { 
            "Sofia": 25.4, "Pernik": 0, "Kustendil": 45.3, "Dupnica": 38, 
            "Blagoevgrad": 65, "Sandanski": 117, "Kulata": 138, "Botevgrad": 70, "Vraca": 80, 
            "Montana": 90, "Belogradchik": 117, "Lom": 136, "Vidin": 155, "Lovech": 149, 
            "Pleven": 156, "Tarnovo": 217, "Biala": 239, "Ruse": 274, "Razgrad": 303, 
            "Shumen": 326, "Dobrich": 403, "Silistra": 381, "Varna": 402, "Burgas": 362.9, 
            "Iambol": 284, "Plovdiv": 149, "Karlovo": 144, "StaraZagora": 214, "Kazanlak": 192, 
            "Gabrovo": 188, "Haskovo": 220, "Kardzhali": 221, "Smolian": 178, "Pazardzhik": 116, 
            "Pirdop": 93, "Troian": 140, "Sliven": 269
        }
        
        heuristic = lambda town: pernik_dist[town]
        assert_astar = functools.partial(self.assert_solution,
                        lambda problem: search.astar(problem, heuristic),
                        "bulgaria_map")
                        
        assert_astar("Varna", "Pernik", ['Varna', 'Shumen', 'Tarnovo', 'Botevgrad', 'Sofia', 'Pernik'])
        assert_astar("Vidin", "Pernik", ['Vidin', 'Montana', 'Sofia', 'Pernik'])
        assert_astar("Silistra", "Pernik", ['Silistra', 'Ruse', 'Biala', 'Lovech', 'Botevgrad', 'Sofia', 'Pernik'])


class AStarNPuzzleTests(SearchTests):    
    def assert_npuzzle(self, initial, goal, expected_solution_length):
        factory = problem.ProblemFactory()
        problem_instance = factory.from_npuzzle(initial, goal)
        heuristic = factory.heuristic_for(problem_instance)
        solution = search.astar(problem_instance, heuristic)
        self.assertEqual(len(solution), expected_solution_length)

    def test_npuzzle(self): 
        if config.HARD_TESTS:
            self.assert_npuzzle("6 4 8 0 1 2 10 11 5 13 3 14 15 7 12 9", " 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0", 35)
            self.assert_npuzzle("8 3 0 4 2 6 1 5 7", "0 1 2 3 4 5 6 7 8", 27)
        self.assert_npuzzle("4 2 5 3 6 8 1 7 0", "0 1 2 3 4 5 6 7 8", 15)


class HillClimbingQueensTests(unittest.TestCase):
    def test_local_minima(self):
        factory = problem.ProblemFactory()
        local_minima = factory.from_nqueens(8, initial=(7, 2, 6, 3, 1, 4, 0, 5))
        heuristic = factory.heuristic_for(local_minima)

        solution = search.hill_climbing(local_minima, heuristic, 0, local_minima_acceptable=True)
        self.assertNotEqual(solution, problem.FAILURE)
        solution = search.hill_climbing(local_minima, heuristic, 0)
        self.assertEqual(solution, problem.FAILURE)

    def test_hill_climbing(self):
        pass

    def test_random_restart_hill_climbing(self):
        factory = problem.ProblemFactory()
        queens8_gen = functools.partial(factory.from_nqueens, 8)
        heuristic = factory.heuristic_for(queens8_gen())
        for _ in range(10):
            self.assertNotEqual(search.random_restart_hc(queens8_gen, heuristic, 100), problem.FAILURE)
            
    def test_random_restart_hill_climbing_giant_queens(self):
        factory = problem.ProblemFactory()
        size = 14
        queens_mil_gen = functools.partial(factory.from_nqueens, size)
        heuristic = factory.heuristic_for(queens_mil_gen())
        self.assertNotEqual(search.random_restart_hc(queens_mil_gen, heuristic, 100), problem.FAILURE)



class SimulatedAnnealingTests(unittest.TestCase):
    def test_simulated_annealing_success_ratio(self):
        factory = problem.ProblemFactory()
        queens8_gen = functools.partial(factory.from_nqueens, 8)
        heuristic = factory.heuristic_for(queens8_gen())
        problem_count = 10
        expected_solutions = 0.7 * problem_count 
        found_solutions = 0
        for _ in range(problem_count):
            solution = search.simulated_annealing(queens8_gen(), heuristic)
            found_solutions += 1 if solution != problem.FAILURE else 0

        self.assertGreaterEqual(found_solutions, expected_solutions)

    def test_simulated_annealing_landscape(self):
        height = 8
        landscape = [2, 3, 4, 3, 2, 3, 5, 6, 5, 4, 5, 4, 3, 2, 3, 4, 5, 6, 7, 6, 5, 4]
        state = 0
        def actions(state):
            actions = []
            if state > 0: actions.append(-1)
            if state < len(landscape) - 1: actions.append(1)
            return actions

        result = lambda state, action: state + action
        step_cost = lambda state, action: 1

        heuristic = lambda state: (height - landscape[state] - 1) / (height - 1)
        goal_state = lambda state: heuristic(state) == 0

        factory = problem.ProblemFactory()
        pr = factory.from_functions(state, actions, step_cost, result, goal_state)

        solution = search.simulated_annealing(pr, heuristic, local_minima_acceptable=True)
        self.assertNotEqual(solution, problem.FAILURE)
        final_state = solution[-1][0]
        # Assert that SA has found at least the best local minima
        self.assertLessEqual(heuristic(final_state), 1)

        
class GeneticTests(unittest.TestCase):
    
    def _reproduce_nqueens(self, father, mother, crossover):
        child = [father[i] if i < crossover else mother[i] 
                 for i in range(len(father))]
        return tuple(child)

    def _mutate_nqueens(self, state):
        column = random.randint(0, len(state) - 1)
        while True:
            row = random.randint(0, len(state) - 1)
            if state[column] != row:
                mutated = [state[i] if i != column else row
                           for i in range(len(state))]
                return tuple(mutated)

    def test_genetic_nqueens(self):
        factory = problem.ProblemFactory()
        size = 8
        state_gen = lambda: factory.from_nqueens(size).initial.state
        heuristic = factory.heuristic_for(factory.from_nqueens(size))
        most_attacking_queens = sum(range(size))
        fitness = lambda state: most_attacking_queens - heuristic(state)
        population_size = 10
        
        res = search.genetic(state_gen, fitness, most_attacking_queens, self._reproduce_nqueens, self._mutate_nqueens, population_size)
        self.assertEqual(heuristic(res), 0)


if __name__ == "__main__":
    unittest.main()