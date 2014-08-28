import re
from collections import defaultdict

from adder import utils
from adder import problem


class LogicOperator:
    Conjuction = "&"
    Disjunction = "|"
    Negation = "!"
    Implication = "=>"
    Equivalence = "<=>"
    Every = "V"
    Exists = "E"


LogicOperator.All = [
    LogicOperator.Equivalence,
    LogicOperator.Implication,
    LogicOperator.Disjunction,
    LogicOperator.Conjuction,
    LogicOperator.Negation,
    LogicOperator.Every,
    LogicOperator.Exists
]


LogicOperator.AllRegex = [
    (LogicOperator.Equivalence, re.compile(LogicOperator.Equivalence)),
    (LogicOperator.Implication, re.compile(LogicOperator.Implication)),
    (LogicOperator.Disjunction, re.compile(r"\|")),
    (LogicOperator.Conjuction, re.compile(LogicOperator.Conjuction)),
    (LogicOperator.Negation, re.compile(LogicOperator.Negation)),
    (LogicOperator.Every, re.compile(r"\b{0}\b".format(LogicOperator.Every))),
    (LogicOperator.Exists, re.compile(r"\b{0}\b".format(LogicOperator.Exists)))
]


class Braces:
    Left = "("
    Right = ")"
    Placeholder = "#"
    FO_Left = "$FO_LEFT$"
    FO_Right = "$FO_RIGHT$"

    @staticmethod
    def remove_surrounding(sentence):
        sentence = sentence.strip()
        while (sentence[0] == Braces.Left and
               sentence[-1] == Braces.Right):

            braces = 1
            for symbol in sentence[1:-1]:
                if symbol == Braces.Left:
                    braces += 1
                if symbol == Braces.Right:
                    braces -= 1
                if braces == 0:
                    return sentence
            sentence = sentence[1:-1].strip()
        return sentence

    @staticmethod
    def flatten(text, is_first_order):
        func = Braces.__flatten_fo if is_first_order else Braces.__flatten_prop
        return func(text)

    @staticmethod
    def __flatten_prop(text):
        tlb = False
        braces = 0
        result = ""
        for index, symbol in enumerate(text):
            if symbol == Braces.Left:
                if braces == 0:
                    tlb = True
                if tlb:
                    result += Braces.Left
                braces += 1
            elif symbol == Braces.Right:
                braces -= 1
                if braces == 0:
                    result += Braces.Right
                if braces != 0:
                    tlb = False
            else:
                result += symbol

        return result

    @staticmethod
    def __flatten_fo(text):
        tlb = False
        fo_braces = 0
        braces = 0
        result = ""
        for index, symbol in enumerate(text):
            if symbol == Braces.Left:
                next_right = Braces.find_unbalanced_right(text[index + 1:])
                between_braces = text[index: index + next_right + 1]
                contains_operator = any(re.search(regex, between_braces)
                                        for op, regex in LogicOperator.AllRegex)
                if not contains_operator and \
                   index > 0 and text[index - 1] != " ":
                    fo_braces += 1
                if contains_operator and braces == 0:
                    tlb = True
                if fo_braces > 0:
                    result += Braces.FO_Left
                elif tlb:
                    result += Braces.Left
                braces += 1
            elif symbol == Braces.Right:
                braces -= 1
                if fo_braces > 0:
                    fo_braces -= 1
                    result += Braces.FO_Right
                elif braces == 0:
                    result += Braces.Right
                if braces != 0 and fo_braces == 0:
                    tlb = False
            else:
                result += symbol

        return result

    @staticmethod
    def replace(text):
        braces = 0
        tlb = False
        result = ""
        replacement_table = []
        replacement_index = -1
        for symbol in text:
            if tlb and (braces != 1 or symbol != Braces.Right):
                result += Braces.Placeholder
                replacement_table[replacement_index] += symbol
            else:
                result += symbol

            if symbol == Braces.Left:
                if braces == 0:
                    tlb = True
                    replacement_table.append(Braces.Left)
                    replacement_index += 1
                braces += 1
            elif symbol == Braces.Right:
                braces -= 1
                if braces == 0:
                    tlb = False
                    replacement_table[replacement_index] += Braces.Right

        replaced = re.sub("{0}+".format(Braces.Placeholder),
                          Braces.Placeholder, result)
        return (replaced, replacement_table)

    @staticmethod
    def restore(text, replacement_table):
        for entry in replacement_table:
            text = text.replace("({0})".format(Braces.Placeholder), entry, 1)

        return text

    @staticmethod
    def find_unbalanced_right(expression):
        braces = 0
        for index, symbol in enumerate(expression):
            if symbol == '(':
                braces += 1
            elif symbol == ')':
                braces -= 1
            if braces == -1:
                return index


class SkolemRegex:
    COMMON = r"{0} ((?:\w+, ?)*(?:\w+))\("


SkolemRegex.EVERY = re.compile(SkolemRegex.COMMON.format(LogicOperator.Every))
SkolemRegex.EXISTS = re.compile(SkolemRegex.COMMON.format(LogicOperator.Exists))


