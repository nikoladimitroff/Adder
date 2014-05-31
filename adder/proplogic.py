from adder import utils
import re
import itertools

class LogicOperator:
    Conjuction = "&"
    Disjunction = "|"
    Negation = "!"
    Implication = "=>"
    Equivalence = "<=>"


class _Braces:
    Left = "("
    Right = ")"
    Placeholder = "*"
    
    @staticmethod
    def remove_surrounding_parenthesis(sentence):    
        if sentence[0] == _Braces.Left and \
           sentence[-1] == _Braces.Right:
            braces = 1
            for symbol in sentence[1:-1]:
                if symbol == _Braces.Left: braces += 1
                if symbol == _Braces.Right: braces -= 1
                if braces == 0: return sentence
            return sentence[1:-1]
        return sentence
    
    @staticmethod
    def flatten_braces(text):
        tlb = False
        braces = 0
        result = ""
        for symbol in text:
            if symbol == _Braces.Left:
                if braces == 0:
                    tlb = True
                    result += _Braces.Left
                braces += 1
            elif symbol == _Braces.Right:
                braces -= 1
                if braces == 0:
                    tlb = False
                    result += _Braces.Right
            else:
                result += symbol
            
        return result


    @staticmethod
    def brace_replace(text):
        braces = 0
        tlb = False
        result = ""
        replacement_table = []
        replacement_index = -1
        for symbol in text:
            if tlb and (braces != 1 or symbol != _Braces.Right):
                result += _Braces.Placeholder
                replacement_table[replacement_index] += symbol
            else:
                result += symbol
            
            if symbol == _Braces.Left:
                if braces == 0:
                    tlb = True
                    replacement_table.append(_Braces.Left)
                    replacement_index += 1
                braces += 1
            elif symbol == _Braces.Right:
                braces -= 1
                if braces == 0:
                    tlb = False
                    replacement_table[replacement_index] += _Braces.Right

        return (re.sub("\*+", _Braces.Placeholder, result), replacement_table)
    
    @staticmethod
    def restore_braces(text, replacement_table):
        for entry in replacement_table:
            text = text.replace("({0})".format(_Braces.Placeholder), entry, 1)
    
        return text


class DefiniteClause:
    def __init__(self, text):
        self.premises, self.conclusion = self.__parse(text)
        self.is_fact = len(self.premises) == 0

    def __parse(self, text):
        if LogicOperator.Implication in text:
            lhs, rhs = text.split(LogicOperator.Implication)
            premises = {symbol.strip() for symbol in lhs.split(LogicOperator.Conjuction)}
            conclusions = [rhs.strip()]
        else:
            symbols = [symbol.strip() for symbol in text.split(LogicOperator.Disjunction)]
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


def parse_definite_knowledge_base(text):
    return [DefiniteClause(clause) for clause in text.strip().split("\n")]


def forward_chaining(knowledge_base, query):
    premises_count = { clause: len(clause.premises) for clause in knowledge_base}
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
    true_symbols = {clause.conclusion for clause in knowledge_base if clause.is_fact}

    return __backward_chaining_step(knowledge_base, query, true_symbols, true_symbols)

def __backward_chaining_step(kb, query, true_symbols, checked):
    if query in true_symbols:
        return True

    applicable_implications = (clause for clause in kb 
                               if query == clause.conclusion)

    return any(__check_clause(kb, true_symbols, checked, clause) 
               for clause in applicable_implications)

def __check_clause(kb, true_symbols, checked, clause):
    all = True
    for premise in clause.premises:
        if premise not in checked:
            is_premise_true = __backward_chaining_step(kb, premise, true_symbols, 
                                                checked.union({premise}))
            all = all and is_premise_true
    return all

def resolution_prover(knowledge_base, query):
    not_query_cnf = parse_cnf_sentence("{0}({1})".format(LogicOperator.Negation, query))
    clauses = knowledge_base + not_query_cnf
    while True:
        new_inferrences = []
        for c1, c2 in itertools.product(clauses, clauses):
            if c1 is c2: continue
            resolvents = __resolve(c1, c2)
            if set() in resolvents:
                return True

            for resolvent in resolvents:
                if resolvent not in clauses and resolvent not in new_inferrences:
                    new_inferrences.append(resolvent)
        if len(new_inferrences) == 0:
            return False
        clauses += new_inferrences

@utils.memoize
def __resolve(first_clause, second_clause):
    resolvents = []
    __resolve_single_sided(first_clause, second_clause, resolvents)
    __resolve_single_sided(second_clause, first_clause, resolvents)
    return resolvents


def __resolve_single_sided(c1, c2, resolvents):
    for symbol in c1:
        negation = LogicOperator.Negation + symbol
        if negation in c2:
            resolvents.append(c1.union(c2).difference({symbol, negation}))


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
    tail = _Braces.remove_surrounding_parenthesis(operands[0])
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

def parse_cnf_knowledge_base(text):
    return [clause for sentence in text.strip().split("\n") 
            for clause in parse_cnf_sentence(sentence)]

def parse_cnf_sentence(sentence):
    cnf = _Braces.flatten_braces(__convert_to_cnf(sentence))
   
    clauses = []
    for disjunct_text in cnf.split(LogicOperator.Conjuction):
        disjunct_text = disjunct_text.replace(_Braces.Left, "") \
                            .replace(_Braces.Right, "")
        if len(disjunct_text) == 0:
            continue

        disjunct = {symbol.strip() for symbol in 
                    disjunct_text.split(LogicOperator.Disjunction)}

        if not __is_disjunct_true(disjunct):
            clauses.append(disjunct)

    return __clean_clauses(clauses)

def __is_disjunct_true(disjunct):
    return any(LogicOperator.Negation + symbol in disjunct 
               for symbol in disjunct)

def __clean_clauses(clauses):
    unique = []
    for clause in clauses:
        if clause not in unique:
            unique.append(clause)
    
    result = []
    for clause in unique:
        is_superset = any([conjuct < clause for conjuct in unique])
        if not is_superset:
            result.append(clause)

    return result


def __convert_to_cnf(sentence):
    # Match every pair of (). Substitue with *
    # For each of them, call recursively the same func
    # If the sentence has no parenthesis, swap a <=> b with (!a | b) & (!b | a)
    # If the sentence contains implication, swap a => b with (!a | b)
    # Push the negation up to vars
    # Use distrubutivity
    

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
    # remove surrounding parenthesis
    sentence = _Braces.remove_surrounding_parenthesis(sentence.strip())
    brace_replaced = _Braces.brace_replace(sentence)
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
    result, replacements = brace_replaced_sentence

    if operator == LogicOperator.Negation:
        sentence = _Braces.restore_braces(result, replacements)
        if sentence[0] == operator:
            return (sentence[1:], )
        return False

    if operator not in result:
        return False
    lhs, rhs = result.split(" {0} ".format(operator), maxsplit=1)
    separator = "!SEPARATOR!"
    separated = "{0} {1} {2}".format(lhs, separator, rhs)
    lhs, rhs = _Braces.restore_braces(separated, replacements).split(separator)
    return (lhs.strip(), rhs.strip())


def print_cnf_clause(clause):
    printable = "(" +") & (".join([" | ".join(disjunct) for disjunct in clause]) + ")"
    return printable