# Depends on: graphs.py

from functools import partial
import random

from adder.utils import InvalidArgumentError

class _Node:
    def __init__(self, state, parent, action, path_cost):
        self.__state = state
        self.__parent = parent
        self.__action = action
        self.__path_cost = path_cost
        
    def __eq__(self, other):
        return self.state == other.state
        
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

class Problem:
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
        

class _GraphProblem(Problem):
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


class _NPuzzleProblem(Problem):

    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

    def __init__(self, initial, goal):
        initial = initial if isinstance(initial, tuple) else tuple(initial.split())
        goal = goal if isinstance(goal, tuple) else tuple(goal.split())

        self.board_size = len(initial) ** 0.5
        if not self.board_size.is_integer():
            raise InvalidArgumentError("The size of the board must be a exact square!")

        self.board_size = int(self.board_size)
        self.initial = _Node(initial, None, None, 0)
        self.goal = goal
        
    def _swap_letters(self, state, first, second):
        next_state = list(state)
        next_state[first], next_state[second] = next_state[second], next_state[first]

        return tuple(next_state)

    def coords_of(self, state, number):
        number = str(number)

        index = state.index(number)

        # index = i * size + j
        j = index % self.board_size
        i = (index - j) / self.board_size
        return (i, int(j))
    
    def actions_iter(self, state):
        i, j = self.coords_of(state, 0)

        index = int(i * self.board_size + j)
        neighbours = []
        if i < self.board_size - 1:
            neighbours.append(_NPuzzleProblem.UP)
        if i > 0:
            neighbours.append(_NPuzzleProblem.DOWN)
        if j < self.board_size - 1:
            neighbours.append(_NPuzzleProblem.RIGHT)
        if j > 0:
            neighbours.append(_NPuzzleProblem.LEFT)

        return iter(neighbours)
            
        
    def step_cost(self, state, action):
        return 1
        
    def result(self, state, action):
        index = state.index("0")
        if action == _NPuzzleProblem.UP:
            return self._swap_letters(state, index, index + self.board_size)
        if action == _NPuzzleProblem.DOWN:
            return self._swap_letters(state, index, index - self.board_size)
        if action == _NPuzzleProblem.RIGHT:
            return self._swap_letters(state, index, index + 1)
        if action == _NPuzzleProblem.LEFT:
            return self._swap_letters(state, index, index - 1)
        
    def goal_test(self, state):
        return state == self.goal

    
class _NQueensProblem(Problem):
    def __init__(self, size, initial=None):
        self.size = size
        initial_state = initial if initial else _NQueensProblem.generate_random_state(size)
        self.initial = _Node(initial_state, None, None, 0)
        
    def generate_random_state(size):
        return tuple(random.randint(0, size) for i in range(size))

    def attacking(state):
        size = len(state)
        attacking = 0
        for col, row in enumerate(state):
            for other_col in range(col + 1, size):
                # Row
                if row == state[other_col]:
                    attacking += 1
                # Diag 1
                if row == state[other_col] + (col - other_col):
                    attacking += 1
                # Diag 2
                if row == state[other_col] - (col - other_col):
                    attacking += 1

        return attacking


    def actions_iter(self, state):
        for col in range(self.size):
            for row in range(self.size):
                if row == state[col]: continue
                yield (col, row)
            
        
    def step_cost(self, state, action):
        return 1
        
    def result(self, state, action):
        col_index, row_index = action
        next_state = list(state)
        next_state[col_index] = row_index

        return tuple(next_state)

    def goal_test(self, state):
        return _NQueensProblem.attacking(state) == 0

        
class ProblemFactory:
    def from_graph(self, graph, root, goal):
        return _GraphProblem(graph, root, goal)        

    def from_functions(self, initial_state, actions, step_cost, result, goal_test):
        problem = Problem()
        problem.initial = _Node(initial_state, None, None, 0)
        problem.actions_iter = actions
        problem.step_cost = step_cost
        problem.result = result
        problem.goal_test = goal_test

        return problem

    def from_npuzzle(self, initial, goal):
        return _NPuzzleProblem(initial, goal)

    def from_nqueens(self, size, initial=None):
        return _NQueensProblem(size, initial)

    
    def _manhattan_heuristic(problem_instance, state):
        scoords = [problem_instance.coords_of(state, num) for num in state]
        gcoords = [problem_instance.coords_of(state, num) for num in problem_instance.goal]
        diff = [abs(scoords[i][0] - gcoords[i][0]) + abs(scoords[i][1] - gcoords[i][1]) for i in range(0, len(state) - 1)]
        return sum(diff)

    def heuristic_for(self, problem):
        if isinstance(problem, _NPuzzleProblem):
            return partial(ProblemFactory._manhattan_heuristic, problem)
        elif isinstance(problem, _NQueensProblem):
            return _NQueensProblem.attacking
        else:
            raise TypeError("No heuristic exists for this type of problem")