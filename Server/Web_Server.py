###################################
# @file Web_Server.py
# @author Tomáš Daniel (xdanie14)
# @brief Web server managing endpoints.
###################################

# Imports
import os
import hashlib
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
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

# Return conext dict based on refresh status
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
            "currentMaxBlock" : heuristics.dataHandler.maxBlock if heuristics.dataHandler.maxBlock else trezor.heighestBlock, # Get currently set highest block by user or client's highest
            "currentMinBlock" : heuristics.dataHandler.minBlock if heuristics.dataHandler.minBlock else 0                     # Get currently set highest block by user or (default) 0
        }
    }

# Home page
@app.get("/", response_class=HTMLResponse)
async def showHome(request: Request):
    return templates.TemplateResponse(
        request = request,
        name    = "intro.html",
        context = await getContext()
    )

# Refresh database
@app.post("/refreshDB", response_class=JSONResponse)
async def refreshDB(minHeight: int = Form(...), maxHeight: int = Form(...), scope: int = Form(...), pwd: str = Form(...)):
    global ongoingRefresh

    # Check for valid refresh password
    correctPwd = (hashlib.sha512(DB_REFRESH_PWD.encode("utf-8")).hexdigest() == pwd)
    # Raise exception to notify client
    if not correctPwd:
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
            "resultsGraph" : resultsGraph
        }
    )

# Get JSON list of crypto exchanges
@app.get("/exchList", response_class=JSONResponse)
async def getExchList():
    return heuristics.exchAddrs

# Edit given exchange addr from JSON list
@app.post("/editAdr", response_class=JSONResponse)
async def editExchAddr(targetAddr: str = "", newAddr: str ="", newValue: str = ""):
    try:
        if targetAddr not in heuristics.exchAddrs:
            raise KeyError("Invalid key")

        # Remove it
        curVal = heuristics.exchAddrs.pop(targetAddr)
        # Replace it with new key and value (if any)
        heuristics.exchAddrs[newAddr] = newValue if newValue else curVal
    except Exception as e:
        return {
            "result" : e
        }
    else:
        return {
            "result" : "success"
        }

# Delete given exchange addr from JSON list
@app.post("/deleteAdr", response_class=JSONResponse)
async def deleteExchAddr(targetAddr: str = ""):
    try:
        heuristics.exchAddrs.pop(targetAddr)
    except Exception as e:
        return {
            "result" : e
        }
    else:
        return {
            "result" : "success"
        }
