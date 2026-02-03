###################################
# @file Web_Server.py
# @author Tomáš Daniel (xdanie14)
# @brief Web server managing endpoints.
###################################

# Imports
import os, hashlib, secrets, json
from fastapi import FastAPI, Request, Form, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from jsonschema import validate, ValidationError
from pathlib import Path
from dotenv import load_dotenv
from Server import HeuristicsClass
from .API import TrezorAPI
from Helpers import Cache

# Load env variables
load_dotenv()
# Load stored password for DB refresh
DB_REFRESH_PWD = os.getenv("DB_REFRESH_PWD", "")

# Init FastAPI
app = FastAPI()
# Add middleware for sessions
app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))
# Absolute path to current file parent
BASE_DIR = Path(__file__).resolve().parent.parent
# Serve static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "Client" / "static")), name="static")

# Prepare template for webpage
templates = Jinja2Templates(directory="Client/templates")

# Create Heuristics class instance
heuristics = HeuristicsClass()
# Create Trezor class instance
trezor = TrezorAPI()
# Create NebulaGraph class instance
nebula = heuristics.nebula
# Flag to determine if refresh is on/off
ongoingRefresh = False

# Schema for valid JSON exch list: "str : str, ..." and no nested objects
schema = {
    "type": "object",
    "patternProperties": {
        ".*": {
            "type": ["string"]
        }
    },
    "additionalProperties": False
}

# Return context dict based on refresh status
async def getContext():
    global ongoingRefresh
    return {
        "clientData"     : await trezor.getCurrentClientData(),
        "exchLen"        : len(heuristics.exchAddrs),
        "ongoingRefresh" : ongoingRefresh,
        "addrsCount"     : {
            "exchanges" : Cache.get("exchanges_cnt"),
            "deposits"  : Cache.get("deposits_cnt"),
            "leafs"     : Cache.get("leafs_cnt")
        },
        "curBlockVals" : {
            "currentMaxBlock" : heuristics.dataHandler.maxBlock if heuristics.dataHandler.maxBlock else 0, # Get currently set highest block by user or (default) 0
            "currentMinBlock" : heuristics.dataHandler.minBlock if heuristics.dataHandler.minBlock else 0  # Get currently set highest block by user or (default) 0
        }
    }

# Throws exception when user not logged in
def requireLogIn(request):
    if not request.session.get("loggedIn", False):
        raise Exception("Please logIn first")

# Check provided pwd validity
def checkPwd(pwd):
    return (hashlib.sha512(DB_REFRESH_PWD.encode("utf-8")).hexdigest() == pwd)

# Home page
@app.get("/", response_class=HTMLResponse)
async def showHome(request: Request):
    return templates.TemplateResponse(
        request = request,
        name    = "intro.html",
        context = {
            **(await getContext()),
            "loggedIn" : request.session.get("loggedIn", False)
        }
    )

# Refresh database
@app.post("/refreshDB", response_class=JSONResponse)
async def refreshDB(request: Request, minHeight: int = Form(...), maxHeight: int = Form(...), scope: int = Form(...), pwd: str = Form(default="")):
    global ongoingRefresh

    # Omit pwd checks when already loggedIn
    if not request.session.get("loggedIn", False):
        # Check for valid refresh password
        # Raise exception to notify client
        if not checkPwd(pwd):
            raise HTTPException(status_code=401, detail="Invalid password")

    if not ongoingRefresh:
        ongoingRefresh = True
        # Trigger refresh with given scope and block limits
        await heuristics.updateAddrsDB(scope=scope, minHeight=minHeight, maxHeight=maxHeight)
        ongoingRefresh = False

    # Return new data
    return (await getContext())

# Init search
@app.post("/search", response_class=HTMLResponse)
async def searchAddr(request: Request, targetAddr: str = Form(...)):
    # Ensure capitalized search address before processing
    targetAddr = targetAddr.upper()
    # Collect addresses
    resultsGraph = await heuristics.clusterAddrs(targetAddr=targetAddr)

    # Render page
    return templates.TemplateResponse(
        request = request,
        name    = "result.html",
        context = {
            **(await getContext()),
            "targetAddr"   : targetAddr,
            "resultsGraph" : resultsGraph,
            "loggedIn"     : request.session.get("loggedIn", False)
        }
    )

# Get JSON list of crypto exchanges
@app.get("/exchList", response_class=JSONResponse)
async def getExchList():
    return heuristics.exchAddrs

# Try user to login
@app.post("/logIn", response_class=JSONResponse)
async def tryLogIn(request: Request):
    try:
        body = await request.json()
        if not checkPwd(body.get("pwd")):
            raise Exception("Invalid password")

        # Set logged in flag for user's session
        request.session["loggedIn"] = True
    except Exception as e:
        return {
            "result" : str(e)
        }
    else:
        return {
            "result" : "success"
        }

# Try user to logout
@app.post("/logOut")
async def tryLogOut(request: Request):
    if request.session.get("loggedIn", False) == True:
        request.session["loggedIn"] = False

# Edit given exchange addr from JSON list
@app.post("/addAdr", response_class=JSONResponse)
async def addExchAddr(request: Request):
    try:
        requireLogIn(request)
        body = await request.json()
        if body.get("newAddr") in heuristics.exchAddrs:
            raise KeyError("Address already included")

        # Add new entry
        heuristics.exchAddrs[body.get("newAddr")] = body.get("newValue")
    except Exception as e:
        return {
            "result" : str(e)
        }
    else:
        return {
            "result" : "success"
        }

# Edit given exchange addr from JSON list
@app.post("/editAdr", response_class=JSONResponse)
async def editExchAddr(request: Request):
    try:
        requireLogIn(request)
        body = await request.json()
        if body.get("targetAddr") not in heuristics.exchAddrs:
            raise KeyError("Invalid key")

        # Update/create new record
        heuristics.exchAddrs[body.get("newAddr")] = body.get("newValue")

        # If address (key) changed, remove previous item
        if body.get("targetAddr") != body.get("newAddr"):
            heuristics.exchAddrs.pop(body.get("targetAddr"))
    except Exception as e:
        return {
            "result" : str(e)
        }
    else:
        return {
            "result" : "success"
        }

# Delete given exchange addr from JSON list
@app.post("/deleteAdr", response_class=JSONResponse)
async def deleteExchAddr(request: Request):
    try:
        requireLogIn(request)
        body = await request.json()
        heuristics.exchAddrs.pop(body.get("targetAddr"))
    except Exception as e:
        return {
            "result" : str(e)
        }
    else:
        return {
            "result" : "success"
        }

# Upload JSON list of exchanges
@app.post("/uploadJSON", response_class=JSONResponse)
async def uploadJSON(request: Request, file: UploadFile = File(...), option: str = Form(...)):
    try:
        requireLogIn(request)
        # Only JSON files are accepted
        if not file.filename.lower().endswith(".json") or file.content_type != "application/json":
            raise Exception("Only JSON files are accepted")

        # Read uploaded file's contents
        contents = await file.read()
        data = json.loads(contents.decode("utf-8"))
        validate(instance=data, schema=schema)

        # Interact with current exch list based on selected option
        if option == "append":
            heuristics.exchAddrs.update(data)
        else: # option == "override"
            heuristics.exchAddrs = data
    except Exception as e:
        return {
            "result" : str(e)
        }
    else:
        return {
            "result" : "success"
        }
