from itertools import product
from collections import namedtuple
import random
from adder import proplogic
from adder.proplogic import KnowledgeBase
from adder.problem import Problem
from adder.problem import Node
from adder.search import astar

class _Axiomatizer:
    FACTS = [ 
        "!P11",
        "L11_0",
        "FacingEast_0",
    ]

    def __init__(self, size):
        self.size = size

    def wumpus_world(self):
        return product(range(1, self.size + 1), range(1, self.size + 1))
 
    def __neighbours(self, row, col):
        neighbours = []
        if row > 1:
            neighbours.append((row - 1, col))
        if row < self.size:
            neighbours.append((row + 1, col))
        if col > 1:
            neighbours.append((row, col - 1))
        if col < self.size:
            neighbours.append((row, col + 1))
            
        return neighbours

    def __breeze(self, row, col):
        pit_disjuncts = " | ".join(["P{0}{1}".format(row_neighb, col_neighb) for
                                    row_neighb, col_neighb in self.__neighbours(row, col)])
        breeze_axiom = "B{0}{1} <=> ({2})".format(row, col, pit_disjuncts)
        
        return breeze_axiom

        
    def __percepts(self, time, position):
        row, col = position
        breeze = "L{0}{1}_{2} => (Breeze_{2} <=> B{0}{1})".format(row, col, time)
        return [breeze]
        
    def __successor_state_axioms(self, time, position):
        axioms = []

        east = "FacingEast_{0} <=> ((FacingSouth_{1} & Turn_{1}) | (FacingEast_{1} & !Turn_{1}))".format(time + 1, time)
        north = "FacingNorth_{0} <=> ((FacingEast_{1} & Turn_{1}) | (FacingNorth_{1} & !Turn_{1}))".format(time + 1, time)
        west = "FacingWest_{0} <=> ((FacingNorth_{1} & Turn_{1}) | (FacingWest_{1} & !Turn_{1}))".format(time + 1, time)
        south = "FacingSouth_{0} <=> ((FacingWest_{1} & Turn_{1}) | (FacingSouth_{1} & !Turn_{1}))".format(time + 1, time)
        axioms += east, north, west, south
        
        row, col = position    
        location_pattern = " | (L{0}{1}_{2} & ({3} & Forward_{2})))"
        location = "L{0}{1}_{2} <=> " \
                    "((L{0}{1}_{3} & !Forward_{3})" \
                    .format(row, col, time + 1, time)
                
        if row > 1:
            location += location_pattern.format(row - 1, col, time, "FacingSouth_{0}".format(time))
        if row < self.size:
            location += location_pattern.format(row + 1, col, time, "FacingNorth_{0}".format(time))
        if col > 1:
            location += location_pattern.format(row, col - 1, time, "FacingWest_{0}".format(time))
        if col < self.size:
            location += location_pattern.format(row, col + 1, time, "FacingEast_{0}".format(time))
        #axioms.append(location)
                
        axioms.append("L{0}{1}_{2}".format(position[0], position[1], time))
        
        return axioms

    def __helper_axioms(self, time):
        if time > 0:
            ok_axioms = ["OK{0}{1}_{2} <=> (OK{0}{1}_{3} | !P{0}{1})"
                         .format(row, col, time, time - 1)
                         for row, col in self.wumpus_world()]
        else:
            ok_axioms = ["OK{0}{1}_{2} <=> !P{0}{1}"
                         .format(row, col, time)
                         for row, col in self.wumpus_world()]

        at_least_1_location = " | ".join("L{0}{1}_{2}".format(row, col, time) for row, col in self.wumpus_world())
        at_most_1_location = []
        for row1, col1 in self.wumpus_world():
            lhs = "L{0}{1}_{2}".format(row1, col1, time)
            rhs = " & ".join("!L{0}{1}_{2}".format(row2, col2, time) 
                             for row2, col2 in self.wumpus_world()
                             if row2 != row1 or col2 != col1)

            at_most_1_location.append("{0} <=> ({1})".format(lhs, rhs))


        ok_axioms.append(at_least_1_location)
        ok_axioms += at_most_1_location
        return ok_axioms

    def generate_atemportal(self):
        axioms = _Axiomatizer.FACTS[:]
        for i, j in self.wumpus_world():
            axioms.append(self.__breeze(i, j))

        return axioms

    def generate_temporal(self, time, position):
        return self.__percepts(time, position) + \
               self.__successor_state_axioms(time, position) + \
               self.__helper_axioms(time)


