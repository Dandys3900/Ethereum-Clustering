###################################
# @file Tests.py
# @author Tomáš Daniel (xdanie14)
# @brief Class for unit-tests.
###################################

# Imports
import pytest, os, io, json
from .Heuristics import HeuristicsClass
from Server.Web_Server import app
from fastapi.testclient import TestClient
from dotenv import load_dotenv

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
    clientData = await HelperClass().heuristics.api.trezor.getCurrentClientData()
    # Check blockbook is up
    assert clientData is not None

##################################################
# Load env variables
load_dotenv()
# Load stored password for DB refresh
DB_REFRESH_PWD = os.getenv("DB_REFRESH_PWD", "")

# Prepare valid test JSON
testValidJSON = {
    "newAddr" : "0X0000000000000000000000000000000000000001",
    "newValue": "MockDEX"
}

# Generic logIn function
def logIn(client):
    response = client.post("/logIn", data={
        "pwd": DB_REFRESH_PWD
    })
    assert response.get("result", "") == "success"
##################################################

def test_addAddr():
    global testValidJSON
    with TestClient(app) as mc:
        # 1. Try adding adress without being logged in
        response = mc.post("/addAdr", data=testValidJSON)
        assert response.get("result", "") == "Please logIn first"

        # 2. Try adding adress when being logged in
        logIn(mc)
        response = mc.post("/addAdr", data=testValidJSON)
        assert response.get("result", "") == "success"

        # Verify succesful addition to the list
        response = mc.post("/exchList")
        assert response.get(testValidJSON.get("newAddr", ""))

        # 3. When logged in, try to add invalid address
        # Not testable from server's POV as input is verified beforewards on client's side UI

def test_editAddr():
    global DB_REFRESH_PWD, testValidJSON
    with TestClient(app) as mc:
        # 1. Try adding adress without being logged in
        # Skip, already tested with test_addAddr()

        # 2. Try editing adress when being logged in
        logIn(mc)
        # Add it first
        mc.post("/addAdr", data=testValidJSON)
        response = mc.post("/editAdr", data=testValidJSON)
        assert response.get("result", "") == "success"

        # Verify succesful edit
        response = mc.post("/exchList")
        assert response.get(testValidJSON.get("newAddr", "")) == testValidJSON.get("newValue", "")

def test_deleteAddr():
    global DB_REFRESH_PWD, testValidJSON
    with TestClient(app) as mc:
        # 1. Try deleting adress without being logged in
        # Skip, already tested with test_addAddr()

        # 2. Try deleting adress when being logged in
        logIn(mc)
        # Try deleting non-existing address
        response = mc.post("/deleteAdr", data=testValidJSON)
        assert response.get("result", "") != "success"
        # Add it now
        mc.post("/addAdr", data=testValidJSON)
        response = mc.post("/deleteAdr", data=testValidJSON)
        assert response.get("result", "") == "success"

        # Verify succesful deletion
        response = mc.post("/exchList")
        assert response.get(testValidJSON.get("newAddr", "")) == None

def test_JSONFileOperations():
    # Create test file
    file = io.BytesIO(json.dumps({
        "0X0000000000000000000000000000000000000001": "MockDEX"
    }).encode("utf-8"))

    with TestClient(app) as mc:
        logIn(mc)
        # 1. Uploading wrong file type
        response = mc.post(
            "/uploadJSON",
            data ={"file": file},
            files={"file": ("test.txt", file, "application/crap")}
        )
        assert response.get("result", "") != "success"

        # 2. Uploading JSON with nested items + other than string literals
        badFile = io.BytesIO(json.dumps({
            "0X0000000000000000000000000000000000000001": {
                "I hate": "nested JSON"
            }
        }).encode("utf-8"))
        response = mc.post(
            "/uploadJSON",
            data ={"file": file},
            files={"file": ("test.json", badFile, "application/json")}
        )
        assert response.get("result", "") != "success"

        # 3. Uploading correct JSON file
        response = mc.post(
            "/uploadJSON",
            data ={"file": file},
            files={"file": ("test.json", file, "application/json")}
        )
        assert response.get("result", "") == "success"

        # Verify succesful append
        response = mc.post("/exchList")
        assert response.get("0X0000000000000000000000000000000000000001") == "MockDEX"
