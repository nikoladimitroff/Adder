from functools import partial
from collections import defaultdict
import re

from adder import problem, logic
from adder.logic import Braces, LogicOperator, DefiniteClause, \
                        standardize_variables, StandartizationReplacer,\
                        skolemize, unify, unify_substitutions, substitute, \
                        propagate_substitutions,\
                        find_all_variables, is_subsumed_by
from adder.utils import ParsingError
from adder.cnfparser import parse_fo_sentence as parse_cnf, \
                            is_fo_disjunction_tautology, print_cnf

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


CLAUSE_MAPPING = defaultdict(list)

def resolution_prover(knowledge_base, query, max_clause_len, information_rich):
    CLAUSE_MAPPING.clear()
    negated_query = "{0}({1})".format(LogicOperator.Negation, query)
    not_query_cnf = parse_cnf(negated_query)
    clauses = not_query_cnf + knowledge_base
    new_inferrences = set()
    already_resolved = set()

    clauses2 = parse_cnf(query) + knowledge_base
    new_inferrences2 = set()
    already_resolved2 = set()

    empty_set = frozenset()
    support = not_query_cnf
    support2 = parse_cnf(query)

    while True:
        result = __resolution_step(new_inferrences, already_resolved,
                                   support, clauses, max_clause_len)
        if result is not None:
            return result

        if information_rich:
            result = __resolution_step(new_inferrences2, already_resolved2,
                                       support2, clauses2, max_clause_len)
            if result is not None:
                return not result


def __resolution_step(new_inferrences, already_resolved,
                      support_set, clauses,
                      max_clause_len, empty_set=frozenset()):
    new_inferrences.clear()
    pairs = ((clauses[i], clauses[j])
             for i in range(len(clauses))
             for j in range(i + 1, len(clauses))
             if (clauses[i], clauses[j]) not in already_resolved)

    for c1, c2 in pairs:
        resolvents = __resolve(c1, c2, max_clause_len)
        #if len(resolvents) != 0:
        #    print("RESOLVENTS", resolvents)
        if empty_set in resolvents:
            return True, list(map(propagate_substitutions, CLAUSE_MAPPING[empty_set]))

        new_inferrences.update(resolvents)
        already_resolved.add((c1, c2))

    #print("INFERRED", new_inferrences)
    if new_inferrences.issubset(clauses):
        return False, {}

    clauses.extend(clause for clause in new_inferrences
                   if not is_subsumed_in(clause, clauses))
   # print("CLAUSES", clauses)

    return None


def __resolve(first_clause, second_clause, max_len):
    resolvents = []
    __resolve_single_sided(first_clause, second_clause, resolvents)
    __resolve_single_sided(second_clause, first_clause, resolvents)
    return [r for r in resolvents
            if len(r) < max_len and not is_fo_disjunction_tautology(r)]


def __resolve_single_sided(c1, c2, resolvents):
    for symbol in c1:
        negation = LogicOperator.Negation + symbol
        for symbol2 in c2:
            if len(CLAUSE_MAPPING[c1]) == 0: CLAUSE_MAPPING[c1].append({})
            if len(CLAUSE_MAPPING[c2]) == 0: CLAUSE_MAPPING[c2].append({})
            for th1 in CLAUSE_MAPPING[c1]:
                for th2 in CLAUSE_MAPPING[c2]:
                    th = unify_substitutions(th1, th2)
                    theta = unify(negation, symbol2, th)
                    if theta is not problem.FAILURE:
                        result = c1.union(c2).difference({symbol, symbol2})
                        resolvents.append(__standardize_resolvent(result, theta))


def __standardize_resolvent(resolvent, theta):
    replacer = StandartizationReplacer("x")
    result = set()
    for index, disjunct in enumerate(resolvent):
        # Do we need standartization?
        result.add(substitute(disjunct, theta))
       # result.add(re.sub(replacer.REGEX, replacer, substitute(disjunct, theta)))

    StandartizationReplacer.GlobalIndex = replacer.index
    resolvent = frozenset(result)
    CLAUSE_MAPPING[resolvent].append(theta)
    return resolvent

def __parser(sentence):
    return parse_cnf(standardize_variables(sentence)[0])

KnowledgeBase = partial(logic.KnowledgeBase, __parser, resolution_prover)
