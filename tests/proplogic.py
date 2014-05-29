# Depends on: adder
from adder import proplogic
import os
import unittest

import tests.config as config

class DefiniteClausesTests(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)

        implications = """A
                B
                L & M => P
                B & L => M
                A & P => L
                A & B => L
                P => Q
        """

        self.kb = proplogic.parse_definite_clauses(implications)

    def test_parsing_kb(self):
        dnf = """A
                B
                !L | !M | P
                !B | !L | M
                !A | !P | L
                !A | !B | L
                !P | Q
        """
        
        parsed_dnf = proplogic.parse_definite_clauses(dnf)
        self.assertEqual(parsed_dnf, self.kb)

    def test_fc_sample(self):
        result = proplogic.forward_chaining(self.kb, "Q")
        self.assertTrue(result)

        
    def test_bs_sample(self):
        result = proplogic.backward_chaining(self.kb, "Q")
        self.assertTrue(result)

    def test_failure(self):
        result_bc = proplogic.backward_chaining(self.kb, "T")
        result_fc = proplogic.forward_chaining(self.kb, "T")
        self.assertFalse(result_bc)
        self.assertFalse(result_fc)


class CnfConverterTests(unittest.TestCase):
    def test_conversion(self):
        formula_equivalences = [
            ("!(A <=> B)", "(!A | !B) & (A | B)"),
            ("(A <=> B)", "(!A | B) & (A | !B)"),
            #("(A <=> B) => ((A => B) & (B => A))", "A | B | !A | !B"),
            #("(P & !Q) | (R & S) | (Q & R & !S)", "(P | Q | S) & (P | R) & (!Q | R)"),
            ("A => (B & C) => B", "A | B"),
            ("(B11 => (P12 | P21)) & ((P12 | P21) => B11)", "(!B11 | P12 | P21) & (!P12 | B11) & (!P21 | B11)"),
            ("(A | B) => C", "(!A | C) & (!B | C)")
        ]

        for formula, cnf in formula_equivalences:
            result = proplogic.parse_cnf_clause(formula)
            result2 = proplogic.parse_cnf_clause(cnf)
            expected_cnf = [{symbol.strip() for symbol in 
                             disjunct.replace(")", "").replace("(", "").split("|")
                             }
                            for disjunct in cnf.split("&")
                            ]
            print(proplogic.print_cnf_clause(result), "\n", proplogic.print_cnf_clause(result2))
            self.assertCountEqual(result, result2)
            self.assertCountEqual(result, expected_cnf)

    def test_is_operator(self):
        formula_equivalences = [
            ("(A <=> B) => ((A => B) & (B => A))", "=>"),
            ("(P | !Q) | (R & S) | (Q & R & !S)", "|"),
            ('!(P12 | P21) | B11', "|"),
            ("A => B & C => B", "=>"),
            ("(A => B) <=> (C => B)", "<=>"),
            ("!(A => B <=> (C => B))", "!")
        ]

        for formula, operator in formula_equivalences:
            parsed = proplogic.parse_sentence(formula)
            result_operator = parsed[0]
            self.assertEqual(result_operator, operator, msg="{}/{}".format(formula, operator))

    def test_is_not_operator(self):
        formula_lies = [
            ("(A <=> B) => ((A => B) & (B => A))", "&"),
            ("(A <=> B) => ((A => B) & (B => A))", "<=>"),
            ("(P & !Q) | (R & S) | (Q & R & !S)", "!"),
            ("(A => B) <=> (C => B)", "=>")
        ]
        for formula, operator in formula_lies:
            parsed = proplogic.parse_sentence(formula)
            result_operator = parsed[0]
            self.assertNotEqual(result_operator, operator, msg="{}/{}".format(formula, operator))

