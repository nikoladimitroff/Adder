from functools import partial
from collections import defaultdict
import re

from adder import problem, logic
from adder.logic import Braces, LogicOperator, DefiniteClause, \
                        standardize_variables, StandartizationReplacer,\
                        skolemize, unify, unify_substitutions, substitute, \
                        propagate_substitutions,\
                        find_variables_symbol, find_variables_expression,\
                        is_subsumed_by
from adder.utils import ParsingError
from adder.cnfparser import parse_fo_sentence as parse_cnf, \
                            is_fo_disjunction_tautology, print_cnf

def backward_chaining(kb, query):
    all_variables = find_variables_symbol(query)
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

    for goal in goals:
        theta = __backward_chaining_or(kb, substitute(goal, theta), theta)

    return theta


DefiniteKnowledgeBase = partial(logic.DefiniteKnowledgeBase, backward_chaining)


def is_subsumed_in(clause, clause_set):
    # 3 x Wut, wut for the functional solution
    return any(all(any(is_subsumed_by(clause_element, disjunct)
                       for clause_element in clause)
                   for disjunct in disjunction)
               for disjunction in clause_set)



def resolution_prover(knowledge_base, query, max_clause_len, information_rich):
    negated_query = "{0}({1})".format(LogicOperator.Negation, query)
    not_query_cnf = parse_cnf(negated_query)
    clauses = not_query_cnf + knowledge_base
    new_inferrences = set()
    already_resolved = set()
    clause_theta_mapping = defaultdict(list)

    clauses2 = parse_cnf(query) + knowledge_base
    new_inferrences2 = set()
    already_resolved2 = set()
    clause_theta_mapping2 = defaultdict(list)

    empty_set = frozenset()
    support = not_query_cnf
    support2 = parse_cnf(query)

    while True:
        result = __resolution_step(new_inferrences, already_resolved,
                                   clauses, max_clause_len,
                                   clause_theta_mapping)
        if result is not None:
            if result[0]:
                return {var: value for var, value in result[1][0].items()
                        if var in find_variables_expression(query)}

            return problem.FAILURE

        if information_rich:
            result = __resolution_step(new_inferrences2, already_resolved2,
                                       clauses2, max_clause_len,
                                       clause_theta_mapping2)
            if result is not None:
                return not result


def __resolution_step(new_inferrences, already_resolved,
                      clauses, max_clause_len,
                      clause_mapping, empty_set=frozenset()):
    new_inferrences.clear()
    pairs = ((clauses[i], clauses[j])
             for i in range(len(clauses))
             for j in range(i + 1, len(clauses))
             if (clauses[i], clauses[j]) not in already_resolved)

    for c1, c2 in pairs:
        resolvents = __resolve(c1, c2, max_clause_len, clause_mapping)
        if empty_set in resolvents:
            return True, list(map(propagate_substitutions, clause_mapping[empty_set]))

        new_inferrences.update(resolvents)
        already_resolved.add((c1, c2))

    #print("INFERRED", new_inferrences)
    if new_inferrences.issubset(clauses):
        return False, {}

    clauses.extend(clause for clause in new_inferrences
                   if not is_subsumed_in(clause, clauses))
   # print("CLAUSES", clauses)

    return None


def __resolve(c1, c2, max_len, clause_mapping):
    resolvents = []
    __resolve_single_sided(c1, c2, resolvents, clause_mapping)
    __resolve_single_sided(c2, c1, resolvents, clause_mapping)
    return [r for r in resolvents
            if len(r) < max_len and not is_fo_disjunction_tautology(r)]


def __resolve_single_sided(c1, c2, resolvents, clause_mapping):
    for symbol1 in c1:
        negation = LogicOperator.Negation + symbol1
        for symbol2 in c2:
            if len(clause_mapping[c1]) == 0: clause_mapping[c1].append({})
            if len(clause_mapping[c2]) == 0: clause_mapping[c2].append({})
            for th1 in clause_mapping[c1]:
                for th2 in clause_mapping[c2]:
                    th = unify_substitutions(th1, th2)
                    theta = unify(negation, symbol2, th)
                    if theta is not problem.FAILURE:
                        result = c1.union(c2).difference({symbol1, symbol2})
                        resolvent = __standardize_resolvent(result, theta)
                        resolvents.append(resolvent)
                        clause_mapping[resolvent].append(theta)


def __standardize_resolvent(resolvent, theta):
    replacer = StandartizationReplacer("x")
    result = set()
    for index, disjunct in enumerate(resolvent):
        # Do we need standartization? No, we don't
        result.add(substitute(disjunct, theta))

    StandartizationReplacer.GlobalIndex = replacer.index
    resolvent = frozenset(result)
    return resolvent

def __parser(sentence):
    return parse_cnf(standardize_variables(sentence)[0])

KnowledgeBase = partial(logic.KnowledgeBase, __parser, resolution_prover)
