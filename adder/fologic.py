from functools import partial

from adder import problem, logic
from adder.logic import Braces, LogicOperator, DefiniteClause, \
                        standardize_variables, skolemize, \
                        unify, substitute, propagate_substitutions, \
                        find_all_variables
from adder.utils import ParsingError

def backward_chaining(kb, query):
    all_variables = find_all_variables(query)
    query, var_map = standardize_variables(query)
    result = __backward_chaining_or(kb, query, {})
    if result is not problem.FAILURE:
        propagate_substitutions(result)
        query_vars = {var: result[var_map[var]] for var in all_variables}
        return query_vars

    return result

def __backward_chaining_or(kb, query, theta):
    for implication in __fetch_implications(kb, query):
        premises, conclusion = implication.premises, implication.conclusion
        subst = __backward_chaining_and(kb, premises, unify(query, conclusion, theta))
        if subst is not problem.FAILURE:
            return subst
    return problem.FAILURE


def __fetch_implications(kb, query):
    implications = []
    for implication in kb:
        subst = unify(query, implication.conclusion)
        if subst != problem.FAILURE:
            implication.standardize()
            implications.append(implication)

    return implications

def __backward_chaining_and(kb, goals, theta):
    if theta is problem.FAILURE:
        return problem.FAILURE
    if len(goals) == 0:
        return theta

    subst = theta
    for goal in goals:
        subst = __backward_chaining_or(kb, substitute(goal, subst), subst)

    return subst

DefiniteKnowledgeBase = partial(logic.DefiniteKnowledgeBase, backward_chaining)