class Cell:
    Empty = "E"
    Pit = "P"
    Gold = "G"


class Orientation:
    South = 0
    East = 1
    North = 2
    West = 3

class Actions:
    Forward = "Forward_{0}"
    Turn = "Turn_{0}"
    Grab = "Grab_{0}"
    Climb = "Climb_{0}"

class World:
    def __init__(self, size, agent, grid=None):
        self.size = size
        if not grid:
            grid = self.__generate_world()
        self.grid = grid


        self.hero = agent
        self.hero.position = (1, 1)
        self.hero.orientation = Orientation.East
 
    @staticmethod
    def get_movement_vector(orientation):
        if orientation == Orientation.East:
            return (0, 1)
        if orientation == Orientation.North:
            return (-1, 0)
        if orientation == Orientation.West:
            return (0, -1)
        if orientation == Orientation.South:
            return (1, 0)        
           
    def __neighbours(self, row, col):
        row -= 1
        col -= 1
        neighbours = []
        if row > 0:
            neighbours.append(self.grid[row - 1][col])
        if row < self.size - 1:
            neighbours.append(self.grid[row + 1][col])
        if col > 0:
            neighbours.append(self.grid[row][col - 1])
        if col < self.size - 1:
            neighbours.append(self.grid[row][col + 1])
            
        return neighbours

    def __generate_world(self):
        if self.size == 4:
            grid = [
                [Cell.Empty, Cell.Empty, Cell.Pit, Cell.Empty],
                [Cell.Empty, Cell.Empty, Cell.Gold, Cell.Empty],
                [Cell.Pit, Cell.Empty, Cell.Pit, Cell.Empty],
                [Cell.Empty, Cell.Empty, Cell.Empty, Cell.Pit]
            ]
        elif self.size == 3:
            grid = [
                [Cell.Empty, Cell.Empty, Cell.Empty],
                [Cell.Gold, Cell.Empty, Cell.Empty],
                [Cell.Empty, Cell.Empty, Cell.Empty]
            ]
        elif self.size == 2:
            grid = [
                [Cell.Empty, Cell.Empty],
                [Cell.Gold, Cell.Empty]
            ]

        return grid

    def __out_of_bounds(self, position):
        return position[0] < 1 or \
               position[0] > self.size or \
               position[1] < 1 or \
               position[1] > self.size

    def sum_tuples(a, b, diff=False):
        return tuple(x + ((-1) ** diff) * y for x, y in zip(a,b))

    def __try_move_forward(self):
        hero = self.hero
        movement = World.get_movement_vector(hero.orientation)
        hero.position = World.sum_tuples(hero.position, movement)

        if self.__out_of_bounds(hero.position):
            hero.position = World.sum_tuples(hero.position, movement, diff=True)
            return False

        return True


    def update(self, action):
        neighbours = self.__neighbours(*self.hero.position)
        breeze = len([cell for cell in neighbours if cell == Cell.Pit]) != 0
        glitter = self.grid[self.hero.position[0] - 1][self.hero.position[1] - 1] == Cell.Gold

        hero = self.hero
        if action == Actions.Forward:
            self.__try_move_forward()
        if action == Actions.Turn:
            hero.orientation = (hero.orientation + 1) % 4
        if action == Actions.Grab:
            if glitter:
                self.gold_taken = True
        if action == Actions.Climb:
            pass

        return (breeze, glitter)


