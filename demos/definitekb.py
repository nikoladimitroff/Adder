from adder import proplogic


def main():
    kb_text = """
            Ponedelnik & Chasa_e_19 => Lekciq
            Srqda & Chasa_e_19 => Lekciq
            Stefan_v_Zalata & Kiro_v_Zalata => Kiro_Kara_Golf
            Lekciq => Kiro_Vodi
            Kiro_Vodi => Kiro_v_Zalata
            Nqma_Closure & Nqma_Conf => Stefan_v_Zalata
            Ponedelnik
            Chasa_e_19
            Nqma_Closure
            Nqma_Conf
        """

    definite_kb = proplogic.DefiniteKnowledgeBase(kb_text)
    print("Given the kb:\n", kb_text)
    print("We ask whether:\n")
    print("    Kiro_Kara_Golf?", definite_kb.ask("Kiro_Kara_Golf"))

main()
