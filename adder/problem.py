# Depends on: graphs.py

class InvalidArgumentError(Exception):
    pass

class _Node:
    def __init__(self, state, parent, action, path_cost):
        self.__state = state
        self.__parent = parent
        self.__action = action
        self.__path_cost = path_cost
        
    def __eq__(self, other):
        return self.state == other.state and \
               self.action == other.action
        
    def __ne__(self, other):
        return not self == other
        
    def __hash__(self):
        return hash(self.state)
        
    def __str__(self):
        parent_name = self.parent.state if self.parent else "None"
        return self.state
        return "(State: {0}, Parent: {1}, Action: {2})".format(self.state, parent_name, self.action)
        
    def __repr__(self):
        return str(self)
        
    @property
    def state(self): return self.__state
    @property
    def parent(self): return self.__parent
    @property
    def action(self): return self.__action
    @property
    def path_cost(self): return self.__path_cost

FAILURE = "FAILURE"
SOLUTION_UNKNOWN = "SOLUTION_UNKNOWN"

class _Problem:    
    def child_node(self, node, action):
        parent = node
        state = self.result(node.state, action)
        action = action
        path_cost = node.path_cost + self.step_cost(node.state, action)
        
        child = _Node(state, parent, action, path_cost)
        return child
        
    def actions_iter(self, state):
        raise NotImplementedError("_Problem is abc")
        
    def step_cost(state, action):
        raise NotImplementedError("_Problem is abc")
        
    def result(self, state, action):
        raise NotImplementedError("_Problem is abc")
        
    def goal_test(self, state):
        raise NotImplementedError("_Problem is abc")
        
    def construct_solution(self, end_node):
        path = []
        while end_node != self.initial:
            parent = end_node.parent
            if parent.state in [node for node, action in path]:
                return FAILURE
                
            path.append((end_node.state, end_node.action))           
            end_node = parent
        path.append((self.initial.state, None))
        path.reverse()
        return path
        
        
    def solution_cost(self, solution):
        if solution is FAILURE or solution is SOLUTION_UNKNOWN:
            return 0
            
        cost = 0
        previous_state = None
        for state, action in solution:
            cost += self.step_cost(previous_state, action) if previous_state else 0
            previous_state = state
        return cost
        

class _GraphProblem(_Problem):
    def __init__(self, graph, root, goal):
        if root not in graph.get_nodes():
            raise InvalidArgumentError("root must be be a node in the graph")
        if goal not in graph.get_nodes():
            raise InvalidArgumentError("goal must be be a node in the graph")
            
        self.graph = graph
        self.initial = _Node(root, None, None, 0)
        self.goal = goal
        
    def actions_iter(self, state):
        return self.graph.children_iter(state)
        
    def step_cost(self, state, action):
        return self.graph.edge_cost(state, action)
        
    def result(self, state, action):
        return action if action in self.graph.children_iter(state) else None                      
        
    def goal_test(self, state):
        return state == self.goal

        
class ProblemFactory:
    def from_graph(self, graph, root, goal):
        return _GraphProblem(graph, root, goal)        