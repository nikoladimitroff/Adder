# Depends on: problem.py

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
                
    return problem.FAILURE