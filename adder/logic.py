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
    All = "V"
    Exists = "E"


class Braces:
    Left = "("
    Right = ")"
    Placeholder = "#"

    @staticmethod
    def remove_surrounding(sentence):
        if sentence[0] == Braces.Left and \
           sentence[-1] == Braces.Right:
            braces = 1
            for symbol in sentence[1:-1]:
                if symbol == Braces.Left:
                    braces += 1
                if symbol == Braces.Right:
                    braces -= 1
                if braces == 0:
                    return sentence
            return sentence[1:-1]
        return sentence

    @staticmethod
    def flatten(text):
        tlb = False
        braces = 0
        result = ""
        for symbol in text:
            if symbol == Braces.Left:
                if braces == 0:
                    tlb = True
                    result += Braces.Left
                braces += 1
            elif symbol == Braces.Right:
                braces -= 1
                if braces == 0:
                    tlb = False
                    result += Braces.Right
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

        replaced = re.sub("{}+".format(Braces.Placeholder),
                          Braces.Placeholder, result)
        return (replaced, replacement_table)

    @staticmethod
    def restore(text, replacement_table):
        for entry in replacement_table:
            text = text.replace("({0})".format(Braces.Placeholder), entry, 1)

        return text

class SkolemRegex:
    COMMON = r"{0} ((?:\w+, ?)*(?:\w+))\("

SkolemRegex.ALL = re.compile(SkolemRegex.COMMON.format(LogicOperator.All))
SkolemRegex.EXISTS = re.compile(SkolemRegex.COMMON.format(LogicOperator.Exists))


class Skolemizer:
    def __init__(self):
        self.constants = 0
        self.functions = 0

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
        right_end = self.__find_unbalanced(expression[left_end:])
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

    def __find_unbalanced(self, expression):
        braces = 0
        for index, symbol in enumerate(expression):
            if symbol == '(':
                braces += 1
            elif symbol == ')':
                braces -= 1
            if braces == -1:
                return index

    def __first_universal(self, expression):
        return re.search(SkolemRegex.ALL, expression)

    def __all_existenstials(self, expression):
        return re.findall(SkolemRegex.EXISTS, expression)


def skolemize(expression, skolemizer=Skolemizer()):
    return skolemizer.skolemize(expression)



class StandartizationReplacer:
    STANDARDIZE_REGEX = re.compile(r"\b[a-z][a-z0-9]*\b", re.ASCII)

    def __init__(self, var, index):
        self.var = var
        self.index = index
        self.replacements = {}

    def __call__(self, match):
        result = match.group()
        if result not in self.replacements:
            self.replacements[result] = self.var + str(self.index)
            self.index += 1

        return self.replacements[result]


def standardize_variables(expression, var="x", index={"index":0}):
    replacer=StandartizationReplacer(var, index["index"])
    index["index"] += 1
    return re.sub(replacer.STANDARDIZE_REGEX, replacer, expression)

def substitute(expression, theta):
    for key, value in theta.items():
        regex = r"\b{0}\b".format(key)
        expression = re.sub(regex, value, expression)
    return expression

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
        substitution = theta[var]
        return __unify_implementation(expression, substitution, theta)

    theta[var] = expression
    return theta

def __split_expression(expr):
    expr = expr.strip()
    left_index = expr.find(Braces.Left)
    if left_index == -1:
        return None, None
    return expr[:left_index], expr[left_index + 1:-1].split(", ")


class DefiniteClause:
    def __init__(self, text):
        self.premises, self.conclusion = self.__parse(text)
        self.is_fact = len(self.premises) == 0

    def __parse(self, text):
        text = standardize_variables(text)
        print(text)
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
