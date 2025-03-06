# Imports
from Server import HeuristicsClass
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from .API import TrezorAPI

# Absolute path to current file parent
BASE_DIR = Path(__file__).resolve().parent

# Init FastAPI
app = FastAPI()
# Serve static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
# Prepare template for webpage
templates = Jinja2Templates(directory="Server/templates")
# Create Heuristics class instance
heuristics = HeuristicsClass()
# Create Trezor class instance
trezor = TrezorAPI()
# Flag to determine if refresh is on/off
ongoingRefresh = False

# Return conext dict based on refresh status
async def getContext():
    global ongoingRefresh
    context = {
        "syncDate" : await trezor.getCurrentSyncDate(),
        "exchLen"  : heuristics.getExchangeCount()
    }
    # Extend if refresh is ongoing
    ongoingRefresh and context.update({"ongoingRefresh" : True})

    return context

# Home page
@app.get("/", response_class=HTMLResponse)
async def showHome(request: Request):
    return templates.TemplateResponse(
        request=request,
        name    = "index.html",
        context = await getContext()
    )

# Refresh database
@app.post("/refreshDB", response_class=HTMLResponse)
async def refreshDB(request: Request, scope: int = Form(...)):
    global ongoingRefresh
    if not ongoingRefresh:
        ongoingRefresh = True
        # Trigger refresh with given scope
        await heuristics.updateAddrsDB(scope=scope)
        ongoingRefresh = False

    # Render page
    return templates.TemplateResponse(
        request=request,
        name    = "index.html",
        context = await getContext()
    )

# Init search
@app.post("/search", response_class=HTMLResponse)
async def searchAddr(request: Request, targetAddr: str = Form(...)):
    # Collect addresses
    resultsGraph = await heuristics.clusterAddrs(targetAddr=targetAddr)

    # Render page
    return templates.TemplateResponse(
        request=request,
        name    = "index.html",
        context = {
            **(await getContext()),
            "targetAddr"   : targetAddr,
            "resultsGraph" : resultsGraph
        }
    )
