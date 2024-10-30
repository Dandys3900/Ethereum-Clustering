# Imports
from Server import HeuristicsClass
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Init FastAPI
app = FastAPI()
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
@app.post("/refreshDB", response_class=HTMLResponse)
async def refreshDB(request: Request):
    # Trigger refresh
    await heuristics.updateAddrsDB()
    # Render page
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# Init search
@app.get("/search", response_class=HTMLResponse)
async def searchAddr(request: Request, targetAddr: str):
    # Collect addresses
    results = await heuristics.clusterAddrs(targetAddr)
    # Render page
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "targetAddr" : targetAddr,
            "results"    : results
        }
    )
