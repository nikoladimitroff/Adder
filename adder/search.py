# Depends on: problem.py
from adder.problem import FAILURE
from adder.problem import SOLUTION_UNKNOWN
from itertools import count
from collections import defaultdict

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
    