from adder import proplogic
from adder import search
from adder import problem

from time import sleep

def main():
    # Definite Knowledge Base
    #definite_kb = proplogic.DefiniteKnowledgeBase("""
    #    Vreme_Za_Piton & Ne_E_Praznik & Stefan => Stefan_V_Zalata
    #    Stefan_V_Zalata => Stefan_Kazva_Taka
    #    Stefan_Kazva_Taka => Kiro_Ot_Pernik
    #    Kiro_Ot_Pernik => Kiro_Kara_Golf
    #""")

    #definite_kb.tell("Vreme_Za_Piton")
    #definite_kb.tell("Ne_E_Praznik")
    #definite_kb.tell("Stefan")
    #print(definite_kb.ask("Kiro_Kara_Golf"))

    ## PL Knowledge Base
    #pl_kb = proplogic.PlKnowledgeBase("""
    #    Ucha_FMI <=> (Matematik | Programist)
    #    Matematik <=> (Znam_DIS & !Znam_Asembler)
    #    Programist <=> (Znam_Python & Znam_C)
    #""")

    #pl_kb.tell("Znam_Python")
    #pl_kb.tell("Znam_C")

    #print(pl_kb.ask("Ucha_FMI"))
    
    ## Simulated annealing
    height = 8
    landscape = [2, 3, 4, 3, 2, 3, 5, 6, 5, 4, 5, 4, 3, 2, 3, 4, 5, 6, 7, 6, 5, 4]
    width = len(landscape)
    state = 0
    def actions(state):
        actions = []
        if state > 0: actions.append(-1)
        if state < len(landscape) - 1: actions.append(1)
        return actions

    
    def print_landscape(state):
        for row_index in range(height):
            row = [' ' if landscape[i] > row_index else 
                                                    ('|' if landscape[i] < row_index else ('Y' if i == state else 'T')) 
                   for i in range(width)]
            print("".join(row))

        sleep(1)

    result = lambda state, action: state + action
    step_cost = lambda state, action: 1

    heuristic = lambda state: (height - landscape[state] - 1) / (height - 1)
    goal_state = lambda state: heuristic(state) == 0

    factory = problem.ProblemFactory()
    pr = factory.from_functions(state, actions, step_cost, result, goal_state)

    solution = search.simulated_annealing(pr, heuristic, local_minima_acceptable=True, print_state=print_landscape)

    # NPuzzle
    
    #initial, goal = ("4 2 5 3 6 8 1 7 0", "0 1 2 3 4 5 6 7 8")
    #factory = problem.ProblemFactory()
    #problem_instance = factory.from_npuzzle(initial, goal)
    #heuristic = factory.heuristic_for(problem_instance)

    
    #def print_state(state):
    #    size = int(len(state) ** 0.5)
    #    for row in range(size):
    #        print(state[row * size : (row + 1) * size])

    #    print()
    #    sleep(1)

    #solution = search.astar(problem_instance, heuristic, print_state=print_state)


if __name__ == "__main__":
    main()
