import re
import itertools

from adder import utils
from adder.logic import Braces
from adder.logic import LogicOperator


class DefiniteClause:
    def __init__(self, text):
        self.premises, self.conclusion = self.__parse(text)
        self.is_fact = len(self.premises) == 0

    def __parse(self, text):
        if LogicOperator.Implication in text:
            lhs, rhs = text.split(LogicOperator.Implication)

            premises = {symbol.strip() for symbol in
                        lhs.split(LogicOperator.Conjuction)}
            conclusions = [rhs.strip()]
        else:
            symbols = [symbol.strip() for symbol in
                       text.split(LogicOperator.Disjunction)]

            premises = {symbol[1:] for symbol in symbols
                        if symbol[0] == LogicOperator.Negation}
            conclusions = [symbol for symbol in symbols
                           if symbol[0] != LogicOperator.Negation]
        if len(conclusions) != 1:
            msg = "A clause must have EXACTLY one positive symbol"
            raise utils.InvalidArgumentError(msg)

        return (premises, conclusions[0])

    def __str__(self):
        return "{0} => {1}".format(" & ".join(self.premises), self.conclusion)

    __repr__ = __str__

    def __eq__(self, other):
        return str(self) == str(other)

    def __neq__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))


class DefiniteKnowledgeBase:
    def __init__(self, text=""):
        self.raw_kb = [DefiniteClause(clause)
                       for clause in text.strip().split("\n")
                       if len(clause) != 0]

    def ask(self, query):
        return backward_chaining(self.raw_kb, query)

    def tell(self, *args):
        for sentence in args:
            self.raw_kb.append(DefiniteClause(sentence.strip()))

    def __eq__(self, other):
        return set(self.raw_kb) == set(other.raw_kb)

    def __neq__(self, other):
        return not (self == other)


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
            self.raw_kb += parse_sentence_to_cnf(sentence.strip())

    def __eq__(self, other):
        return set(self.raw_kb) == set(other.raw_kb)

    def __neq__(self, other):
        return not (self == other)


def resolution_prover(knowledge_base, query, max_clause_len, information_rich):
    negated_query = "{0}({1})".format(LogicOperator.Negation, query)
    not_query_cnf = parse_sentence_to_cnf(negated_query)
    clauses = not_query_cnf + knowledge_base
    new_inferrences = set()
    already_resolved = set()

    clauses2 = parse_sentence_to_cnf(query) + knowledge_base
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
            if len(r) < max_len and not __is_tautology(r)]


def __resolve_single_sided(c1, c2, resolvents):
    for symbol in c1:
        negation = LogicOperator.Negation + symbol
        if negation in c2:
            resolvents.append(c1.union(c2).difference({symbol, negation}))


def parse_knowledge_base(text):
    return [clause
            for sentence in text.strip().split("\n")
            for clause in parse_sentence_to_cnf(sentence)]


def parse_sentence_to_cnf(sentence):
    cnf = Braces.flatten_braces(__convert_to_cnf(sentence))

    clauses = set()
    for disjunct_text in cnf.split(LogicOperator.Conjuction):
        left_replaced = disjunct_text.replace(Braces.Left, "")
        disjunct_text = left_replaced.replace(Braces.Right, "")
        if len(disjunct_text) == 0:
            continue

        disjunct = frozenset(symbol.strip() for symbol in
                             disjunct_text.split(LogicOperator.Disjunction))

        if not __is_tautology(disjunct):
            clauses.add(disjunct)

    return __clean_clauses(clauses)


def __is_tautology(disjunct):
    for symbol in disjunct:
        if LogicOperator.Negation + symbol in disjunct:
            return True
    return False


def __clean_clauses(clauses):
    result = []
    for clause in clauses:
        is_superset_of_another = any(conjuct < clause for conjuct in clauses)
        if not is_superset_of_another:
            result.append(clause)

    return result


def __equivalence_cnf(operands):
    lhs, rhs = operands
    cnf = __convert_to_cnf("({2}{0} {3} {1}) {4} ({2}{1} {3} {0})"
                           .format(lhs, rhs,
                                   LogicOperator.Negation,
                                   LogicOperator.Disjunction,
                                   LogicOperator.Conjuction))
    return cnf


def __implication_cnf(operands):
    lhs, rhs = operands
    cnf = __convert_to_cnf("{2}{0} {3} {1}".format(lhs, rhs,
                                                   LogicOperator.Negation,
                                                   LogicOperator.Disjunction))
    return cnf


