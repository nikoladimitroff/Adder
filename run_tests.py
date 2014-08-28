from tests.graphs import GraphFactoryTests
from tests.graphs import GraphLoadingTests
from tests.graphs import GraphLoadingTests
from tests.search import BfsTests
from tests.search import DlsTests
from tests.search import AStarTests
from tests.search import AStarNPuzzleTests
from tests.search import HillClimbingQueensTests
from tests.search import SimulatedAnnealingTests
from tests.search import GeneticTests
from tests.problems import NQueensTest
from tests.proplogic import DefiniteClausesTests
from tests.proplogic import CnfConverterTests
from tests.proplogic import ResolutionProverTests
from tests.fologic import HelperTests
from tests.fologic import ChainingTests
from tests.fologic import CnfTests
from tests.fologic import ResolutionTests

from tests import config

import unittest


if __name__ == "__main__":
    config.HARD_TESTS = False

    unittest.main()
