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
                        if symbol[0] == LogicOperator.Negation }
            conclusions = [symbol for symbol in symbols 
                           if symbol[0] != LogicOperator.Negation]
        if len(conclusions) != 1:
            raise utils.InvalidArgumentException("The clause is not definite i.e. it doesn't have EXACTLY one positive symbol")

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
    def __init__(self, text):
        self.raw_kb = [DefiniteClause(clause) for clause in text.strip().split("\n")]

    def ask(self, query):
        return backward_chaining(self.raw_kb, query)

    def tell(self, *args):
        for sentence in args:
            self.raw_kb.append(DefiniteClause(sentence.strip()))

    def __eq__(self, other):
        return self.raw_kb == other.raw_kb

    def __neq__(self, other):
        return not (self == other)


def forward_chaining(knowledge_base, query):
    premises_count = {clause: len(clause.premises) for clause in knowledge_base}
    inferred = {}
    true_symbols = [clause.conclusion for clause in knowledge_base if clause.is_fact]

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

    return __backward_chaining_step(knowledge_base, query, true_symbols, true_symbols)


def __backward_chaining_step(kb, query, true_symbols, checked):
    if query in true_symbols:
        return True

    applicable_implications = (clause for clause in kb 
                               if query == clause.conclusion)

    return any(__check_implication(kb, true_symbols, checked, clause)
               for clause in applicable_implications)


def __check_implication(kb, true_symbols, checked, clause):
    all = True
    for premise in clause.premises:
        if premise not in checked:
            is_premise_true = __backward_chaining_step(kb, 
                                                       premise, 
                                                       true_symbols,
                                                       checked.union({premise}))
            all = all and is_premise_true
    return all


class PlKnowledgeBase:
    def __init__(self, text, max_clause_len=float("inf")):
        self.raw_kb = parse_cnf_knowledge_base(text)
        self.max_clause_len = max_clause_len

    def ask(self, query):
        return resolution_prover(self.raw_kb, query, max_clause_len=self.max_clause_len)

    def tell(self, *args):
        for sentence in args:
            self.raw_kb += parse_cnf_sentence(sentence)

    def __eq__(self, other):
        return self.raw_kb == other.raw_kb

    def __neq__(self, other):
        return not (self == other)


def resolution_prover(knowledge_base, query, max_clause_len=float("inf")):
    negated_query = "{0}({1})".format(LogicOperator.Negation, query)
    not_query_cnf = parse_cnf_sentence(negated_query)
    clauses = not_query_cnf + knowledge_base
    start_size = len(clauses)
    empty_set = frozenset()
    new_inferrences = set()
    while True:
        new_inferrences.clear()
        pairs = [(clauses[i], clauses[j]) 
                 for i in range(len(clauses))
                 for j in range(i + 1, len(clauses))]

        for c1, c2 in pairs:
            resolvents = __resolve(c1, c2, max_clause_len)
            if empty_set in resolvents:
                return True

            new_inferrences.update(resolvents)
        if new_inferrences.issubset(clauses):
            return False

        clauses.extend(clause for clause in new_inferrences 
                       if clause not in clauses)


@utils.memoize
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


def parse_cnf_knowledge_base(text):
    return [clause 
            for sentence in text.strip().split("\n") 
            for clause in parse_cnf_sentence(sentence)]


def parse_cnf_sentence(sentence):
    cnf = Braces.flatten_braces(__convert_to_cnf(sentence))
   
    clauses = set()
    for disjunct_text in cnf.split(LogicOperator.Conjuction):
        disjunct_text = disjunct_text.replace(Braces.Left, "") \
                            .replace(Braces.Right, "")
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
        rewritten_formula = "{2}{0} {3} {2}{1}".format(lhs, rhs, 
                                                       LogicOperator.Negation, 
                                                       LogicOperator.Disjunction)
    elif operator == LogicOperator.Disjunction:
        lhs, rhs = tail_operands
        rewritten_formula = "{2}{0} {3} {2}{1}".format(lhs, rhs, 
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
    return not (LogicOperator.Negation in sentence or \
           LogicOperator.Conjuction in sentence or \
           LogicOperator.Disjunction in sentence or \
           LogicOperator.Implication in sentence or \
           LogicOperator.Equivalence in sentence)


def parse_sentence(sentence):
    sentence = Braces.remove_surrounding_parenthesis(sentence.strip())
    brace_replaced = Braces.brace_replace(sentence)
    operator = __get_operator(brace_replaced[0])
    operands = __get_operands(brace_replaced, operator)

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

    if operator == LogicOperator.Negation:
        sentence = Braces.restore_braces(text, replacements)
        if sentence[0] == operator:
            return (sentence[1:], )
        return False

    if operator not in text:
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
        printable = "(" + ") & (".join([" | ".join(disjunct) for disjunct in clause]) + ")"
    
    print(printable)