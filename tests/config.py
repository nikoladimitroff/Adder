import os

TEST_GRAPHS = {
    "Bulgaria_map": os.path.join(os.path.dirname(__file__), "../data/bulgaria.graph"),
    "Bulgaria_disconnected_map": os.path.join(os.path.dirname(__file__), "../data/bulgaria_disconnected.graph"),
    "germany_map": os.path.join(os.path.dirname(__file__), "../data/germany.graph"),
    "romania_map": os.path.join(os.path.dirname(__file__), "../data/romania.graph")
}

HARD_TESTS = False
