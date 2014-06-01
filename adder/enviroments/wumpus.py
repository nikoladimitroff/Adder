from itertools import product
import random

class _WumpusWorldAxiomatizer:
    FACTS = [ 
        "!P11",
        "!W11",
        "L11_0",
        "WumpusAlive_0",
        "FaceEast_0",
        "HaveArrow_0",
    ]

    def __init__(self, size):
        self.size = size

    def __wumpus_world(self):
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

    def __breeze_stench(self, row, col):
        pit_disjuncts = " | ".join(["P{0}{1}".format(row_neighb, col_neighb) for
                                    row_neighb, col_neighb in self.__neighbours(row, col)])
        breeze_axiom = "B{0}{1} <=> ({2})".format(row, col, pit_disjuncts)
        
        wumpus_disjuncts = " | ".join(["W{0}{1}".format(row_neighb, col_neighb) for
                                    row_neighb, col_neighb in self.__neighbours(row, col)])
                                    
        stench_axiom = "S{0}{1} <=> ({2})".format(row, col, wumpus_disjuncts)
        
        return breeze_axiom, stench_axiom
        
    def __wumpus_axioms(self):
        wumpus_existence = " | ".join(["W{0}{1}".format(row, col) for row, col in
                                       self.__wumpus_world()])
       
        wumpus_symbols = []
        for row1, col1 in self.__wumpus_world():
            for row2, col2 in self.__wumpus_world():
                if (row1, col1) >= (row2, col2):
                    continue
                wumpus_symbols.append("(!W{0}{1} | !W{2}{3})"
                                      .format(row1, col1, row2, col2))
                
        wumpus_unique = " & ".join(wumpus_symbols)
        
        return wumpus_existence, wumpus_unique
        
    def __percepts(self, time):
        percept_axioms = []
        for row, col in self.__wumpus_world():
            breeze = "L{0}{1}_{2} => (Breeze_{2} <=> B{0}{1})".format(row, col, time)
            stench = "L{0}{1}_{2} => (Stench_{2} <=> S{0}{1})".format(row, col, time)
            percept_axioms += breeze, stench
        return percept_axioms
        
    def __successor_state_axioms(self, time):
        axioms = []
        arrow = "HaveArrow_{0} <=> (HaveArrow_{1} & !Shoot_{1})".format(time + 1, time)
        axioms.append(arrow)
            
        wumpus = "WumpusAlive_{0} <=> (WumpusAlive_{1} & !Scream_{1})".format(time + 1, time)
        axioms.append(wumpus)
        
        east = "FacingEast_{0} <=> (FacingSouth_{1} & Turn_{1})".format(time + 1, time)
        north = "FacingNorth_{0} <=> (FacingEast_{1} & Turn_{1})".format(time + 1, time)
        west = "FacingWest_{0} <=> (FacingNorth_{1} & Turn_{1})".format(time + 1, time)
        south = "FacingSouth_{0} <=> (FacingWest_{1} & Turn_{1})".format(time + 1, time)
        axioms += east, north, west, south
        
            
        location_pattern = "| (L{0}{1}_{2} & ({3} & Forward_{2}))"
        for row, col in self.__wumpus_world():
            location = "L{0}{1}_{2} <=> " \
                        "(L{0}{1}_{3} & (!Forward_{3} | Bump_{2}))" \
                        .format(row, col, time + 1, time)
                
            if row > 1:
                location += location_pattern.format(row - 1, col, time, "South_{0}".format(time))
            if row < self.size:
                location += location_pattern.format(row + 1, col, time, "North_{0}".format(time))
            if col > 1:
                location += location_pattern.format(row, col - 1, time, "West_{0}".format(time))
            if col < self.size:
                location += location_pattern.format(row, col + 1, time, "East_{0}".format(time))
            axioms.append(location)
                
        return axioms

    def generate_atemportal(self):
        for i, j in self.__wumpus_world():
            kb += self.__breeze_stench(i, j)
            
        kb += self.__wumpus_axioms()

    def generate_temporal(self, time):
        return self.__percepts(time) + self.__successor_state_axioms(time)


