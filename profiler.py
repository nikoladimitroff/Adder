from demos import wumpus
import adder.proplogic as proplogic

import cProfile, pstats, io
import adder

def profileWumpus():
    size = 2
    agent = wumpus.HybridAgent(size)
    world = wumpus.World(size, agent)

    iterations = 1

    percept = world.update(None)

    profiler = cProfile.Profile()
    profiler.enable()

    for i in range(2):
        action = agent.update(percept)
        percept = world.update(action)
        print(percept, action, agent.position, agent.time)

    profiler.disable()

    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

def profileKB():

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

def profile():
    import sys
    sys.argv = ["profiler.py", "snake", "10"]


    profiler = cProfile.Profile()
    profiler.enable()

    import demos.snake


    profiler.disable()

    s = io.StringIO()
    sortby = "tottime"
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
    #profileWumpus()

profile()
