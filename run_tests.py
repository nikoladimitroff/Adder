from tests.graphs import GraphFactoryTests

import unittest

from adder import graphs
from adder import search
from tests import config


loader = graphs.GraphLoader()
graph = loader.from_file(config.TEST_DATA["germany_map"])
search.bfs(graph, "Frankfurt")


if __name__ == "__main__":
    unittest.main()