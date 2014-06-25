from adder.enviroments import wumpus
import adder.proplogic as proplogic

import cProfile, pstats, io

def profileWumpus():
    size = 2
    world = wumpus.World(size)
    #agent = wumpus.HybridAgent(size)
    

    iterations = 1
    
    percept = world.update(None)
    agents = [wumpus.HybridAgent(size) for i in range(iterations)]


    profiler = cProfile.Profile()
    profiler.enable()
    for agent in agents:
        action = agent.update(percept)
        print(action)
    profiler.disable()

    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

def profileKB():
    
    pl_kb = proplogic.PlKnowledgeBase("""
        Ucha_FMI <=> (Matematik | Programist)
        Matematik => (Znam_DIS & !Znam_Asembler)
        Programist <=> (Znam_Python & Znam_C)
        """)
    #    Programist2 <=> (Znam_Python & Znam_C)
    #    Programist3 <=> (Znam_Python & Znam_C)
    #    Programist4 <=> (Znam_Python & Znam_C)
    #    Programist5 <=> (Znam_Python & Znam_C)
    #    Programist6 <=> (Znam_Python & Znam_C)
    #    Programist7 <=> (Znam_Python & Znam_C)
    #    Programist8 <=> (Znam_Python & Znam_C)
    #    Programist9 <=> (Znam_Python & Znam_C)
    #    Programist10 <=> (Znam_Python & Znam_C)
    #    Programist11 <=> (Znam_Python & Znam_C)
    #""")

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


def profile():
    profileWumpus()

profile()