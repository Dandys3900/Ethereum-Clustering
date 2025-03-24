# Imports
import os
import hashlib
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from dotenv import load_dotenv
from Server import HeuristicsClass
from .API import TrezorAPI, NebulaAPI

# Load env variables
load_dotenv()
# Load stored password for DB refresh
DB_REFRESH_PWD = os.getenv("DB_REFRESH_PWD", "")

# Init FastAPI
app = FastAPI()
# Absolute path to current file parent
BASE_DIR = Path(__file__).resolve().parent
# Serve static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Prepare template for webpage
templates = Jinja2Templates(directory="Server/templates")

# Create Heuristics class instance
heuristics = HeuristicsClass()
# Create Trezor class instance
trezor = TrezorAPI()
# Create NebulaGraph class instance
nebula = NebulaAPI()
# Flag to determine if refresh is on/off
ongoingRefresh = False

# Return conext dict based on refresh status
async def getContext():
    global ongoingRefresh
    return {
        "syncDate"       : await trezor.getCurrentSyncDate(),
        "exchLen"        : heuristics.getExchangeCount(),
        "ongoingRefresh" : ongoingRefresh,
        "addrsCount"     : {
            "exchanges" : nebula.getAddrsOfType("exchange", "COUNT(v)")[0],
            "deposits"  : nebula.getAddrsOfType("deposit",  "COUNT(v)")[0],
            "leafs"     : nebula.getAddrsOfType("leaf",     "COUNT(v)")[0]
        }
    }

# Home page
@app.get("/", response_class=HTMLResponse)
async def showHome(request: Request):
    return templates.TemplateResponse(
        request = request,
        name    = "index.html",
        context = await getContext()
    )

# Refresh database
@app.post("/refreshDB", response_class=HTMLResponse)
async def refreshDB(request: Request, scope: int = Form(...), pwd: str = Form(...)):
    global ongoingRefresh

    # Check for valid refresh password
    correctPwd = (hashlib.sha512(DB_REFRESH_PWD.encode("utf-8")).hexdigest() == pwd)
    # Raise exception to notify client
    if not correctPwd:
        raise HTTPException(status_code=401, detail="Invalid password")

    if not ongoingRefresh:
        ongoingRefresh = True
        # Trigger refresh with given scope
        await heuristics.updateAddrsDB(scope=scope)
        ongoingRefresh = False

    # Render page
    return templates.TemplateResponse(
        request = request,
        name    = "index.html",
        context = await getContext()
    )

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
        name    = "index.html",
        context = {
            **(await getContext()),
            "targetAddr"   : targetAddr,
            "resultsGraph" : resultsGraph
        }
    )
