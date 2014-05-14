# Depends on: problem.py
from adder.problem import FAILURE
from adder.problem import SOLUTION_UNKNOWN

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
    