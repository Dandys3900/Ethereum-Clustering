# Class for unittests
# Imports
import time, unittest
from .API import NebulaAPI
from .Heuristics import HeuristicsClass
from Server.Web_Server import app,heuristics
from fastapi.testclient import TestClient

class TestsClass(unittest.TestCase):
    def setUp(self):
        self.heuristics = HeuristicsClass()
        # Init Nebula to interact with database
        self.nebula = NebulaAPI()
        # Make sure space is created
        self.nebula.createSpace("MockSpace")

    # Performs clearance of address database
    def recreateDB(self):
        # Clear existing data
        self.nebula.ExecNebulaCommand('CLEAR SPACE IF EXISTS MockSpace')

        # Use defined space
        self.nebula.ExecNebulaCommand('USE MockSpace')

        # Sleep 20 seconds to ensure tags and edges are created
        time.sleep(20)

    # Fill database with test data
    def fillDB(self):
        ######## Add one exchange address ########
        self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000000",
            "mock exchange",
            nodeType="exchange"
        )
        ######## Add two deposit addresses ########
        self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000001",
            "mock deposit 1",
            parentAddr="0X0000000000000000000000000000000000000000",
            nodeType="deposit"
        )
        self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000002",
            "mock deposit 2",
            parentAddr="0X0000000000000000000000000000000000000000",
            nodeType="deposit"
        )
        ######## Add four leaf addresses - two for each deposit ########
        self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000003",
            "mock leaf 1",
            parentAddr="0X0000000000000000000000000000000000000001",
            nodeType="leaf"
        )
        self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000004",
            "mock leaf 2",
            parentAddr="0X0000000000000000000000000000000000000001",
            nodeType="leaf"
        )
        self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000005",
            "mock leaf 3",
            parentAddr="0X0000000000000000000000000000000000000002",
            nodeType="leaf"
        )
        self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000006",
            "mock leaf 4",
            parentAddr="0X0000000000000000000000000000000000000002",
            nodeType="leaf"
        )

    #################### Tests ####################
    def test_SearchEndpoint(self):
        # Clear test space on NebulaGraph
        self.recreateDB()
        # Fill test space with test data
        self.fillDB()
        # Switch to Nebula test space
        heuristics.setNebulaSpace("MockSpace")

        with TestClient(app) as mc:
            # First, get leafs for first deposit address cluster
            response = mc.get("/search", params={
                "targetAddr": "0X0000000000000000000000000000000000000003"
            })

        self.assertEqual(response.status_code, 200)
        self.assertIn("0X0000000000000000000000000000000000000005", response.text)
        self.assertIn("0X0000000000000000000000000000000000000004", response.text)
# End of TestsClass class
