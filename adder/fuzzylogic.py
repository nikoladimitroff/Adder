import re
from itertools import groupby

from adder.logic import LogicOperator, Braces
from adder.utils import InvalidArgumentError


class FuzzySymbol:
    Equals = "is"


FuzzySymbol.EqualsRegex = re.compile(r"\b{0}\b".format(FuzzySymbol.Equals))


class FuzzyAtom:
    def __init__(self, text, swap_modalities=False):
        var, setSymbol = re.split(FuzzySymbol.EqualsRegex, text)
        var = var.strip()
        setSymbol = setSymbol.strip()

        self.var = var
        lastLeftBrace = setSymbol.rfind(Braces.Left)
        firstRightBrace = setSymbol.find(Braces.Right)
        if lastLeftBrace != -1:
            if firstRightBrace == -1:
                raise InvalidArgumentError("Unbalanced parenthesis")
            self.operators = setSymbol[:lastLeftBrace].split(Braces.Left)
            self.set = setSymbol[lastLeftBrace + 1:firstRightBrace]
        else:
            self.operators = []
            self.set = setSymbol

        if swap_modalities:
            for index, op in enumerate(self.operators):
                if op == LogicOperator.Very:
                    print("bef", self.operators[index])
                    self.operators[index] = LogicOperator.Fairly
                    print("aftr", self.operators[index])
                else:
                    self.operators[index] = LogicOperator.Very

    def __str__(self):
        return "{0} {1} {2}".format(self.var, FuzzySymbol.Equals, self.set)


class FuzzyRule:
    def __init__(self, rule_text):
        premises, conclusion = rule_text.split(LogicOperator.Implication)
        regex = r"{0}|{1}".format(re.escape(LogicOperator.Conjuction),
                                  re.escape(LogicOperator.Disjunction))

        operators = re.findall(regex, premises)
        premises = [FuzzyAtom(premise)
                    for premise in re.split(regex, premises)]
        conclusion = FuzzyAtom(conclusion, swap_modalities=True)

        self.premises = premises
        self.operators = operators
        self.conclusion = conclusion


class KnowledgeBase:
    def __init__(self, rules, variable_info, max_values, accuracy=10):
        self.rules = [FuzzyRule(line.strip())
                      for line in rules.strip().splitlines()]
        self.max_values = max_values
        self.vars = {var: dict(fuzzy_sets)
                     for var, fuzzy_sets in variable_info.items()}
        self.accuracy = accuracy

    def ask(self, query):
        return answer_query(self, query, self.accuracy)


def answer_query(kb, query, accuracy):
    # query = ({ "distance": 50, "profession": "warrior" }, "fighting_will")
    values, var = query
    fuzzified = [compute_rule_value(kb, rule, values)
                 for rule in fetch_rules(kb, var)]
    get_set = lambda fuzzy_value: fuzzy_value[1]
    sorted_data = sorted(fuzzified, key=get_set)
    per_set_max = {}
    for fuzzy_set, group in groupby(sorted_data, key=get_set):
        group = list(group)
        per_set_max[fuzzy_set] = max(group)[0]

    def manifold(x):
        set_maximums = (min(kb.vars[var][fuzzy_set](x), set_max)
                        for fuzzy_set, set_max in per_set_max.items())
        return sum(set_maximums)

    step = kb.max_values[var] / accuracy
    samples = [x * step for x in range(accuracy + 1)]
    sample_values = list(map(manifold, samples))
    numerator = sum(s * dom_s for s, dom_s in zip(samples, sample_values))
    denomerator = sum(sample_values)
    return numerator / denomerator


def fetch_rules(kb, var):
    return [rule for rule in kb.rules
            if rule.conclusion.set in kb.vars[var]]


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


def evaluate_atom(kb, atom, values):
    return kb.vars[atom.var][atom.set](values[atom.var])


def compute_rule_value(kb, rule, values):
    first_atom = rule.premises[0]
    first_value = evaluate_atom(kb, first_atom, values)
    result = evaluate_modality(first_atom, first_value)
    for index, operator in enumerate(rule.operators):
        func = __EVALUATORS[operator]
        atom = rule.premises[index + 1]
        value = evaluate_atom(kb, atom, values)
        result = func(result, evaluate_modality(atom, value))

    return evaluate_modality(rule.conclusion, result), rule.conclusion.set


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
