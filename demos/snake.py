import sys

import random
import time

from adder.search import astar
from adder.problem import Problem, FAILURE, Node


def sum_coords(a, b):
    return (a[0] + b[0], a[1] + b[1])


class RouteProblem(Problem):
    def __init__(self, coords, board_size, obstacles, snake, goal):
        self.initial = Node((coords, 0, tuple()), None, None, 0)
        self.board_size = board_size
        self.goal = goal
        self.obstacles = obstacles
        self.snake = snake

    def actions_iter(self, state):
        actions = []
        obstacles = self.obstacles
        coords = state[0]
        time = state[1]
        path = state[2]

        if coords[0] > 0:
            actions.append((-1, 0))
        if coords[0] < self.board_size - 1:
            actions.append((1, 0))
        if coords[1] > 0:
            actions.append((0, -1))
        if coords[1] < self.board_size - 1:
            actions.append((0, 1))

        applicable = []
        snake_len = len(self.snake)
        for action in actions:
            result = sum_coords(coords, action)
            if result not in obstacles and \
               result not in self.snake[0:snake_len - time - 1] and \
               result not in path[0:snake_len]:
                applicable.append(action)

        return iter(applicable)


    def step_cost(self, state, action):
        return 1

    def result(self, state, action):
        coords = sum_coords(state[0], action)
        time = state[1] + 1
        path = state[2]
        if len(path) == len(self.snake):
            path = path[:1] + (state[0], )
        else:
            path = path + (state[0], )
        return  (coords, time, path)
        
    def goal_test(self, state):
        coords = state[0]
        return coords[0] == self.goal[0] and coords[1] == self.goal[1]
    
    def heuristic(self, state):
        # manhattan
        coords = state[0]
        return abs(coords[0] - self.goal[0]) + abs(coords[1] - self.goal[1])


class Snake:
    def __init__(self, board_size, obstacles):
        self.body = [(4, 0), (3, 0), (2, 0), (1, 0)]
        self.plan = []
        self.size = board_size
        self.obstacles = obstacles
        self.__randomize_fruit()


    def __randomize_fruit(self):
        self.fruit = (random.randint(0, self.size - 1), 
                      random.randint(0, self.size - 1))
        if self.fruit in self.obstacles or self.fruit in self.body:
            self.__randomize_fruit()


    def try_step(self):
        if len(self.plan) == 0:
            problem = RouteProblem(self.body[0], self.size, 
                                   self.obstacles, self.body, 
                                   self.fruit)
            self.plan = astar(problem, problem.heuristic)
            if self.plan == FAILURE:
                print("No solution from the current position")
                return False
            self.plan.pop(0)

        next_state, action = self.plan.pop(0)
        print(next_state)
        
        tail = self.body[-1] + tuple()

        for i in range(len(self.body) - 1, 0, -1):
            self.body[i] = self.body[i - 1]

        self.body[0] = sum_coords(self.body[0], action)

        if self.body[0] == self.fruit:
            self.body.append(tail)
            self.__randomize_fruit()

        return True

    def draw(self):
        buffer = ["\b" for i in range(self.size * (self.size + 1))]
        #buffer = []
        for row in range(self.size):
            for col in range(self.size):
                if (row, col) in self.body:
                    if (row, col) == self.body[0]:
                        buffer.append("^")
                    else:
                        buffer.append("*")
                elif (row, col) in self.obstacles:
                    buffer.append("#")
                elif (row, col) == self.fruit:
                    buffer.append("@")
                else:
                    buffer.append("-")
            buffer.append("\n")

        print("".join(buffer))


SIZE = 8
OBSTACLE_COUNT = 0
def main():
    args = sys.argv[2:]
    size = int(args[0]) if len(args) > 0 else SIZE
    obstacles_count = int(args[1]) if len(args) > 1 else OBSTACLE_COUNT

    obstacles = [(random.randint(0, size - 1), random.randint(0, size - 1)) 
                 for i in range(obstacles_count)]
    snake = Snake(size, obstacles)
    
    snake.fruit = (size - 1, size - 1)
    while snake.try_step():
        snake.draw()
        time.sleep(0.2)

main()