def __disjunction_cnf(operands):
    lhs, rhs = operands
    first = __convert_to_cnf(lhs).split(LogicOperator.Conjuction)
    second = __convert_to_cnf(rhs).split(LogicOperator.Conjuction)
    cnf = ""
    for clause1 in first:
        for clause2 in second:
            cnf += "({0} {2} {1}) {3} ".format(clause1, clause2,
                                               LogicOperator.Disjunction,
                                               LogicOperator.Conjuction)

    return cnf[:-2]


def __conjuction_cnf(operands):
    lhs, rhs = operands
    cnf = "{0} {2} {1}".format(__convert_to_cnf(lhs),
                               __convert_to_cnf(rhs),
                               LogicOperator.Conjuction)
    return cnf


def __negation_cnf(operands):
    tail = Braces.remove_surrounding_parenthesis(operands[0])
    if __is_var(tail):
        return LogicOperator.Negation + tail

    tail_operation = parse_sentence(tail)
    operator = tail_operation[0]
    tail_operands = tail_operation[1:]
    rewritten_formula = ""
    if operator == LogicOperator.Negation:
        rewritten_formula = tail_operands[0]
    elif operator == LogicOperator.Conjuction:
        lhs, rhs = tail_operands
        pattern = "{2}{0} {3} {2}{1}"
        rewritten_formula = pattern.format(lhs, rhs,
                                           LogicOperator.Negation,
                                           LogicOperator.Disjunction)
    elif operator == LogicOperator.Disjunction:
        lhs, rhs = tail_operands
        pattern = "{2}{0} {3} {2}{1}"
        rewritten_formula = pattern.format(lhs, rhs,
                                           LogicOperator.Negation,
                                           LogicOperator.Conjuction)
    else:
        rewritten_formula = "{0}({1})".format(LogicOperator.Negation,
                                              __convert_to_cnf(tail))

    return __convert_to_cnf(rewritten_formula)

__OPERATOR_PARSERS = {
    LogicOperator.Equivalence: __equivalence_cnf,
    LogicOperator.Implication: __implication_cnf,
    LogicOperator.Disjunction: __disjunction_cnf,
    LogicOperator.Conjuction: __conjuction_cnf,
    LogicOperator.Negation: __negation_cnf
}


def __convert_to_cnf(sentence):
    if __is_var(sentence):
        return sentence

    parsed = parse_sentence(sentence)
    result = __OPERATOR_PARSERS[parsed[0]](parsed[1:])
    return result


def __is_var(sentence):
    return not (LogicOperator.Negation in sentence or
                LogicOperator.Conjuction in sentence or
                LogicOperator.Disjunction in sentence or
                LogicOperator.Implication in sentence or
                LogicOperator.Equivalence in sentence)


def parse_sentence(sentence):
    sentence = Braces.remove_surrounding_parenthesis(sentence.strip())
    brace_replaced = Braces.brace_replace(sentence)
    operator = __get_operator(brace_replaced[0])
    operands = __get_operands(brace_replaced, operator)

    if not operands:
        msg = "Could not parse sentence '{0}'".format(sentence)
        raise utils.ParsingError(msg)

    return (operator, ) + operands


def __get_operator(brace_replaced_sentence):
    operator_precedence = [
        LogicOperator.Equivalence,
        LogicOperator.Implication,
        LogicOperator.Disjunction,
        LogicOperator.Conjuction,
        LogicOperator.Negation
    ]

    for operator in operator_precedence:
        if operator in brace_replaced_sentence:
            return operator


def __get_operands(brace_replaced_sentence, operator):
    text, replacements = brace_replaced_sentence

    if operator is None:
        return False

    if operator == LogicOperator.Negation:
        sentence = Braces.restore_braces(text, replacements)
        if sentence[0] == operator:
            return (sentence[1:], )
        return False

    lhs, rhs = text.split(" {0} ".format(operator), maxsplit=1)
    separator = "!SEPARATOR!"
    separated = "{0} {1} {2}".format(lhs, separator, rhs)
    lhs, rhs = Braces.restore_braces(separated, replacements).split(separator)
    return (lhs.strip(), rhs.strip())


def print_cnf_clause(clause):
    if isinstance(clause, frozenset):
        printable = " | ".join(sorted(clause))
    else:
        formula = ") & (".join([" | ".join(disjunct) for disjunct in clause])
        printable = "({0})".format(formula)

    print(printable)
