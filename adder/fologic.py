import re

from adder import problem
from adder.logic import *


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
