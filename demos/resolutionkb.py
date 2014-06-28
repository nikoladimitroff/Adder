import os

from adder import proplogic

def load_kb(ir=True):
    print(ir)
    return proplogic.PlKnowledgeBase("", max_clause_len=3, information_rich=ir)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    # PL Knowledge Base
    kb = load_kb()

    example = """
        Ucha_FMI <=> (Matematik | Programist)
        Matematik <=> (Znam_DIS & !Znam_Asembler)
        Programist <=> (Znam_Python & Znam_C)
        Znam_Python
        Znam_C
    """
    told_statements = []

    print("Welcome to interactive demo for resolution based knowledge systems!")
    print("If you run out of ideas, try the following example:")
    print(example)

    while True:
        command = input()
        if command == "quit":
            break
        elif command == "help":
            available = "quit help print example clearkb clear tell ask"
            print("Available commands: ", available)

        elif command == "print":
            if len(told_statements) == 0:
                print("KB is empty!")
            else:
                print("\n".join(told_statements))
        elif command.startswith("example"):
            print(example)
            if command.endswith("load"):
                kb.tell(*example.split("\n"))
                told_statements = example.split("\n")

        elif command.startswith("clearkb"):
            kb = load_kb(ir=not command.endswith("nir"))
            told_statements.clear()
        elif command == "clear":
            clear_screen()

        elif command.startswith("tell"):
            sentence = command.split(maxsplit=1)[1] 
            kb.tell(sentence)
            told_statements.append(sentence)
        elif command.startswith("ask"):
            print(kb.ask(command.split(maxsplit=1)[1]))
        else:
            print("Unknown command")


main()