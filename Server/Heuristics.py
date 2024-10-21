# Performs clustering heuristics around target address
# Imports
import json
from aiohttp import ClientSession
from GUI import App
from .ServerData_Handler import ServerHandler, partial, asyncio

class HeuristicsClass():
    def __init__(self, ui:App=None):
        # Store UI instance
        self.ui = ui
        # Init ServerData_Handler for communicating with blockchain client
        self.api = ServerHandler()
        # Load list of all known exchange addresses
        with open("exchanges.json", "r", encoding="utf-8") as file:
            self.exchAddrs = json.load(file)
        # Load all addresses linked with known exchanges
        with open("exchanges_conns.json", "r", encoding="utf-8") as file:
            self.exchConns = json.load(file)

    # Performs update of addresses connected to known exchanges
    async def updateExchangeConns(self):
        self.exchConns = []
        # Create session for async requests
        async with ClientSession() as session:
            # Execute address collecting
            await self.api.runParalel([
                partial(self.api.getLinkedAddrs, session, dexAddr, self.exchConns) for dexAddr in self.exchAddrs
            ])
            # Exclude known exchange addresses
            self.exchConns = list(filter(lambda x: x not in self.exchAddrs, self.exchConns))
        # Update addresses in JSON file
        with open("exchanges_conns.json", "w", encoding="utf-8") as file:
            json.dump(self.exchConns, file)

    # Performs clustering around target address
    async def clusterAddrs(self):
        # Load target address inserted by user
        targetAddr = self.ui.search_bar.get()
        # Avoid usage of empty address value
        if not targetAddr:
            return
        # Create lists for storing transactions of target address and known exchanegs
        addrTxs = []
        # Create session for async requests
        async with ClientSession() as session:
            # Execute address collecting
            await self.api.runParalel([
                partial(self.api.getLinkedAddrs, session, targetAddr, addrTxs)
            ])
            # Exclude known exchange addresses
            addrTxs = list(filter(lambda x: x not in self.exchAddrs, addrTxs))
            # Find all similar addresses => deposit addresses
            depositAddrs = list(set(addrTxs) & set(self.exchConns))
            # None found -> return
            if not depositAddrs:
                return
            # From found similar addresses get all addresses sending to them -> results
            results = []
            # Execute address collecting
            await self.api.runParalel([
                partial(self.api.getLinkedAddrs, session, depositAddr, results) for depositAddr in depositAddrs
            ])
        # Add result to UI
        self.ui.addResultAddress(results)
# End of HeuristicsClass class

# Workflow:
    # find all addresses transfering funds to exchange addresses, but exclude ones same as exchange addresses
    # deposit address must forward constantly to the same exchange address
    # addresses sending to deposit addresses must be EOA, nor smart contracts, exchange or miner
