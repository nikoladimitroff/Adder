import re

from adder import problem
from adder.logic import Braces, LogicOperator
from adder.utils import ParsingError

def skolemize(expression):
    expression = "E x, y(P(x, y)) | V p, q(S(p, q) <=> E r(r) & E y,z(y == z) & x) & E x(x | V y(y))"
    print(__build_skolem_tree(expression))
	
def __build_skolem_tree(expression, root=None):
    universal = __first_universal(expression)
    print("EXPR: ", expression)
    if not universal:
        return {root: __all_existenstials(expression)}
    else:
        left_end = universal.span()[1]
        right_end = __find_right_index(expression[left_end:])
        if not right_end:
            raise ParsingError("Unbalanced parenthesis")
        right_end += left_end
        
        left = expression[:universal.span()[0]]
        middle = expression[left_end:right_end]
        right = expression[right_end:]
        
        left_tree = __build_skolem_tree(left, root)
        middle_tree = __build_skolem_tree(middle, universal.group(1))
        right_tree = __build_skolem_tree(right, root)
        return {root: left_tree[root] + [middle_tree] + right_tree[root]}
        
        
    print(universal)
    
def __find_right_index(expression):
    braces = 0
    for index, symbol in enumerate(expression):
        if symbol == '(':
            braces += 1
        elif symbol == ')':
            braces -= 1
        if braces == -1:
            return index

def __first_universal(expression):
    common_regex = r"{0} ((?:\w+, ?)*(?:\w+))\("
    uni_regex = common_regex.format(LogicOperator.All)
    exists_regex = common_regex.format(LogicOperator.Exists)
    
    return re.search(uni_regex, expression)

def __all_existenstials(expression):
    common_regex = r"{0} ((?:\w+, ?)*(?:\w+))\("
    uni_regex = common_regex.format(LogicOperator.All)
    exists_regex = common_regex.format(LogicOperator.Exists)
    
    return re.findall(exists_regex, expression)
    


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
