from functools import partial

from adder import problem, logic
from adder.logic import Braces, LogicOperator, DefiniteClause, \
                        standardize_variables, skolemize, \
                        unify, substitute
from adder.utils import ParsingError

def backward_chaining(kb, query):
    query = standardize_variables(query)
    return __backward_chaining_or(kb, query, {})

def __backward_chaining_or(kb, query, theta):
    print("ORING", query, theta)
    for implication in __fetch_implications(kb, query):
        premises, conclusion = implication.premises, implication.conclusion
        subst = __backward_chaining_and(kb, premises, unify(query, conclusion, theta))
        yield from subst


def __fetch_implications(kb, query):
    implications = []
    for implication in kb:
        if query[0] == "S":
            print("FING", query, implication.conclusion, unify(query, implication.conclusion))
        subst = unify(query, implication.conclusion)
        if subst != problem.FAILURE:
            implications.append(implication)

    print("fetched", query, implications)
    return implications

def __backward_chaining_and(kb, goals, theta):
    print("ANDING", goals, theta)
    if theta is problem.FAILURE:
        yield problem.FAILURE
        return
    if len(goals) == 0:
        yield theta
        return
    if len(goals) == 1:
        yield from __backward_chaining_or(kb, substitute(goals[0], theta), theta)

    first, rest = goals[0], goals[1:]
    for subst1 in __backward_chaining_or(kb, substitute(first, theta), theta):
        for subst2 in __backward_chaining_and(kb, rest, subst1):
            yield subst2

DefiniteKnowledgeBase = partial(logic.DefiniteKnowledgeBase, backward_chaining)


