from adder import graphs
import os
import unittest

class GraphFactoryTests(unittest.TestCase):
    def __init__(self, *args):
    
        unittest.TestCase.__init__(self, *args)
        self.bulgaria_map_path = os.path.join(os.path.dirname(__file__), "../data/bulgaria.graph")

    def fill_sample_graph(self, graph):
        graph.add_edge("A", "B", 1)
        graph.add_edge("A", "C", 1)
  
    def test_digraph_constructor(self):
        dg = graphs.Digraph()
        
        self.assertTrue(len(dg.get_nodes()) == 0)
        
        self.fill_sample_graph(dg)
        
        nodes = dg.get_nodes()
        self.assertSetEqual(nodes, {"A", "B", "C" })
        
        self.assertSetEqual(dg.edges["A"], {"B", "C"})
        self.assertSetEqual(dg.edges["B"], set())
        self.assertSetEqual(dg.edges["C"], set())
        
    def test_graph_constructor(self):
        g = graphs.Graph()
        
        self.assertTrue(len(g.get_nodes()) == 0)
        
        self.fill_sample_graph(g)
        nodes = g.get_nodes()
        self.assertEqual(nodes, {"A", "B", "C" })
        
        self.assertSetEqual(g.edges["A"], {"B", "C"})
        self.assertSetEqual(g.edges["B"], {"A"})
        self.assertSetEqual(g.edges["C"], {"A"})
        
    def assert_bulgaria_map_loaded(self, graph):
        self.assertIsInstance(graph, graphs.Graph)
        cities = { "Sofia", "Pernik", "Kustendil", "Dupnica", "Blagoevgrad", "Sandanski", "Kulata", "Botevgrad",
            "Vraca", "Montana", "Belogradchik", "Lom", "Vidin", "Lovech", "Pleven", "Tarnovo", "Biala", "Ruse",
            "Razgrad", "Shumen", "Dobrich", "Silistra", "Varna", "Burgas", "Iambol", "Plovdiv", "Karlovo", "StaraZagora",
            "Kazanlak", "Gabrovo", "Haskovo", "Kardzhali", "Smolian", "Pazardzhik" , "Pirdop", "Troian", "Sliven"
        }
        
        self.assertSetEqual(graph.get_nodes(), cities)
        some_edges = { "Sofia": {("Pernik", 28), ("Botevgrad", 64), ("Pazardzhik", 112), ("Pirdop", 80), ("Montana", 109)},
                        "Pernik": {("Sofia", 28), ("Kustendil", 56), ("Dupnica", 53)},
                        "Troian": {("Lovech", 34), ("Tarnovo", 97), ("Karlovo", 66), ("Pirdop", 99) },
                    }
                    
        for source in some_edges:
            self.assertSetEqual(graph.edges[source], {dest for dest, cost in some_edges[source]})
            for destination, cost in some_edges[source]:
                self.assertEqual(graph.edge_cost(source, destination), cost)
        
    def test_graph_load_from_string(self):
        with open(self.bulgaria_map_path) as file:
            file_content = file.read()
        
        loader = graphs.GraphLoader()
        graph = loader.from_string(file_content)
        self.assert_bulgaria_map_loaded(graph)
        
    def test_graph_load_from_file(self):
        loader = graphs.GraphLoader()
        graph = loader.from_file(self.bulgaria_map_path)
        self.assert_bulgaria_map_loaded(graph)
        
        
if __name__ == "__main__":
    unittest.main()