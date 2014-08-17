import re
import itertools
from functools import partial

from adder import utils, logic
from adder.logic import Braces, LogicOperator, DefiniteClause, SkolemRegex, skolemize
from adder.cnfparser import parse_propositional_sentence as parse_cnf, \
                            is_disjunction_tautology

def forward_chaining(knowledge_base, query):
    premises_count = {clause: len(clause.premises)
                      for clause in knowledge_base}
    inferred = {}
    true_symbols = [clause.conclusion for clause in knowledge_base
                    if clause.is_fact]

    while len(true_symbols) != 0:
        symbol = true_symbols.pop(0)

        if symbol == query:
            return True

        if symbol not in inferred:
            inferred[symbol] = True
            for clause in knowledge_base:
                if symbol in clause.premises:
                    premises_count[clause] -= 1
                    if premises_count[clause] == 0:
                        true_symbols.append(clause.conclusion)

    return False


def backward_chaining(knowledge_base, query):
    true_symbols = {clause.conclusion for clause in knowledge_base
                    if clause.is_fact}

    return __or_step(knowledge_base, query,
                     true_symbols, true_symbols)

def __or_step(kb, query, true_symbols, checked):
    if query in true_symbols:
        return True

    applicable_implications = (clause for clause in kb
                               if query == clause.conclusion)

    return any(__and_step(kb, true_symbols, checked, clause)
               for clause in applicable_implications)


def __and_step(kb, true_symbols, checked, implication):
    all = True
    for premise in implication.premises:
        if premise not in checked:
            is_premise_true = __or_step(kb, premise, true_symbols,
                                        checked.union({premise}))
            all = all and is_premise_true
    return all

DefiniteKnowledgeBase = partial(logic.DefiniteKnowledgeBase, backward_chaining)

class KnowledgeBase:
    def __init__(self, text="", max_clause_len=float("inf"),
                 information_rich=True):
        self.raw_kb = parse_knowledge_base(text)
        self.max_clause_len = max_clause_len
        self.information_rich = information_rich

    def ask(self, query):
        return resolution_prover(self.raw_kb, query,
                                 self.max_clause_len,
                                 self.information_rich)

    def tell(self, *args):
        for sentence in args:
            self.raw_kb += parse_cnf(sentence.strip())

    def __eq__(self, other):
        return set(self.raw_kb) == set(other.raw_kb)

    def __neq__(self, other):
        return not (self == other)


def resolution_prover(knowledge_base, query, max_clause_len, information_rich):
    negated_query = "{0}({1})".format(LogicOperator.Negation, query)
    not_query_cnf = parse_cnf(negated_query)
    clauses = not_query_cnf + knowledge_base
    new_inferrences = set()
    already_resolved = set()

    clauses2 = parse_cnf(query) + knowledge_base
    new_inferrences2 = set()
    already_resolved2 = set()

    empty_set = frozenset()

    while True:
        result = __resolution_step(new_inferrences, already_resolved,
                                   clauses, max_clause_len)
        if result is not None:
            return result

        if information_rich:
            result = __resolution_step(new_inferrences2, already_resolved2,
                                       clauses2, max_clause_len)
            if result is not None:
                return not result


def __resolution_step(new_inferrences, already_resolved, clauses,
                      max_clause_len, empty_set=frozenset()):
    new_inferrences.clear()
    pairs = ((clauses[i], clauses[j])
             for i in range(len(clauses))
             for j in range(i + 1, len(clauses))
             if (clauses[i], clauses[j]) not in already_resolved)

    for c1, c2 in pairs:
        resolvents = __resolve(c1, c2, max_clause_len)
        if empty_set in resolvents:
            return True

        new_inferrences.update(resolvents)
        already_resolved.add((c1, c2))

    if new_inferrences.issubset(clauses):
        return False

    clauses.extend(clause for clause in new_inferrences
                   if clause not in clauses)

    return None


def __resolve(first_clause, second_clause, max_len):
    resolvents = []
    __resolve_single_sided(first_clause, second_clause, resolvents)
    __resolve_single_sided(second_clause, first_clause, resolvents)
    return [r for r in resolvents
            if len(r) < max_len and not is_disjunction_tautology(r)]


def __resolve_single_sided(c1, c2, resolvents):
    for symbol in c1:
        negation = LogicOperator.Negation + symbol
        if negation in c2:
            resolvents.append(c1.union(c2).difference({symbol, negation}))


def parse_knowledge_base(text):
    return [clause
            for sentence in text.strip().split("\n")
            for clause in parse_cnf(sentence)]