class Skolemizer:
    def __init__(self):
        self.constants = 0
        self.functions = 0

    def find_all_variables(self, expression):
        tree = self.__build_tree(expression)
        reversed = self.__reverse_tree(tree)
        vars = []
        for existentials, parents in reversed.items():
            vars += existentials.replace(" ", "").split(",")
        return vars

    def skolemize(self, expression):
        tree = self.__build_tree(expression)
        reversed = self.__reverse_tree(tree)
        replacements = {}
        for existentials, parents in reversed.items():
            vars = existentials.replace(" ", "").split(",")
            parents.remove(None)
            universals = ",".join(parents).replace(" ", "").split(",")
            for var in vars:
                replacements[var] = self.skolemize_var(var, universals)

        expression = re.sub(SkolemRegex.EXISTS, "(", expression)

        for var, skolemized in replacements.items():
            regex = r"\b{0}\b".format(var)
            skolemizer = self.get_replacer(skolemized)
            expression = re.sub(regex, skolemizer, expression)

        return expression

    def skolemize_var(self, var, universals):
        if len(universals) == 1 and len(universals[0]) == 0:
            self.constants += 1
            return "SC{0}".format(self.constants)
        else:
            self.functions += 1
            return "SF{0}({1})".format(self.functions, ", ".join(universals))

    def get_replacer(self, skolemized):
        def replacer(match):
            if re.match(SkolemRegex.EXISTS, match.group()):
                return match.group()
            return skolemized
        return replacer

    def __reverse_tree(self, tree):
        frontier = [(None, tree[None])]
        reversed = defaultdict(list)
        is_parent = {}
        while len(frontier) > 0:
            parent, node = frontier.pop(0)
            for child in node:
                if isinstance(child, str):
                    reversed[child] = reversed[parent] + [parent]
                elif isinstance(child, dict):
                    child_name = list(child.keys())[0]
                    if len(child[child_name]) > 0:
                        frontier.append((child_name, child[child_name]))
                        reversed[child_name] = reversed[parent] + [parent]
                elif isinstance(child, list):
                    for vars in child:
                        reversed[child] = reversed[parent] + [parent]
                is_parent[parent] = True

        return {key: value for key, value in reversed.items()
                if key not in is_parent}

    def __build_tree(self, expression, root=None):
        universal = self.__first_universal(expression)
        if not universal:
            return {root: self.__all_existenstials(expression)}

        left_end = universal.span()[1]
        right_end = Braces.find_unbalanced_right(expression[left_end:])
        if not right_end:
            raise ParsingError("Unbalanced parenthesis")
        right_end += left_end

        left = expression[:universal.span()[0]]
        middle = expression[left_end:right_end]
        right = expression[right_end:]

        left_tree = self.__build_tree(left, root)
        middle_tree = self.__build_tree(middle, universal.group(1))
        right_tree = self.__build_tree(right, root)
        return {root: left_tree[root] + [middle_tree] + right_tree[root]}

    def __first_universal(self, expression):
        return re.search(SkolemRegex.EVERY, expression)

    def __all_existenstials(self, expression):
        return re.findall(SkolemRegex.EXISTS, expression)


def skolemize(expression, skolemizer=Skolemizer()):
    return skolemizer.skolemize(expression)


class StandartizationReplacer:
    REGEX = re.compile(r"\b[a-z][a-z0-9]*\b", re.ASCII)
    GlobalIndex = 0

    def __init__(self, var, use_global=True):
        self.var = var
        self.index = self.GlobalIndex if use_global else 0
        self.replacements = {}

    def __call__(self, match):
        result = match.group()
        if result not in self.replacements:
            self.replacements[result] = self.var + str(self.index)
            self.index += 1

        return self.replacements[result]


def standardize_variables(expression, var="x", use_global=True):
    replacer = StandartizationReplacer(var, use_global)
    result = re.sub(replacer.REGEX, replacer, expression)
    if use_global:
        StandartizationReplacer.GlobalIndex = replacer.index
    return result, replacer.replacements


class Substituer:
    def __init__(self, theta):
        self.theta = theta
        if len(theta) == 0:
            self.regex = r"(?!x)x"
        else:
            self.regex = r"(\b" + r"\b)|(\b".join(theta.keys()) + r"\b)"
        self.regex = re.compile(self.regex)

    def __call__(self, match):
        return self.theta[match.group()]


def substitute(expression, theta):
    subst = Substituer(theta)
    return re.sub(subst.regex, subst, expression)


def propagate_substitutions(theta):
    for key, value in theta.items():
        for var in theta:
            regex = r"\b{0}\b".format(var)
            theta[key] = re.sub(regex, theta[var], theta[key])
    return theta


def unify(expression1, expression2, theta=None):
    theta = theta or {}
    return __unify_implementation(expression1, expression2, theta)


