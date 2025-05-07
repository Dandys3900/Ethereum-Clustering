###################################
# @file Tests.py
# @author Tomáš Daniel (xdanie14)
# @brief Class for unit-tests.
###################################

# Imports
import pytest
from .Heuristics import HeuristicsClass
from Server.Web_Server import app
from fastapi.testclient import TestClient

class HelperClass():
    def __init__(self):
        self.heuristics = HeuristicsClass(targetSpace="MockSpace")
        # Set Nebula to interact with database
        self.nebula = self.heuristics.nebula

    # Performs clearance of address database
    def clearMockDB(self):
        # Clear existing data
        self.nebula.execNebulaCommand('CLEAR SPACE IF EXISTS MockSpace')

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
# End of HelperClass class

#################### Tests ####################
@pytest.mark.asyncio
async def test_Search():
    testHelper = HelperClass()
    # Clear test space on NebulaGraph
    testHelper.clearMockDB()
    # Fill test space with test data
    await testHelper.fillDB()

    assert (response := await testHelper.heuristics.clusterAddrs(
        targetAddr="0X0000000000000000000000000000000000000003"
    ))
    assert "0X0000000000000000000000000000000000000003" in response
    assert "0X0000000000000000000000000000000000000004" in response
    assert "0X0000000000000000000000000000000000000005" not in response

    # Cleanup
    testHelper.clearMockDB()

def test_InvalidPwd():
    with TestClient(app) as mc:
        # First, get leafs for first deposit address cluster
        response = mc.post("/refreshDB", data={
            "scope": 1,
            "pwd"  : "INVALID" # Invalid pwd
        })
        # Check correct response for invalid password
        assert response.status_code == 401

def test_NebulaInit():
    targetSpace="MockSpace"
    # Trigger creation of Nebula mock space
    nebula = (HelperClass()).nebula

    # Check all DB objects exists
    assert nebula.objectExists(targetSpace, "SPACES")
    assert nebula.objectExists("address", "TAGS")
    assert nebula.objectExists("linked_to", "EDGES")
    assert nebula.objectExists("addrs_index", "TAG INDEXES", name="Index Name")

@pytest.mark.asyncio
async def test_TrezorSyncDate():
    testHelper = HelperClass()
    syncDate = await testHelper.heuristics.api.trezor.getCurrentSyncDate()

    # Check blockbook is up
    assert syncDate != ";"
