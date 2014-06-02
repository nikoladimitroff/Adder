from itertools import count
from collections import defaultdict
import random
import math
from time import sleep

from adder.problem import FAILURE
from adder.problem import SOLUTION_UNKNOWN

# <uninformed searches>

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
                
    return FAILURE


def depth_limited_search(problem, max_depth):
    return __recursive_dls(problem, problem.initial, {problem.initial}, max_depth)


def __recursive_dls(problem, node, visited, max_depth):
    if problem.goal_test(node.state):
        return problem.construct_solution(node)

    if max_depth == 0:
        return SOLUTION_UNKNOWN
    
    unknown_occured = False
    for action in problem.actions_iter(node.state):
        child = problem.child_node(node, action)
        if child not in visited:
            visited.add(child)
            child_dls = __recursive_dls(problem, child, set(visited), max_depth - 1)
            if child_dls is SOLUTION_UNKNOWN:
                unknown_occured = True
            elif child_dls is not FAILURE:
                return child_dls   
            
    return SOLUTION_UNKNOWN if unknown_occured else FAILURE


def dfs(problem):
    return depth_limited_search(problem, float("inf"))


def iterative_deepening_dfs(problem, max_depth=float("inf")):
    for depth in count():
        result = depth_limited_search(problem, depth)
        if result is not SOLUTION_UNKNOWN:
            return result
        if depth >= max_depth:
            return SOLUTION_UNKNOWN
            
# </uninformed searches>

def __astar_key_comparer(pair):
    return pair[0]


def astar(problem, heuristic, print_state=lambda state: None):
    visited = set()
    node = problem.initial
    frontier = [node]
    
    f_values = { node: heuristic(node.state)}
    g_values = { node: 0 }
    nodes_generated = 0
    while len(frontier) != 0:
        # Expand the node with lowest f_value
        frontier_f_scores = [(f_values[expanded], index) 
                             for index, expanded in enumerate(frontier)]
        node_index = min(frontier_f_scores, key=__astar_key_comparer)[1]
 
        node = frontier.pop(node_index)     
        print_state(node.state)
        visited.add(node)
        
        if problem.goal_test(node.state):
            return problem.construct_solution(node)
        
        for action in problem.actions_iter(node.state):
            child = problem.child_node(node, action)
            if child in visited: continue
            
            new_g_value = g_values[node] + problem.step_cost(node.state, action)
            child_index = -1
            for i, element in enumerate(frontier):
                if element == child:
                    child_index = i

            child_in_frontier = child_index != -1
            needs_update = child_in_frontier and new_g_value < g_values[child]
                
            if needs_update:
                # Update the node so that it has proper parent, action and cost
                frontier[child_index] = child
                
            if child not in frontier:
                frontier.append(child)
            
            if not child_in_frontier or needs_update:
                g_values[child] = new_g_value
                f_values[child] = new_g_value + heuristic(child.state)
    return FAILURE


def hill_climbing(problem, heuristic, max_sideways_walk, local_minima_acceptable=False):
    node = problem.initial
    current_cost = float("inf")
    sideway_moves = 0
    while True:
        if problem.goal_test(node.state):
            return problem.construct_solution(node)

        heuristic_transform = lambda action: heuristic(problem.result(node.state, action))
        best_action = min(problem.actions_iter(node.state), key=heuristic_transform)
        cost = heuristic_transform(best_action)
        
        if cost > current_cost:
            return problem.construct_solution(node) if local_minima_acceptable else FAILURE
        elif cost == current_cost:
            if sideway_moves >= max_sideways_walk:
                return problem.construct_solution(node) if local_minima_acceptable else FAILURE
            sideway_moves += 1
        else:
            sideway_moves = 0

        node = problem.child_node(node, best_action)
        current_cost = cost


def random_restart_hc(problem_generator, heuristic, max_sideways_walk, max_iterations=1<<31):
    for _ in range(max_iterations):
        solution = hill_climbing(problem_generator(), heuristic, max_sideways_walk)
        if solution != FAILURE:
            return solution

    return FAILURE


def simulated_annealing(problem, heuristic, 
                        local_minima_acceptable=False, 
                        temperature_func=lambda t: math.log(1 / t), 
                        min_temperature=0.01,
                        print_state=lambda state: None):
    """
    Solves the problem using Simulated Annealing. The method is highly dependent on the right parameters. For best results, obey the following:
    - the temperature_func must be monothonic and slowly decreasing. The time argument will be in the range [0, 1]
    """


    node = problem.initial
    current_cost = heuristic(node.state)
    max_time = 1000
    for time in range(1, max_time):
        print_state(node.state)
        if problem.goal_test(node.state):
            return problem.construct_solution(node)

        temperature = temperature_func(time / max_time) / temperature_func(1 / max_time)
        action = random.choice(list(problem.actions_iter(node.state)))
        child = problem.child_node(node, action)
        child_cost = heuristic(child.state)
        delta_cost = current_cost - child_cost

        chance = math.exp(delta_cost / temperature)
        node = child if chance >= random.random() else node

        if abs(temperature) <= min_temperature:
            break

        current_cost = heuristic(node.state)

    return problem.construct_solution(node) if local_minima_acceptable else FAILURE


_MUTATION_CHANCE = 0.1
def genetic(state_generator, 
            fitness_func, 
            best_fitness_value,
            reproducer, 
            mutator, 
            population_size, 
            max_generations=1<<31):
    """
    Finds a state whose fitness value is at least best_fitness_value.
    Alternatively, finds the best state after max_generations.

    Args: 
        state_generator: a function generating random states
        fitness_func: a function computing the fitness value of a state. MUST BE NONNEGATIVE!
        best_fitness_value: the threshold for the best state
        reproducer: a function that combines two states given a separation point
        mutator: a function that sligthly changes the given state
        population_size: the size of the population
    """

    population = {}
    fitness_sum = 0
    for i in range(population_size):
        individual = state_generator()
        population[individual] = fitness_func(individual)
        fitness_sum += population[individual]
    
    for _ in range(max_generations):
        for individual in population:
            population[individual] = population[individual] / fitness_sum

        generation_fitness = {}
        generation_fitness_sum = 0
        for i in range(population_size):
            father = _weighted_choice(population)
            mother = _weighted_choice(population)
            
            for child in _reproduce(father, mother, reproducer):
                if random.random() <= _MUTATION_CHANCE:
                    child = mutator(child)
                if child in generation_fitness: continue
                generation_fitness[child] = fitness_func(child)
                if generation_fitness[child] >= best_fitness_value:
                    return child
                generation_fitness_sum += generation_fitness[child]

        population = generation_fitness
        fitness_sum = generation_fitness_sum

    return max(population, key=lambda key_value_pair: key_value_pair[1])[0]

def _weighted_choice(choices):
    r = random.uniform(0, 1)
    upto = 0
    for choice, weight in choices.items():
        if upto + weight > r:
            return choice
        upto += weight
    assert False, "No way to get here"


def _reproduce(father, mother, reproducer):
    crossover_point = random.randint(0, len(father) - 1)
    first_child = reproducer(father, mother, crossover_point) 
    second_child = reproducer(father, mother, len(father) - crossover_point)
    return (first_child, second_child)
