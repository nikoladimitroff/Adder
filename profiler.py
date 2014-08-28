from demos import wumpus
import adder.proplogic as proplogic

import cProfile
import pstats
import io
import adder
from adder import fologic


def profile_prop_kb():

    pl_kb = proplogic.KnowledgeBase("""
        Ucha_FMI <=> (Matematik | Programist)
        Matematik => (Znam_DIS & !Znam_Asembler)
        Programist <=> (Znam_Python & Znam_C)
        Programist2 <=> (Znam_Python & Znam_C)
        Programist3 <=> (Znam_Python & Znam_C)
        Programist4 <=> (Znam_Python & Znam_C)
        Programist5 <=> (Znam_Python & Znam_C)
        Programist6 <=> (Znam_Python & Znam_C)
        Programist7 <=> (Znam_Python & Znam_C)
        Programist8 <=> (Znam_Python & Znam_C)
        Programist9 <=> (Znam_Python & Znam_C)
        Programist10 <=> (Znam_Python & Znam_C)
        Programist11 <=> (Znam_Python & Znam_C)
    #""", max_clause_len=3)

    pl_kb.tell("Znam_Python")
    pl_kb.tell("Znam_C")

    profiler = cProfile.Profile()
    profiler.enable()
    print(pl_kb.ask("!Ucha_FMI"))
    print(pl_kb.ask("Ucha_FMI"))
    profiler.disable()

    s = io.StringIO()
    sortby = "tottime"
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())


def profile_fo_definite_kb():
    kb = fologic.DefiniteKnowledgeBase("""


    """)

    kb.ask()


def profile_fo_resolution():
    kb = fologic.KnowledgeBase("""
        V x(American(x) & Weapon(y) & Sells(x, y, z) & Hostile(z) => Criminal(x))
        Owns(Nono, M1)
        Missile(M1)
        V x(Missile(x) & Owns(Nono, x) => Sells(West, x, Nono))
        V x(Missile(x) => Weapon(x))
        V x(Enemy(x, America) => Hostile(x))
        American(West)
        Enemy(Nono, America)
    """, 5, True)

    print("Is West the criminal?", kb.ask("Criminal(West)"))
    print("Who's the criminal?", kb.ask("E x(Criminal(x))"))
    print("Who's there a noncriminal?", kb.ask("E x(!Criminal(x))"))

    kb = fologic.KnowledgeBase("""
        V x(V y(Animal(y) => Loves(x, y)) => E z(Loves(z, x)))
        V x(E y(Animal(y) & Kills(x, y)) => V z(!Loves(z, x)))
        V x(Animal(x) => Loves(x, Jack))
        Cat(Tuna)
        Kills(Jack, Tuna) | Kills(Curiosity, Tuna)
        V x(Cat(x) => Animal(x))
    """, 3, True)

    print("Did Curiosity kill Tuna?", kb.ask("Kills(Curiosity, Tuna)"))
    print("Did Curiosity NOT kill Tuna?", kb.ask("!Kills(Curiosity, Tuna)"))
    print("Did Jack Kill Tuna?", kb.ask("Kills(Jack, Tuna)"))
    print("Did Jack NOT kill Tuna?", kb.ask("!Kills(Jack, Tuna)"))
    print("Who killed Tuna?", kb.ask("E x(Kills(x, Tuna))"))
    print("Did Jack kill something?", kb.ask("E x(Kills(Jack, x))"))
    print("Did Curisity kill something?", kb.ask("E x(Kills(Curiosity, x))"))
    print("Is there a cat?", kb.ask("E x(Cat(x))"))
    print("Is anyone loved by all animals?", kb.ask("E x(V y(Animal(y)) => Loves(y, x))"))
    print("Did anyone kill anything?", kb.ask("E x,y(Kills(x, y))"))


def profile():
    import sys
    sys.argv = ["profiler.py", "snake", "10"]

    profiler = cProfile.Profile()
    profiler.enable()

    profile_fo_resolution()

    profiler.disable()

    s = io.StringIO()
    sortby = "tottime"
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

profile()
