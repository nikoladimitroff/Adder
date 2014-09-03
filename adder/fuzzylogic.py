import re

from adder.logic import LogicOperator, Braces
from adder.utils import InvalidArgumentError


class FuzzySymbol:
    Equals = "is"


class FuzzyAtom:
    def __init__(self, text, swap_modalities=False):
        var, setSymbol = text.split(FuzzySymbol.Equals)
        self.var = var
        lastLeftBrace = setSymbol.find(Braces.Left)
        firstRightBrace = setSymbol.find(Braces.Right)
        if lastLeftBrace != -1:
            if firstRightBrace == -1:
                raise InvalidArgumentError("Unbalanced parenthesis")
            self.operators = setSymbol[:lastLeftBrace].split(Braces.Left)
            self.set = setSymbol[lastLeftBrace:firstRightBrace]
        else:
            self.operators = []
            self.set = setSymbol

        if swap_modalities:
            for index, op in self.operators:
                if op is LogicOperator.Very:
                    self.operators[index] = LogicOperator.Fairly
                else:
                    self.operators[index] = LogicOperator.Very


class FuzyRule:
    def __init__(self, rule_text):
        premises, conclusion = query.split(LogicOperator.Implication)
        regex = r"\b({0}|{1})\b".format(re.escape(LogicOperator.Conjuction),
                                        re.escape(LogicOperator.Disjunction))

        operators = re.findall(regex, premises)
        premises = [FuzzyAtom(premise)
                    for premise in re.split(regex, premises)]
        conclusion = FuzzyAtom(conclusion, swap_modalities=True)

        self.premises = premises
        self.operators = operators
        self.conclussion = conclusion


class KnowledgeBase:
    def __init__(self, rules, variable_info):
        self.rules = [FuzzyRule(line.strip()) for line in rules.strip()]
        self.max_values = {info[0]: info[2] for info in variable_info}
        self.vars = {info[0]: info[1] for info in variable_info}

    def ask(self, query):
        return answer_query(self, query, 10)


# distance = close & profession = warrior => very(Fightable)
def create_variable(variable, fuzzy_sets, max_value):
    return (variable, fuzzy_sets, max_value)


def answer_query(kb, query, accuracy):
    #query = ({ "distance": 50, "profession": "warrior" }, "fighting_will")
    values, var = query
    fuzzified = [compute_rule_value(kb, rule, values)
                 for rule in fetch_rules(kb, var)]
    get_set = lambda fuzzy_value: fuzzy_value[1]
    sorted_data = sorted(fuzzified, get_set)
    per_set_max = {}
    for fuzzy_set, group in groupby(sorted_data, get_set):
        per_set_max[fuzzy_set] = max(group)

    def manifold(x):
        set_maximums = (max(kb.vars[var][fuzzy_set](x), set_max)
                        for fuzzy_set, set_max in per_set_max.items())
        return max(set_maximums)

    samples = list(range(0, kb.max_values[var], 1 / accuracy))
    sample_values = list(map(manifold, samples))
    numerator = sum(s * dom_s for s, dom_s in zip(samples, sample_values))
    denomerator = sum(sample_values)
    return numerator / denomerator


def fetch_rules(kb, var):
    return [rule for rule in kb.rules
            if rule.conclusion.set in kb.variables[var]]


__EVALUATORS = {
    LogicOperator.Conjuction: min,
    LogicOperator.Disjunction: max,
    LogicOperator.Very: lambda x: x**2,
    LogicOperator.Fairly: lambda x: x**0.5,
}


def evaluate_modality(atom, dom):
    for operator in reversed(atom.operators):
        dom = __EVALUATORS[operator](dom)
    return dom


def compute_rule_value(kb, values, rule):
    result = evaluate_modality(rule.premises[0], values)
    for index, operator in enumerate(rule.operators):
        func = __EVALUATORS[operator]
        value = kb.vars[atom.var][atom.set](values[atom.var])
        result = func(result,
                      evaluate_modality(rule.premises[i + 1], value))

    return evaluate_modality(kb, conclusion, result), conclusion.set


class TriangleSet:
    def __init__(self, left, peak, right):
        self.left = left
        self.peak = peak
        self.right = right

    def __call__(self, x):
        if x <= self.peak and x >= self.left:
            gradient = 1 / (self.peak - self.left)
            return gradient * (x - self.left)
        elif x > self.peak and x <= self.right:
            gradient = 1 / (self.right - self.peak)
            return gradient * (self.right - x)

        return 0


class ShoulderSet:
    def __init__(self, peak, base):
        self.peak = peak
        self.base = base
        self.is_right = peak - base > 0

    def __call__(self, x):
        if self.is_right:
            if x < self.peak and x >= self.base:
                gradient = 1 / (self.peak - self.base)
                return gradient * (x - self.base)
            elif x >= self.peak:
                return 1
            return 0
        else:
            if x > self.peak and x <= self.base:
                gradient = 1 / (self.base - self.peak)
                return gradient * (self.base - x)
            elif x <= self.peak:
                return 1
            return 0


class MembershipSets:
    triangle = TriangleSet
    shoulder = ShoulderSet
