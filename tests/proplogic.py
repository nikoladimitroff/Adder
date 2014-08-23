import os
import unittest

from adder import proplogic, utils, cnfparser

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

        self.kb = proplogic.DefiniteKnowledgeBase(implications)

    def test_fc_sample(self):
        q = proplogic.forward_chaining(self.kb.raw_kb, "Q")
        not_q = proplogic.forward_chaining(self.kb.raw_kb, "!Q")
        self.assertTrue(q)
        self.assertFalse(not_q)

    def test_bc_sample(self):
        q = proplogic.backward_chaining(self.kb.raw_kb, "Q")
        not_q = proplogic.backward_chaining(self.kb.raw_kb, "!Q")
        self.assertTrue(q)
        self.assertFalse(not_q)

    def test_kb_ask(self):
        q = self.kb.ask("Q")
        not_q = self.kb.ask("!Q")
        self.assertTrue(q)
        self.assertFalse(not_q)

    def test_kb_tell(self):
        kb = proplogic.DefiniteKnowledgeBase()
        kb.tell("A & B => C")
        kb.tell("A")
        self.assertFalse(kb.ask("C"))
        self.assertTrue(kb.ask("A"))
        kb.tell("B")
        self.assertTrue(kb.ask("C"))

    def test_failure(self):
        result_bc = proplogic.backward_chaining(self.kb.raw_kb, "T")
        result_fc = proplogic.forward_chaining(self.kb.raw_kb, "T")
        self.assertFalse(result_bc)
        self.assertFalse(result_fc)

    def test_invalid_clause(self):
        self.assertRaises(utils.InvalidArgumentError, proplogic.DefiniteClause, ("A | B"))


class CnfConverterTests(unittest.TestCase):
    def test_conversion(self):
        formula_equivalences = [
            ("!(A <=> B)", "(!A | !B) & (A | B)"),
            ("(A <=> B)", "(!A | B) & (A | !B)"),
            ("!((A <=> B) => ((A => B) & (B => A)))", "(A | B) & (!A | B) & (!B | A) & (!A | !B)"),
            ("(A <=> B) => ((A => B) & (B => A))", ""),
            ("(P & !Q) | (R & S) | (Q & R & !S)", "(P | Q | S) & (P | R) & (!Q | R)"),
            ("(A => (B & C)) => B", "A | B"),
            ("((!A | B) & (!A | C)) => B", "A | B"),
            ("!(A => (B & C))", "A & (!B | !C)"),
            ("(A => B) => C", "(A | C) & (!B | C)"),
            ("(B11 => (P12 | P21)) & ((P12 | P21) => B11)", "(!B11 | P12 | P21) & (!P12 | B11) & (!P21 | B11)"),
            ("(B11 <=> (P12 | P21))", "(!B11 | P12 | P21) & (!P12 | B11) & (!P21 | B11)"),
            ("(A | B) => C", "(!A | C) & (!B | C)")
        ]

        for formula, cnf in formula_equivalences:
            result = cnfparser.parse_propositional_sentence(formula)
            result2 = cnfparser.parse_propositional_sentence(cnf)
            expected_cnf = [{symbol.strip() for symbol in
                             conjunct.replace(")", "").replace("(", "").split("|")
                            }
                            for conjunct in cnf.split("&")
                            if len(conjunct) != 0
                           ]
            self.assertCountEqual(result, result2)
            self.assertCountEqual(result, expected_cnf)

        general_formulae = [first for first, second in formula_equivalences]
        cnfs = [second for first, second in formula_equivalences]
        from_general = proplogic.KnowledgeBase("\n".join(general_formulae))
        from_cnfs = proplogic.KnowledgeBase("\n".join(cnfs))
        self.assertEqual(from_general, from_cnfs)
        self.assertFalse(from_general != from_cnfs)

    def test_kb_parsing(self):
        formulae = [
            "(A => B | D)",
            "((A & B) => C)",
            "(C <=> !D)",
        ]
        kb = proplogic.KnowledgeBase("\n".join(formulae))
        expected = "(!A | B | D) & (!A | !B | C) & (!C | !D) & (C | D)"
        expected_cnf = cnfparser.parse_propositional_sentence(expected)
        self.assertCountEqual(kb.raw_kb, expected_cnf)

        and_concatenation = cnfparser.parse_propositional_sentence(" & ".join(formulae))
        self.assertCountEqual(kb.raw_kb, and_concatenation)


class ResolutionProverTests(unittest.TestCase):
    def test_prover_truth(self):
        # Wumpus sample, aima p.256
        #    (B11 <=> (P12 | P21)) & !B11
        formulae = "(B11 <=> (P12 | P21)) & !B11"
        kb = proplogic.KnowledgeBase(formulae)
        query = "!P12"

        result = kb.ask(query)
        self.assertTrue(result)

    def test_prover_false(self):
        # Wumpus sample, aima p.256
        formulae = "(B11 <=> (P12 | P21)) & !B11"
        kb = proplogic.KnowledgeBase(formulae)
        query = "P12"

        result = kb.ask(query)
        self.assertFalse(result)


        formulae = "A | B"
        kb = proplogic.KnowledgeBase(formulae, complete=False)
        query = "A"

        result = kb.ask(query)
        self.assertFalse(result)

    def test_tell(self):
        kb = proplogic.KnowledgeBase(complete=False)
        kb.tell("(A & !B) <=> C")
        kb.tell("A")
        self.assertFalse(kb.ask("C"))
        self.assertTrue(kb.ask("A"))
        kb.tell("!B")
        self.assertTrue(kb.ask("C"))
        self.assertFalse(kb.ask("B"))

    def test_wumpus_sample_kb(self):
        kb = proplogic.KnowledgeBase("""!Breeze_0
            WumpusAlive_0
            !Stench_0
            L11_0
            !P11
            !W11
            B11 <=> (P12 | P21)
            S11 <=> (W21 | W12)
            L11_0 => (Stench_0 <=> S11)
            L11_0 => (Breeze_0 <=> B11)
            OK12_0 <=> !P12 & (!W12 | !WumpusAlive_0)
        """, max_clause_len=3)

        self.assertTrue(kb.ask("OK12_0"))
        self.assertFalse(kb.ask("!OK12_0"))