class PlanningProblem(Problem):
    def __init__(self, current_position, current_orientation, goal, safe_cells):
        self.goal = goal
        self.cells = safe_cells
        initial_state = (current_position, current_orientation)
        self.initial = Node(initial_state, None, None, 0) 

    def actions_iter(self, state):
        return [Actions.Forward, Actions.Turn]
        
    def step_cost(self, state, action):
        return 1
        
    def result(self, state, action):
        position, orientation = state
        if action == Actions.Forward:
            movement = World.get_movement_vector(orientation)
            new_position = (position[0] + movement[0], position[1] + movement[1])
            if new_position in self.cells:
                return (new_position, orientation)
            else:
                return state
        elif action == Actions.Turn:
            orientation = (orientation + 1) % 4
            return (position, orientation)

    def goal_test(self, state):
        return state[0] == self.goal

    def heuristic(self, state):
        # manhattan
        return abs(state[0][0] - self.goal[0]) + abs(state[0][1] - self.goal[1])


class HybridAgent:
    def __init__(self, size):
        self.axiomatizer = _Axiomatizer(size)
        self.kb = KnowledgeBase("\n".join(self.axiomatizer.generate_atemportal()), max_clause_len=3)
        self.time = -1
        self.plan = []
        self.position = (1, 1)

    def __make_percept_sentence(self, percept):
        percepts_at_time = [sentence.format(self.time) for sentence in
                            ["Breeze_{0}", "Glitter_{0}"]]

        for i in range(len(percept)):
            if not percept[i]:
                percepts_at_time[i] = "!" + percepts_at_time[i]

        percept_sentence = " & ".join(percepts_at_time)

        return percept_sentence

    def __make_action_sentence(self, action):
        return action.format(self.time)

    def update(self, percept):
        self.time += 1
        percept_sentence = self.__make_percept_sentence(percept)
        self.kb.tell(percept_sentence)
        self.kb.tell(*self.axiomatizer.generate_temporal(self.time, self.position))

        safe_cells = [(row, col) for row, col in self.axiomatizer.wumpus_world()
                      if self.kb.ask("OK{0}{1}_{2}".format(row, col, self.time))]

        print(safe_cells)
        if self.kb.ask("Glitter_{0}".format(self.time)):
            self.plan = [Actions.Grab] + self.plan_route_to((1, 1), safe_cells) \
                         + [Actions.Climb]
        
        if len(self.plan) == 0:
            unvisited = set()
            for row, col in self.axiomatizer.wumpus_world():
                is_visited = False
                for time in range(self.time + 1):
                    if self.kb.ask("L{0}{1}_{2}".format(row, col, time)):
                        is_visited = True
                        break
                if not is_visited: 
                    unvisited.add((row, col))



            #for row, col in self.axiomatizer.wumpus_world():
            #    for time in range(self.time + 1):
            #        symbol = "L{0}{1}_{2}".format(row, col, time)
            #        print(symbol, self.kb.ask(symbol), "!" + symbol, self.kb.ask("!" + symbol))

            unvisited_and_safe = unvisited.intersection(safe_cells)
            target = unvisited_and_safe.pop()
            self.plan = [action for next_state, action in 
                         self.plan_route_to(target, safe_cells)]
            self.plan.pop(0)

        action = self.plan.pop(0)
        self.kb.tell(self.__make_action_sentence(action))

        return action

    def plan_route_to(self, goal, cells):
        current_position = (-1, -1)
        for row, col in self.axiomatizer.wumpus_world():
            if self.kb.ask("L{0}{1}_{2}".format(row, col, self.time)):
                self.position = row, col
                break
        
        orientation = Orientation.South
        if self.kb.ask("FacingEast_{0}".format(self.time)):
            orientation = Orientation.East
        elif self.kb.ask("FacingNorth_{0}".format(self.time)):
            orientation = Orientation.North
        elif self.kb.ask("FacingWest_{0}".format(self.time)):
            orientation = Orientation.West

        problem = PlanningProblem(self.position, orientation, goal, cells)
        return astar(problem, problem.heuristic)
