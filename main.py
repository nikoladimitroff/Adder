from adder.enviroments import wumpus
import adder.proplogic as proplogic

import cProfile, pstats, io

def main():
    size = 3
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



if __name__ == "__main__":
    main()
