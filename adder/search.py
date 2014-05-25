# Depends on: problem.py
from adder.problem import FAILURE
from adder.problem import SOLUTION_UNKNOWN
from itertools import count
from collections import defaultdict
import random
import math

# <uninformed searches>

def bfs(problem):
    visited = set()
    frontier = []
    
    node = problem.initial
    if problem.goal_test(node.state):
        return problem.construct_solution(node)
        
    frontier.append(node)
    while len(frontier) != 0:
        node = frontier.pop(0)
        if node not in visited:
            visited.add(node)
            for action in problem.actions_iter(node.state):
                child = problem.child_node(node, action)
                if child not in frontier:
                    if problem.goal_test(child.state):
                        return problem.construct_solution(child)
                    frontier.append(child)
                
    return FAILURE
    
    
def depth_limited_search(problem, max_depth):
    return __recursive_dls(problem, problem.initial, {problem.initial}, max_depth)
    
    
def __recursive_dls(problem, node, visited, max_depth):
    if problem.goal_test(node.state):
        return problem.construct_solution(node)

    if max_depth == 0:
        return SOLUTION_UNKNOWN
    
    unknown_occured = False
    for action in problem.actions_iter(node.state):
        child = problem.child_node(node, action)
        if child not in visited:
            visited.add(child)
            child_dls = __recursive_dls(problem, child, set(visited), max_depth - 1)
            if child_dls is SOLUTION_UNKNOWN:
                unknown_occured = True
            elif child_dls is not FAILURE:
                return child_dls   
            
    return SOLUTION_UNKNOWN if unknown_occured else FAILURE
    
def dfs(problem):
    return depth_limited_search(problem, float("inf"))
    
def iterative_deepening_dfs(problem, max_depth=float("inf")):
    for depth in count():
        result = depth_limited_search(problem, depth)
        if result is not SOLUTION_UNKNOWN:
            return result
            
# </uninformed searches>

def __astar_key_comparer(pair):
    return pair[0]

    
def astar(problem, heuristic):
    visited = set()
    node = problem.initial
    frontier = [node]
    
    f_values = { node: heuristic(node.state)}
    g_values = { node: 0 }
    nodes_generated = 0
    while len(frontier) != 0:
        # Expand the node with lowest f_value
        frontier_f_scores = [(f_values[expanded], index) for index, expanded in enumerate(frontier)]
        node_index = min(frontier_f_scores, key=__astar_key_comparer)[1]
 
        node = frontier.pop(node_index)     
        visited.add(node)
        
        if problem.goal_test(node.state):
            return problem.construct_solution(node)
        
        for action in problem.actions_iter(node.state):
            child = problem.child_node(node, action)
            if child in visited: continue
            
            new_g_value = g_values[node] + problem.step_cost(node.state, action)
            child_index = -1
            for i, element in enumerate(frontier):
                if element == child:
                    child_index = i

            child_in_frontier = child_index != -1
            needs_update = child_in_frontier and new_g_value < g_values[child]
                
            if needs_update:
                # Update the node so that it has proper parent, action and cost
                frontier[child_index] = child
                
            if child not in frontier:
                frontier.append(child)
            
            if not child_in_frontier or needs_update:
                g_values[child] = new_g_value
                f_values[child] = new_g_value + heuristic(child.state)
    return FAILURE

def hill_climbing(problem, heuristic, max_sideways_walk, local_minima_acceptable=False):
    node = problem.initial
    current_cost = float("inf")
    sideway_moves = 0
    while True:
        heuristic_transform = lambda action: heuristic(problem.result(node.state, action))
        best_action = min(problem.actions_iter(node.state), key=heuristic_transform)
        cost = heuristic_transform(best_action)

        if cost > current_cost:
            return problem.construct_solution(node) if local_minima_acceptable else FAILURE
        elif cost == current_cost:
            if sideway_moves >= max_sideways_walk:
                return problem.construct_solution(node) if local_minima_acceptable else FAILURE
            sideway_moves += 1
        else:
            sideway_moves = 0

        node = problem.child_node(node, best_action)
        current_cost = cost
        if problem.goal_test(node.state):
            return problem.construct_solution(node)

def random_restart_hc(problem_generator, heuristic, max_sideways_walk, max_iterations=1<<31):
    for _ in range(max_iterations):
        solution = hill_climbing(problem_generator(), heuristic, max_sideways_walk)
        if solution != FAILURE:
            return solution

    return FAILURE

import time as TIME
def simulated_annealing(problem, heuristic, 
                        local_minima_acceptable=False, 
                        temperature_func=lambda t: math.log(1 / t), 
                        min_temperature=0.01):
    """
    Solves the problem using Simulated Annealing. The method is highly dependent on the right parameters. For best results, obey the following:
    - the temperature_func must be monothonic and slowly decreasing. The time argument will be in the range [0, 1]
    """
    #landscape = [2, 3, 4, 3, 2, 3, 5, 6, 5, 4, 5, 4, 3, 2, 3, 4, 5, 6, 7, 6, 5, 4]
    #width = len(landscape)
    #height = 8
    #def print_landscape(state):
    #    print(time, temperature_func(time))
    #    for row_index in range(height):
    #        row = [' ' if landscape[i] > row_index else ('|' if landscape[i] < row_index else ('Y' if i == state else 'T')) for i in range(width)]
    #        print("".join(row))


    node = problem.initial
    current_cost = heuristic(node.state)
    max_time = 1000
    for time in range(1, max_time):
        #print_landscape(node.state)
        if problem.goal_test(node.state):
            return problem.construct_solution(node)

        temperature = temperature_func(time / max_time) / temperature_func(1 / max_time)
        action = random.choice(list(problem.actions_iter(node.state)))
        child = problem.child_node(node, action)
        child_cost = heuristic(child.state)
        delta_cost = current_cost - child_cost

        chance = math.exp(delta_cost / temperature)
        node = child if chance >= random.random() else node

        if abs(temperature) <= min_temperature:
            break

        current_cost = heuristic(node.state)

    return problem.construct_solution(node) if local_minima_acceptable else FAILURE
