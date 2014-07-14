import re
from collections import defaultdict
from functools import partial

from adder import problem
from adder.logic import Braces, LogicOperator
from adder.utils import ParsingError

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
            
    

class _StandartizationReplacer:
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


def standardize_variables(expression, standard_var="x", index=0):
    replacer = _StandartizationReplacer(standard_var, index)
    return re.sub(replacer.STANDARDIZE_REGEX, replacer, expression)

def unify(expression1, expression2):
    return __unify_implementation(expression1, expression2, {})

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
