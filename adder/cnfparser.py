import re

from adder import utils
from adder.logic import Braces, LogicOperator, skolemize, SkolemRegex

def parse_fo_sentence(sentence):
   sentence = __move_negation_inwards(sentence)
   sentence = skolemize(sentence)
   sentence = __drop_universals(sentence)
   cnf = parse_propositional_sentence(sentence)
   return cnf


def parse_propositional_sentence(sentence):
    return __clean_cnf(__compute_cnf(sentence))


def __move_negation_inwards(sentence):
    next_negation = sentence.find(LogicOperator.Negation)
    while next_negation != -1:
        next_symbol_index = next_negation + 1
        while sentence[next_symbol_index] == Braces.Left:
            next_symbol_index += 1

        symbol = sentence[next_symbol_index]
        if symbol == LogicOperator.Every or \
           symbol == LogicOperator.Exists:
               operator = LogicOperator.Every if symbol != LogicOperator.Every \
                                              else LogicOperator.Exists
               next_left = sentence[next_symbol_index:].index(Braces.Left) + \
                           next_symbol_index

               variables = sentence[next_symbol_index + 1: next_left].strip()
               tail = sentence[next_left + 1:]
               next_right = Braces.find_unbalanced_right(tail)
               expression = tail[:next_right]
               rewritten = "{0} {1}({2}({3}))".format(operator, variables,
                                                      LogicOperator.Negation,
                                                      expression)
               # +3 = 1 from tail + 1 from + 1 to include the right brace
               original = sentence[next_negation: next_left + 3 + next_right]
               sentence = sentence.replace(original, rewritten)

        offset = len(variables) + 3 # +3 for the operator, space and (
        next_next_negation = sentence[next_negation + offset:].find(LogicOperator.Negation)
        if next_next_negation != -1:
            next_negation += next_next_negation + offset
        else:
            next_negation = -1

    return sentence


def __drop_universals(sentence):
    regex = SkolemRegex.EVERY
    current = re.sub(regex, "(", sentence)
    while (current != sentence):
        sentence = current
        current = re.sub(regex, "(", sentence)

    return sentence


def __clean_cnf(cnf):
    cnf = Braces.flatten(cnf)

    clauses = set()
    for disjunct_text in cnf.split(LogicOperator.Conjuction):
        left_replaced = disjunct_text.replace(Braces.Left, "")
        disjunct_text = left_replaced.replace(Braces.Right, "")
        if len(disjunct_text) == 0:
            continue

        disjunct = frozenset(symbol.strip() for symbol in
                             disjunct_text.split(LogicOperator.Disjunction))

        if not is_disjunction_tautology(disjunct):
            clauses.add(disjunct)

    return __clean_clauses(clauses)


def is_disjunction_tautology(disjunction):
    for symbol in disjunction:
        if LogicOperator.Negation + symbol in disjunction:
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
    cnf = __compute_cnf("({2}{0} {3} {1}) {4} ({2}{1} {3} {0})"
                           .format(lhs, rhs,
                                   LogicOperator.Negation,
                                   LogicOperator.Disjunction,
                                   LogicOperator.Conjuction))
    return cnf


def __implication_cnf(operands):
    lhs, rhs = operands
    cnf = __compute_cnf("{2}{0} {3} {1}".format(lhs, rhs,
                                                   LogicOperator.Negation,
                                                   LogicOperator.Disjunction))
    return cnf


def __disjunction_cnf(operands):
    lhs, rhs = operands
    first = __compute_cnf(lhs).split(LogicOperator.Conjuction)
    second = __compute_cnf(rhs).split(LogicOperator.Conjuction)
    cnf = ""
    for clause1 in first:
        for clause2 in second:
            cnf += "({0} {2} {1}) {3} ".format(clause1, clause2,
                                               LogicOperator.Disjunction,
                                               LogicOperator.Conjuction)

    return cnf[:-2]


def __conjuction_cnf(operands):
    lhs, rhs = operands
    cnf = "{0} {2} {1}".format(__compute_cnf(lhs),
                               __compute_cnf(rhs),
                               LogicOperator.Conjuction)
    return cnf


def __negation_cnf(operands):
    tail = Braces.remove_surrounding(operands[0])
    if __is_symbol(tail):
        return LogicOperator.Negation + tail

    tail_operation = __breakdown_sentence(tail)
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
                                              __compute_cnf(tail))

    return __compute_cnf(rewritten_formula)

__OPERATOR_PARSERS = {
    LogicOperator.Equivalence: __equivalence_cnf,
    LogicOperator.Implication: __implication_cnf,
    LogicOperator.Disjunction: __disjunction_cnf,
    LogicOperator.Conjuction: __conjuction_cnf,
    LogicOperator.Negation: __negation_cnf
}


def __compute_cnf(sentence):
    if __is_symbol(sentence):
        return sentence

    parsed = __breakdown_sentence(sentence)
    result = __OPERATOR_PARSERS[parsed[0]](parsed[1:])
    return result


def __is_symbol(sentence):
    return not (LogicOperator.Negation in sentence or
                LogicOperator.Conjuction in sentence or
                LogicOperator.Disjunction in sentence or
                LogicOperator.Implication in sentence or
                LogicOperator.Equivalence in sentence)


def __breakdown_sentence(sentence):
    sentence = Braces.remove_surrounding(sentence.strip())
    replaced = Braces.replace(sentence)
    operator = __get_operator(replaced[0])
    operands = __get_operands(replaced, operator)

    if not operands:
        msg = "Could not parse sentence '{0}'".format(sentence)
        raise utils.ParsingError(msg)

    return (operator, ) + operands


def __get_operator(replaced_sentence):
    for operator in LogicOperator.All:
        if operator in replaced_sentence:
            return operator


def __get_operands(replaced_sentence, operator):
    text, replacements = replaced_sentence

    if operator is None:
        return False

    if operator == LogicOperator.Negation:
        sentence = Braces.restore(text, replacements)
        if sentence[0] == operator:
            return (sentence[1:], )
        return False

    lhs, rhs = text.split(" {0} ".format(operator), maxsplit=1)
    separator = "!SEPARATOR!"
    separated = "{0} {1} {2}".format(lhs, separator, rhs)
    lhs, rhs = Braces.restore(separated, replacements).split(separator)
    return (lhs.strip(), rhs.strip())


def print_cnf_clause(clause):
    if isinstance(clause, frozenset):
        printable = " | ".join(sorted(clause))
    else:
        formula = ") & (".join([" | ".join(disjunct) for disjunct in clause])
        printable = "({0})".format(formula)

    print(printable)
