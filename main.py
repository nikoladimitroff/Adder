from adder.enviroments import wumpus
import adder.proplogic as proplogic

def main():
    size = 3
    world = wumpus.World(size)
    agent = wumpus.HybridAgent(size)
    
    action, percept = None, None
    for i in range(20):
        percept = world.update(action)
        action = agent.update(percept)



if __name__ == "__main__":
    main()
