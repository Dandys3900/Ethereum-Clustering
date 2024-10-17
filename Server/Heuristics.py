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

    # Performs clustering around target address
    async def clusterAddrs(self):
        # Load target address inserted by user
        targetAddr = self.ui.search_bar.get()
        # Avoid usage of empty address value
        if not targetAddr:
            return
        # Create lists for storing transactions of target address and known exchanegs
        addrTxs = []
        dexTxs  = []
        # Get all transactions for address and known exchanges
        with open("exchanges.json", "r", encoding="utf-8") as file:
            # Load known exchange addresses
            exchAddrs = json.load(file)

        async with ClientSession() as session:
            # Execute address collecting
            await self.api.runParalel(
                [partial(self.api.getLinkedAddrs, session, targetAddr, addrTxs)]
              + [partial(self.api.getLinkedAddrs, session, dexAddr, dexTxs) for dexAddr in exchAddrs
            ])
            # From both lists exclude known exchange addresses
            addrTxs = filter(lambda x: x not in exchAddrs, addrTxs)
            dexTxs  = filter(lambda x: x not in exchAddrs, dexTxs)
            # Find all similar addresses => deposit addresses
            depositAddrs = list(set(addrTxs) & set(dexTxs))
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
