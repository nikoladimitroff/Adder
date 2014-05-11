from collections import defaultdict
import re

class Digraph:
    def __init__(self):
        self.__edges = defaultdict(set)
        self.__edge_costs = dict()
        
    def get_nodes(self):
        nodes = set(self.__edges.keys())
        for edge in self.__edges.values():
            for dest in edge:
                nodes.add(dest)
        
        return nodes
        
    @property
    def edges(self):
        return self.__edges
    
    def edge_cost(self, source, destination):
        return self.__edge_costs[(source, destination)]
        
    def add_edge(self, source, destination, cost):    
        self.__edges[source].add(destination)
        self.__edge_costs[(source, destination)] = cost
        
    def remove_edge(self, source, destination):
        self.__edges[source].remove(destination)
        self.__edge_costs.pop((source, destination))
        

class Graph(Digraph):

    def add_edge(self, source, destination, cost):
        Digraph.add_edge(self, source, destination, cost)
        Digraph.add_edge(self, destination, source, cost)
        
    def remove_edge(self, source, destination):
        Digraph.remove_edge(self, source, destination)
        Digraph.remove_edge(self, destination, source)
        
class GraphLoader:
    DIRECTED_EDGE_SEPARATOR = "->"
    BIDIRECTED_EDGE_SEPARATOR = "<->"
    COMMENT = "#"
    
    def from_string(self, text):
        edges = set()
        is_graph_bidirected = True
        for line in text.split("\n"):
            # skip comments and empty lines
            if line.startswith(GraphLoader.COMMENT) or len(line.strip()) == 0: continue
            # if the line is in the form "source <->" there are no destinations, skip it
            if re.match(line, r"\w*\s*<->\s*"): continue
            
            is_line_bidirected = GraphLoader.BIDIRECTED_EDGE_SEPARATOR in line
            is_graph_bidirected = is_graph_bidirected and is_line_bidirected
            separator = GraphLoader.BIDIRECTED_EDGE_SEPARATOR if is_line_bidirected else GraphLoader.DIRECTED_EDGE_SEPARATOR
            
            parts = line.split(separator)
            source = parts[0].strip()
            # split the right side of the separator by commas. Split each CSV by space.
            # the first part is the destination, the second is the cost
            destinations = [(edge.split()[0], float(edge.split()[1])) for edge in parts[1].split(",")
                            if len(edge.strip()) != 0] 
            for destination, cost in destinations:
                edges.add((source, destination, cost))
                if is_line_bidirected:
                    edges.add((destination, source, cost))
        
        graph = Graph() if is_graph_bidirected else Digraph()
        for source, dest, cost in edges:
            graph.add_edge(source, dest, cost)
        
        return graph
        
    def from_file(self, path):
        with open(path) as file:
            return self.from_string(file.read())