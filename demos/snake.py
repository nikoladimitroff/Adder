import sys

import random
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future

from adder.search import astar
from adder.problem import Problem, FAILURE, Node


def sum_coords(a, b):
    return (a[0] + b[0], a[1] + b[1])


class RouteProblem(Problem):
    def __init__(self, coords, board_size, obstacles, snake, goal):
        self.initial = Node((coords, 0, tuple()), None, None, 0)
        self.board_size = board_size
        self.obstacles = obstacles
        self.snake = snake
        self.goal = goal

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
               result not in self.snake[0:snake_len - time] and \
               result not in path:
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
        return (coords, time, path)

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
        self.size = board_size
        self.obstacles = obstacles

        self.fruit = self.__random_fruit()
        self.next_fruit = None
        self.plan = self.__generate_plan(self.body, self.fruit)

        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = self.executor.submit(self.__generate_future_plan)

    def __random_fruit(self, body=None):
        body = body if body else self.body

        fruit = (random.randint(0, self.size - 1),
                 random.randint(0, self.size - 1))
        while fruit in self.obstacles or fruit in body:
            fruit = (random.randint(0, self.size - 1),
                     random.randint(0, self.size - 1))
        return fruit

    def __generate_plan(self, body, fruit):
        problem = RouteProblem(body[0], self.size,
                               self.obstacles, body,
                               fruit)
        plan = astar(problem, problem.heuristic)
        if plan != FAILURE:
            plan.pop(0)

        return plan

    def __generate_future_plan(self):
        plan, next_body = self.plan[:], self.body[:]
        for state, action in plan[:-1]:
            self.execute_action(next_body, action)

        if len(plan) != 0:
            next_body.append(next_body[-1] + tuple())
            self.execute_action(next_body, plan[-1][1])

        next_fruit = self.__random_fruit(next_body)
        self.next_fruit = next_fruit
        next_plan = self.__generate_plan(next_body, next_fruit)

        return next_plan

    def execute_action(self, body, action):
        for i in range(len(body) - 1, 0, -1):
            body[i] = body[i - 1]

        body[0] = sum_coords(body[0], action)

    def try_step(self):
        if len(self.plan) == 0:
            self.plan = self.future.result()
            self.fruit = self.next_fruit
            self.future = self.executor.submit(self.__generate_future_plan)

            if self.plan == FAILURE:
                print("No solution from the current position")
                return False

        next_state, action = self.plan.pop(0)

        tail = self.body[-1] + tuple()
        self.execute_action(self.body, action)

        if self.body[0] == self.fruit:
            self.body.append(tail)
            if self.next_fruit and self.next_fruit != self.fruit:
                self.fruit = self.next_fruit
            else:
                self.fruit = (-1, -1)

        return True

    def draw(self):
        buffer = ["\b" for i in range(self.size * (self.size + 1))]
        for row in range(self.size):
            for col in range(self.size):
                if (row, col) == self.fruit:
                    buffer.append("@")
                elif (row, col) in self.body:
                    if (row, col) == self.body[0]:
                        buffer.append("^")
                    elif (row, col) == self.body[-1]:
                        buffer.append("&")
                    else:
                        buffer.append("*")
                elif (row, col) in self.obstacles:
                    buffer.append("#")
                else:
                    buffer.append("-")
            buffer.append("\n")

        print("".join(buffer))


def str_to_bool(string):
    return string.lower() in ("yes", "true", "t", "1")

SIZE = 8
OBSTACLE_COUNT = 0


def main():
    args = sys.argv[2:]
    size = int(args[0]) if len(args) > 0 else SIZE
    obstacles_count = int(args[1]) if len(args) > 1 else OBSTACLE_COUNT

    obstacles = [(random.randint(0, size - 1), random.randint(0, size - 1))
                 for i in range(obstacles_count)]
    snake = Snake(size, obstacles)

    while snake.try_step():
        snake.draw()
        time.sleep(0.4)

main()
