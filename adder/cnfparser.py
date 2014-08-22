import re

from adder import utils
from adder.logic import Braces, LogicOperator, skolemize, SkolemRegex

def parse_fo_sentence(sentence):
    cnf = __compute_cnf(sentence)
    cnf = skolemize(cnf)
    cnf = __drop_universals(cnf)
    return __clean_cnf(cnf)

def parse_propositional_sentence(sentence):
    return __clean_cnf(__compute_cnf(sentence))


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
        disjunct_text = disjunct_text.replace(Braces.Left, "")\
                                     .replace(Braces.Right, "")
        if len(disjunct_text) == 0:
            continue

        disjunct_text = disjunct_text.replace(Braces.FO_Left, Braces.Left)\
                                     .replace(Braces.FO_Right, Braces.Right)
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
    elif operator == LogicOperator.Every or operator == LogicOperator.Exists:
        negated_operator = LogicOperator.Exists if operator == LogicOperator.Every \
                                                else LogicOperator.Every
        variables, expression = tail_operands
        pattern = "{0} {1}({2}({3}))"
        rewritten_formula = pattern.format(negated_operator,
                                           variables,
                                           LogicOperator.Negation,
                                           expression)
    else:
        rewritten_formula = "{0}({1})".format(LogicOperator.Negation,
                                              __compute_cnf(tail))

    return __compute_cnf(rewritten_formula)


def __every_cnf(operands):
    return "{0} {1}({2})".format(LogicOperator.Every,
                                 operands[0],
                                 __compute_cnf(operands[1]).strip())


def __exists_cnf(operands):
    return "{0} {1}({2})".format(LogicOperator.Exists,
                                 operands[0],
                                 __compute_cnf(operands[1]).strip())


__OPERATOR_PARSERS = {
    LogicOperator.Equivalence: __equivalence_cnf,
    LogicOperator.Implication: __implication_cnf,
    LogicOperator.Disjunction: __disjunction_cnf,
    LogicOperator.Conjuction: __conjuction_cnf,
    LogicOperator.Negation: __negation_cnf,
    LogicOperator.Every: __every_cnf,
    LogicOperator.Exists: __exists_cnf
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
    for operator, regex in LogicOperator.AllRegex:
        if re.search(regex, replaced_sentence):
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

    if operator == LogicOperator.Every or \
       operator == LogicOperator.Exists:
           op_index = text.index(operator)
           left_brace = text[op_index:].index(Braces.Left)
           variables = text[op_index + 1:left_brace].strip()
           expression = replacements[0][1:-1]
           return (variables, expression)

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
