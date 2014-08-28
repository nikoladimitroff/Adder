from functools import partial
from collections import defaultdict
import re

from adder import problem, logic
from adder.logic import (Braces, LogicOperator, DefiniteClause,
                         standardize_variables, StandartizationReplacer,
                         skolemize, unify, unify_substitutions, substitute,
                         propagate_substitutions,
                         find_variables_symbol, find_variables_expression,
                         is_subsumed_by)

from adder.utils import ParsingError
from adder.cnfparser import (parse_fo_sentence as parse_cnf,
                             is_fo_disjunction_tautology, print_cnf)


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


class ClauseBindingMapper:
    def __init__(self):
        self.container = defaultdict(list)
        self.memo = {}

    def get_from_key(self, c1, c2, i, j):
        key = (c1, c2, i, j)
        if self.memo.get(key) is None:
            self.memo[key] = unify_substitutions(self.container[c1][i],
                                                 self.container[c2][j])
        return self.memo[key]

    def get_unified_bindings(self, c1, c2):
        if len(self.container[c1]) == 0:
            self.container[c1].append({})
        if len(self.container[c2]) == 0:
            self.container[c2].append({})
        return (self.get_from_key(c1, c2, i, j)
                for i, th1 in enumerate(self.container[c1])
                for j, th2 in enumerate(self.container[c2]))


def resolution_prover(knowledge_base, query, max_clause_len, is_complete):
    negated_query = "{0}({1})".format(LogicOperator.Negation, query)
    not_query_cnf = parse_cnf(negated_query)
    clauses = not_query_cnf + knowledge_base
    new_inferrences = set()
    already_resolved = set()
    clause_theta_mapping = ClauseBindingMapper()

    clauses2 = parse_cnf(query) + knowledge_base
    new_inferrences2 = set()
    already_resolved2 = set()
    clause_theta_mapping2 = ClauseBindingMapper()

    empty_set = frozenset()
    support = not_query_cnf
    support2 = parse_cnf(query)

    while True:
        result = __resolution_step(new_inferrences, already_resolved,
                                   clauses, max_clause_len,
                                   clause_theta_mapping)
        if result is not None:
            if result[0]:
                return {var: value for var, value in result[1].items()
                        if var in find_variables_expression(query)}

            return problem.FAILURE

        if is_complete:
            result = __resolution_step(new_inferrences2, already_resolved2,
                                       clauses2, max_clause_len,
                                       clause_theta_mapping2)
            if result is not None:
                if result[0]:
                    return {var: value for var, value in result[1].items()
                            if var in find_variables_expression(query)}
                return problem.FAILURE


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
            bindings = clause_mapping.container[empty_set][0]
            bindings = propagate_substitutions(bindings)
            return True, bindings

        new_inferrences.update(resolvents)
        already_resolved.add((c1, c2))

    if new_inferrences.issubset(clauses):
        return False, {}

    clauses.extend(clause for clause in new_inferrences
                   if not is_subsumed_in(clause, clauses))

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
            for th in clause_mapping.get_unified_bindings(c1, c2):
                theta = unify(negation, symbol2, th)
                if theta is not problem.FAILURE:
                    result = c1.union(c2).difference({symbol1, symbol2})
                    resolvent = __standardize_resolvent(result, theta)
                    resolvents.append(resolvent)
                    clause_mapping.container[resolvent].append(theta)


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
