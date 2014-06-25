from adder.search import astar
from adder.problem import Problem
from adder.problem import Node

import random
import time

def sum_coords(a, b):
    return (a[0] + b[0], a[1] + b[1])


class RouteProblem(Problem):
    def __init__(self, coords, board_size, obstacles, snake, goal):
        self.initial = Node(coords + (0, ), None, None, 0)
        self.board_size = board_size
        self.goal = goal
        self.obstacles = obstacles
        self.snake = snake

    def actions_iter(self, state):
        actions = []
        obstacles = self.obstacles
        coords = (state[0], state[1])
        time = state[2]

        if coords[0] > 0:
            actions.append((-1, 0))
        if coords[0] < self.board_size - 1:
            actions.append((1, 0))
        if coords[1] > 0:
            actions.append((0, -1))
        if coords[1] < self.board_size - 1:
            actions.append((0, 1))

        actions = [a for a in actions 
                   if sum_coords(coords, a) not in obstacles and \
                      sum_coords(coords, a) not in self.snake[0:time + len(self.snake) + 2]]

        return iter(actions)
         
        
    def step_cost(self, state, action):
        return 1
        
    def result(self, state, action):
        return (state[0] + action[0], state[1] + action[1], state[2] + 1)
        
    def goal_test(self, state):
        return state[0] == self.goal[0] and state[1] == self.goal[1]
    
    def heuristic(self, state):
        # manhattan
        return abs(state[0] - self.goal[0]) + abs(state[1] - self.goal[1])

class Snake:
    def __init__(self, board_size, obstacles):
        self.body = [(4, 0), (3, 0), (2, 0), (1, 0)]
        self.plan = []
        self.size = board_size
        self.obstacles = obstacles
        self.__randomize_fruit()


    def __randomize_fruit(self):
        self.fruit = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
        if self.fruit in self.obstacles or self.fruit in self.body:
            self.__randomize_fruit()


    def step(self):
        if len(self.plan) == 0:
            problem = RouteProblem(self.body[0], self.size, 
                                   self.obstacles, self.body, 
                                   self.fruit)
            self.plan = astar(problem, problem.heuristic)
            self.plan.pop(0)

        next_state, action = self.plan.pop(0)
        
        tail = self.body[-1] + tuple()

        for i in range(len(self.body) - 1, 0, -1):
            self.body[i] = self.body[i - 1]

        self.body[0] = sum_coords(self.body[0], action)

        if self.body[0] == self.fruit:
            self.body.append(tail)
            self.__randomize_fruit()

    def draw(self):
        buffer = ["\b" for i in range(self.size * (self.size + 1))]
        #buffer = []
        for row in range(self.size):
            for col in range(self.size):
                if (row, col) in self.body:
                    buffer.append("*")
                elif (row, col) in self.obstacles:
                    buffer.append("#")
                elif (row, col) == self.fruit:
                    buffer.append("@")
                else:
                    buffer.append("-")
            buffer.append("\n")

        print("".join(buffer))


ITERATIONS = 1000
SIZE = 8
OBSTACLE_COUNT = 0
def main():
    obstacles = [(random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)) 
                 for i in range(OBSTACLE_COUNT)]
    snake = Snake(SIZE, obstacles)
    
    snake.fruit = (0, 0)
    for i in range(ITERATIONS):
        snake.step()
        #print(snake.body, snake.fruit, [s for s, a in snake.plan], [a for s, a in snake.plan])
        snake.draw()
        time.sleep(0.5)

main()



