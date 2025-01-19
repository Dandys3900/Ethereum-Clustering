# Imports
from Server import HeuristicsClass
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

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

# Home page
@app.get("/", response_class=HTMLResponse)
async def showHome(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# Refresh database
@app.get("/refreshDB", response_class=HTMLResponse)
async def refreshDB(request: Request, refreshScope: int):
    # Trigger refresh with given scope
    await heuristics.updateAddrsDB(scope=refreshScope)
    # Render page
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# Init search
@app.get("/search", response_class=HTMLResponse)
async def searchAddr(request: Request, targetAddr: str):
    # Collect addresses
    resultsList, resultsGraph = await heuristics.clusterAddrs(targetAddr=targetAddr)
    # Render page
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "resultsList"  : resultsList,
            "resultsGraph" : resultsGraph
        }
    )