class WumpusCell:
    Empty = "E"
    Pit = "P"
    Wumpus = "W"
    Gold = "G"

class Orientation:
    South = 0
    East = 1
    North = 2
    West = 3

class Actions:
    Forward = 0
    Shoot = 1
    Turn = 2
    Grab = 3
    Climb = 4

class WumpusWorld:
    def __init__(self, size, grid=None):
        self.size = size
        if not grid:
            grid = self.__generate_world()
        self.grid = grid

        for i in range(size):
            for j in range(size):
                if self.grid[i][j] == WumpusCell.Wumpus:
                    self.wumpus = (i, j)
                    break

        if not self.wumpus:
            raise RuntimeError("There's is no wumpus in the world")


        hero = Object()
        hero.position = (1, 1)
        hero.orientation = Orientation.South
        hero.has_arrow = True
        self.gold_taken = False
        self.wumpus_alive = True

        
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

    def __generate_world():
        grid = [
            [WumpusCell.Empty, WumpusCell.Empty, WumpusCell.Wumpus, WumpusCell.Empty],
            [WumpusCell.Empty, WumpusCell.Empty, WumpusCell.Gold, WumpusCell.Empty],
            [WumpusCell.Pit, WumpusCell.Empty, WumpusCell.Pit, WumpusCell.Empty],
            [WumpusCell.Empty, WumpusCell.Empty, WumpusCell.Empty, WumpusCell.Pit]
        ]

        return grid

    def __out_of_bounds(self, position):
        return position[0] < 1 or \
               position[0] >= self.size or \
               position[1] < 1 or \
               position[1] >= self.size

    def __get_movement_vector(self):
        if self.hero.orientation == Orientation.East:
            return (0, 1)
        if self.hero.orientation == Orientation.North:
            return (-1, 0)
        if self.hero.orientation == Orientation.West:
            return (0, -1)
        if self.hero.orientation == Orientation.South:
            return (1, 0)

    def __try_move_forward(self):      
        movement = self.__get_movement_vector()
        hero = self.hero
        hero.position[0] += movement[0]
        hero.position[1] += movement[1]
        if self.__out_of_bounds(hero.position):
            hero.position[0] -= movement[0]
            hero.position[1] -= movement[1]
            return False

        return True

    def __try_kill(self):
        hero = self.hero

        if not hero.has_arrow:
            return False
        hero.has_arrow = False

        movement = self.__get_movement_vector()
        arrow_position = tuple(hero.position)
        while not self.__out_of_bounds(arrow_position):
            arrow_position[0] += movement[0]
            arrow_position[1] += movement[1]
            if arrow_position == self.wumpus:
                self.wumpus_alive = False
                return True

        return False

    def update(self, action):
        neighbours = self.__neighbours(self.player.position)
        breeze = len([cell == WumpusCell.Pit for cell in neighbours]) != 0
        stench = len([cell == WumpusCell.Wumpus for cell in neighbours]) != 0
        glitter = self.grid[self.hero.position[0] - 1][self.hero.position[1] - 1]
        bump = False
        scream = False

        hero = self.hero
        if action == Actions.Forward:
            bump = not self.__try_move_forward()
        if action == Actions.Turn:
            hero.orientation = (hero.orientation + 1) % 4
        if action == Actions.Shoot:
            scream = self.__try_kill()
        if action == Actions.Grab:
            if glitter:
                self.gold_taken = True
        if action == Actions.Climb:
            pass

        return (breeze, stench, glitter, bump, scream)


class HybridWumpusAgent:
    def __init__(self, size):
        self.axiomatier = _WumpusWorldAxiomatizer(size)
        self.kb = self.axiomatier.generate_atemportal()
