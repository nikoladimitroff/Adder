import re

class LogicOperator:
    Conjuction = "&"
    Disjunction = "|"
    Negation = "!"
    Implication = "=>"
    Equivalence = "<=>"


class Braces:
    Left = "("
    Right = ")"
    Placeholder = "*"
    
    @staticmethod
    def remove_surrounding_parenthesis(sentence):
        if sentence[0] == Braces.Left and \
           sentence[-1] == Braces.Right:
            braces = 1
            for symbol in sentence[1:-1]:
                if symbol == Braces.Left: braces += 1
                if symbol == Braces.Right: braces -= 1
                if braces == 0: return sentence
            return sentence[1:-1]
        return sentence
    
    @staticmethod
    def flatten_braces(text):
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
    def brace_replace(text):
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

        return (re.sub("\*+", Braces.Placeholder, result), replacement_table)
    
    @staticmethod
    def restore_braces(text, replacement_table):
        for entry in replacement_table:
            text = text.replace("({0})".format(Braces.Placeholder), entry, 1)
    
        return text
