# Class for unittests
# Imports
import pytest
from .API import NebulaAPI
from .Heuristics import HeuristicsClass
from Server.Web_Server import app,heuristics
from fastapi.testclient import TestClient

class TestsClass():
    def __init__(self):
        self.heuristics = HeuristicsClass(targetSpace="MockSpace")
        # Set Nebula to interact with database
        self.nebula = self.heuristics.nebula

    # Performs clearance of address database
    def clearMockDB(self):
        # Clear existing data
        self.nebula.ExecNebulaCommand('CLEAR SPACE IF EXISTS MockSpace')

    # Fill database with test data
    async def fillDB(self):
        ######## Add one exchange address ########
        await self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000000",
            "mock exchange",
            nodeType="exchange"
        )
        ######## Add two deposit addresses ########
        await self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000001",
            "mock deposit 1",
            parentAddr="0X0000000000000000000000000000000000000000",
            nodeType="deposit"
        )
        await self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000002",
            "mock deposit 2",
            parentAddr="0X0000000000000000000000000000000000000000",
            nodeType="deposit"
        )
        ######## Add four leaf addresses - two for each deposit ########
        await self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000003",
            "mock leaf 1",
            parentAddr="0X0000000000000000000000000000000000000001",
            nodeType="leaf"
        )
        await self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000004",
            "mock leaf 2",
            parentAddr="0X0000000000000000000000000000000000000001",
            nodeType="leaf"
        )
        await self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000005",
            "mock leaf 3",
            parentAddr="0X0000000000000000000000000000000000000002",
            nodeType="leaf"
        )
        await self.nebula.addNodeToGraph(
            "0X0000000000000000000000000000000000000006",
            "mock leaf 4",
            parentAddr="0X0000000000000000000000000000000000000002",
            nodeType="leaf"
        )
# End of TestsClass class

#################### Tests ####################
@pytest.mark.asyncio
async def test_SearchEndpoint():
    testHelper = TestsClass()
    # Clear test space on NebulaGraph
    testHelper.clearMockDB()
    # Fill test space with test data
    await testHelper.fillDB()

    with TestClient(app) as mc:
        # First, get leafs for first deposit address cluster
        response = mc.get("/search", params={
            "targetAddr": "0X0000000000000000000000000000000000000003"
        })

    assert response.status_code == 200
    assert "0X0000000000000000000000000000000000000003" in response.text
    assert "0X0000000000000000000000000000000000000004" in response.text
    assert "0X0000000000000000000000000000000000000005" not in response.text
