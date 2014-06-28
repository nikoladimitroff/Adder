import os
import unittest

from adder.graphs import Graph, Digraph, GraphLoader

import tests.config as config

class GraphFactoryTests(unittest.TestCase):
    def fill_sample_graph(self, graph):
        graph.add_edge("A", "B", 1)
        graph.add_edge("A", "C", 1)
  
    def test_digraph(self):
        dg = Digraph()
        
        self.assertTrue(len(dg.get_nodes()) == 0)
        
        self.fill_sample_graph(dg)
        
        nodes = dg.get_nodes()
        self.assertCountEqual(nodes, {"A", "B", "C" })
        
        self.assertCountEqual(dg.children_iter("A"), {"B", "C"})
        self.assertCountEqual(dg.children_iter("B"), set())
        self.assertCountEqual(dg.children_iter("C"), set())

        dg.remove_edge("A", "B")
        self.assertCountEqual(dg.children_iter("A"), {"C"})
        
    def test_graph(self):
        g = Graph()
        
        self.assertTrue(len(g.get_nodes()) == 0)
        
        self.fill_sample_graph(g)
        nodes = g.get_nodes()
        self.assertEqual(nodes, {"A", "B", "C" })
        
        self.assertCountEqual(g.children_iter("A"), {"B", "C"})
        self.assertCountEqual(g.children_iter("B"), {"A"})
        self.assertCountEqual(g.children_iter("C"), {"A"})

        g.remove_edge("A", "B")
        self.assertCountEqual(g.children_iter("A"), {"C"})
        self.assertCountEqual(g.children_iter("B"), set())
        self.assertCountEqual(g.children_iter("C"), {"A"})

    def test_iterator(self):
        g = Graph()
        self.fill_sample_graph(g)

        self.assertCountEqual(set(g), {"A", "B", "C"})
        
class GraphLoadingTests(unittest.TestCase):
    def assert_graph_loaded(self, graph, nodes, edges, is_directed=False):
        self.assertIsInstance(graph, Graph if not is_directed else Digraph)
        self.assertCountEqual(graph.get_nodes(), nodes)
        
        for source in edges:
            expected_destinations = {dest for dest, cost in edges[source]}
            self.assertCountEqual(graph.children_iter(source), expected_destinations)
            for destination, cost in edges[source]:
                self.assertEqual(graph.edge_cost(source, destination), cost)
    
    def assert_bulgaria_map_loaded(self, graph):
        cities = { 
            "Sofia", "Pernik", "Kustendil", "Dupnica", "Blagoevgrad", "Sandanski", "Kulata", "Botevgrad",
            "Vraca", "Montana", "Belogradchik", "Lom", "Vidin", "Lovech", "Pleven", "Tarnovo", "Biala", "Ruse",
            "Razgrad", "Shumen", "Dobrich", "Silistra", "Varna", "Burgas", "Iambol", "Plovdiv", "Karlovo", "StaraZagora",
            "Kazanlak", "Gabrovo", "Haskovo", "Kardzhali", "Smolian", "Pazardzhik" , "Pirdop", "Troian", "Sliven"
        }
        
        some_edges = { 
            "Sofia": {("Pernik", 28), ("Botevgrad", 64), ("Pazardzhik", 112), ("Pirdop", 80), ("Montana", 109)},
            "Pernik": {("Sofia", 28), ("Kustendil", 56), ("Dupnica", 53)},
            "Troian": {("Lovech", 34), ("Tarnovo", 97), ("Karlovo", 66), ("Pirdop", 99) },
        }
        self.assert_graph_loaded(graph, cities, some_edges)
        
    def assert_germany_map_loaded(self, graph):
        cities = { 
            "Frankfurt", "Mannheim", "Wurzburg", "Kassel", "Karlsruhe", "Augsburg",
            "Nurnberg", "Erfurt", "Munchen", "Stuttgart"
        }
        
        some_edges = { 
            "Frankfurt": {("Mannheim", 85), ("Wurzburg", 217), ("Kassel", 173)},
            "Munchen": {("Augsburg", 84), ("Nurnberg", 167), ("Kassel", 502)},
            "Erfurt": {("Wurzburg", 186)},
            "Karlsruhe": {("Mannheim", 80), ("Augsburg", 250)},
        }
        self.assert_graph_loaded(graph, cities, some_edges)
        
    def assert_romania_map_loaded(self, graph):
        cities = { 
            "Oradea", "Zerind", "Arad", "Sibiu", "RimnicuVilcea", "Timisoara", "Lugoj", "Mehadia",
            "Drobeta", "Pitesti", "Fagaras", "Bucharest", "Urziceni", "Hirsova", "Vaslui",
            "Iasi", "Neamt", "Craiova", "Giugiu", "Eforie"
        }
                
        some_edges = { 
            "Bucharest": {("Fagaras", 211), ("Giugiu", 90), ("Urziceni", 85), ("Pitesti", 101)},
            "Craiova": {("Drobeta", 120), ("Pitesti", 138), ("RimnicuVilcea", 146)},
            "Iasi": {("Neamt", 87), ("Vaslui", 92)},
        }
                    
        self.assert_graph_loaded(graph, cities, some_edges)
        
    def assert_bulgaria_disconnected_map_loaded(self, graph):
        cities = { "Pernik", "Sofia", "Kustendil", "Dupnica", "Varna", "Burgas"}
                
        some_edges = { 
            "Pernik": {("Sofia", 28)},
            "Kustendil": {("Dupnica", 41)},
            "Burgas": {("Varna", 128)},
        }

        self.assert_graph_loaded(graph, cities, some_edges)
        
    def test_graph_load_from_string(self):
        for test_name, path in config.TEST_GRAPHS.items():
            with open(path) as file:
                file_content = file.read()
            
            loader = GraphLoader()
            graph = loader.from_string(file_content)
            test_func = getattr(self, "assert_{0}_loaded".format(test_name))
            test_func(graph)
        
    def test_graph_load_from_file(self):
        for test_name, path in config.TEST_GRAPHS.items():
            loader = GraphLoader()
            graph = loader.from_file(path)
            test_func = getattr(self, "assert_{0}_loaded".format(test_name))
            test_func(graph)        


if __name__ == "__main__":
    unittest.main()