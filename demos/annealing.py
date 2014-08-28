from time import sleep

from adder import problem, search


def main():
    height = 8
    landscape = [2, 3, 4, 3, 2, 3, 5, 6, 5, 4, 5,
                 4, 3, 2, 3, 4, 5, 6, 7, 6, 5, 4]
    width = len(landscape)
    state = 0

    def actions(state):
        actions = []
        if state > 0:
            actions.append(-1)
        if state < len(landscape) - 1:
            actions.append(1)
        return actions

    def print_landscape(state):
        for row_index in range(height):
            row = [' ' if landscape[i] > row_index else
                   ('|' if landscape[i] < row_index
                    else ('Y' if i == state else 'T'))
                   for i in range(width)]
            print("".join(row))

        sleep(0.4)

    result = lambda state, action: state + action
    step_cost = lambda state, action: 1

    heuristic = lambda state: (height - landscape[state] - 1) / (height - 1)
    goal_state = lambda state: heuristic(state) == 0

    factory = problem.ProblemFactory()
    pr = factory.from_functions(state, actions, step_cost, result, goal_state)

    solution = search.simulated_annealing(pr, heuristic,
                                          local_minima_acceptable=True,
                                          min_temperature=0.1,
                                          print_state=print_landscape)
    print("Done")

main()