def __unify_implementation(x, y, theta):
    if theta == problem.FAILURE: return problem.FAILURE
    elif x == y: return theta
    elif __is_variable(x): return __unify_variable(x, y, theta)
    elif __is_variable(y): return __unify_variable(y, x, theta)
    elif isinstance(x, list) and isinstance(y, list):
        head_unifier = __unify_implementation(x[0], y[0], theta)
        return __unify_implementation(x[1:], y[1:], head_unifier)

    xOperator, xOperands = __split_expression(x)
    yOperator, yOperands = __split_expression(y)

    if not xOperator or not yOperator:
        return problem.FAILURE

    unified_operators = __unify_implementation(xOperator, yOperator, theta)
    return __unify_implementation(xOperands, yOperands, unified_operators)


def __is_variable(expression):
    return isinstance(expression, str) and expression[0].islower()


def __unify_variable(var, expression, theta):
    if var in theta:
        return __unify_implementation(expression, theta[var], theta)
    if expression in theta:
        return __unify_implementation(var, theta[expression], theta)

    # Skip occur-check
    theta[var] = expression
    return theta


def unify_substitutions(theta1, theta2):
    theta = theta1.copy()
    for x in theta2:
        if x in theta1:
            subst = unify(theta1[x], theta2[x], theta)
            if subst is problem.FAILURE:
                return subst
            theta[x] = substitute(theta1[x], subst)
        else:
            theta[x] = theta2[x]

    return theta


@utils.memoize
def __split_expression(expr, cache={}):
    expr = expr.strip()
    left_index = expr.find(Braces.Left)
    if left_index == -1:
        return (None, None)
    replaced, table = Braces.replace(expr[left_index + 1: -1])
    separator = "!SEPARATOR!"
    replaced = Braces.restore(replaced.replace(", ", separator), table)
    function = expr[:left_index]
    args = replaced.split(separator)
    return (function, args)


def find_variables_symbol(expression):
    args = __split_expression(expression)[1]
    if args is None or len(args) == 0:
        return []

    firstLevel = [var for var in args
                  if __is_variable(var)]
    nestedLevels = [var
                    for expr in args
                    for var in find_variables_symbol(expr)
                    if not __is_variable(expr)]

    return firstLevel + nestedLevels


def find_variables_expression(expression):
    skolemizer = Skolemizer()
    return skolemizer.find_all_variables(expression)


def is_subsumed_by(x, y):
    """
    Returns true if y subsumes x (for example P(x) subsumes P(A) as it is more
    abstract)
    """
    varsX = __split_expression(x)[1]
    theta = unify(x, y)
    if theta is problem.FAILURE:
        return False
    return all(__is_variable(theta[var]) for var in theta.keys()
               if var in varsX)


class DefiniteClause:
    ReplacementIndex = 0

    def __init__(self, text):
        self.premises, self.conclusion = self.__parse(text)
        self.is_fact = len(self.premises) == 0

    def __parse(self, text):
        if LogicOperator.Implication in text:
            lhs, rhs = text.split(LogicOperator.Implication)

            premises = [symbol.strip() for symbol in
                        lhs.split(LogicOperator.Conjuction)]
            conclusions = [rhs.strip()]
        else:
            symbols = [symbol.strip() for symbol in
                       text.split(LogicOperator.Disjunction)]

            premises = [symbol[1:] for symbol in symbols
                        if symbol[0] == LogicOperator.Negation]
            conclusions = [symbol for symbol in symbols
                           if symbol[0] != LogicOperator.Negation]
        if len(conclusions) != 1:
            msg = "A clause must have EXACTLY one positive symbol"
            raise utils.InvalidArgumentError(msg)

        return (premises, conclusions[0])

    def standardize(self, var="x"):
        replacer = StandartizationReplacer(var)
        for index, premise in enumerate(self.premises):
            self.premises[index] = re.sub(replacer.REGEX, replacer, premise)
        self.conclusion = re.sub(replacer.REGEX, replacer, self.conclusion)

        StandartizationReplacer.GlobalIndex = replacer.index

    def __str__(self):
        return "{0} => {1}".format(" & ".join(self.premises), self.conclusion)

    __repr__ = __str__


class DefiniteKnowledgeBase:
    def __init__(self, chaining_solver, text=""):
        self.raw_kb = [DefiniteClause(clause)
                       for clause in text.strip().split("\n")
                       if len(clause) != 0]
        self.solver = chaining_solver

    def ask(self, query):
        return self.solver(self.raw_kb, query)

    def tell(self, *args):
        for sentence in args:
            self.raw_kb.append(DefiniteClause(sentence.strip()))


class KnowledgeBase:
    def __init__(self, parser, solver, text="",
                 max_clause_len=float("inf"), complete=True):
        self.parser = parser
        self.solver = solver
        self.raw_kb = parse_knowledge_base(parser, text)
        self.max_clause_len = max_clause_len
        self.complete = complete

    def ask(self, query):
        return self.solver(self.raw_kb, query,
                           self.max_clause_len,
                           self.complete)

    def tell(self, *args):
        for sentence in args:
            self.raw_kb += self.parser(sentence.strip())

    def __eq__(self, other):
        return set(self.raw_kb) == set(other.raw_kb)

    def __neq__(self, other):
        return not (self == other)


def parse_knowledge_base(parser, text):
    return [clause
            for sentence in text.strip().split("\n")
            for clause in parser(sentence)]
