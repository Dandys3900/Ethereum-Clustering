# Requests data for UI from server and handles response
# Imports
import asyncio
from functools import partial
from Helpers import Out
from .API import *

class ServerHandler():
    def __init__(self, exchAddrs):
        try:
            # Create API instance
            self.trezor = TrezorAPI()
            # Store list of known exchanges
            self.exchAddrs = exchAddrs
        except Exception as e:
            Out.error(e)
            # Exit on API error
            exit(-1)

    # Submits tasks to the executor making them asynchronous
    async def runParalel(self, funcsList):
        tasks = [func() for func in funcsList]
        return await asyncio.gather(*tasks)

    # Handles adding new node to graph
    async def addNodeToGraph(self, addr="", addrName="", parentAddr="", nodeType="", nebula=None):
        nebula.execute(
            f"INSERT VERTEX IF NOT EXISTS address(name, type) VALUES '{addr}': ('{addrName}', '{nodeType}')"
        )
        # Parent address is given so create a path to it
        if parentAddr:
            nebula.execute(
                f"INSERT EDGE IF NOT EXISTS linked_to() VALUES '{parentAddr}'->'{addr}': ()"
            )

    # From given transactions, extract addresses
    # NOTE: Store opposite address to found one in transaction
    async def getTxAddrs(self, session=None, addr="", addrName="", parentAddr="", nodeType="", nebula=None, page=1):
        apiResponse = await (self.trezor.get(session, f"v2/address/{addr}", params={
            "page"    : page,
            "details" : "txslight"
        }))
        # Check if valid server response
        if not apiResponse or apiResponse.get("transactions", {}) == {}:
            return
        # Get list of transactions
        apiResponse = apiResponse.get("transactions")
        # Iterate over received transaction records
        for tx in apiResponse:
            try:
                txFROMAddr = tx.get("vin")[0].get("addresses")[0]
                txTOAddr   = tx.get("vout")[0].get("addresses")[0]
                # Transaction contain target address and it's NOT known exchange
                if addr in [txFROMAddr, txTOAddr] and addr not in self.exchAddrs:
                    # Determine which address record to add
                    addrKey = (txTOAddr if addr == txFROMAddr else txFROMAddr)
                    # Add address to graph
                    self.addNodeToGraph(
                        addrKey,
                        addrName,
                        parentAddr,
                        nodeType,
                        nebula
                    )
            except Exception:
                continue

    # Collects all addresses targetAddr has any transactions with
    async def getLinkedAddrs(self, session=None, targetAddr="", targetName="", parentAddr="", nodeType="", nebula=None):
        retVal = await self.trezor.get(session, f"v2/address/{targetAddr}", params={
            "details"  : "txslight"
        })
        # Check if valid server response
        if not retVal or not retVal.get("totalPages"):
            return
        # Get total number of pages of transaction for target address
        totalPages = retVal.get("totalPages")
        # Process returned transactions (implicitily from first page)
        await self.getTxAddrs(
            session,
            targetAddr,
            targetName,
            parentAddr,
            nodeType,
            nebula
        )
        # Decide whether multi-thread
        if totalPages > 1:
            # Execute address collecting
            await self.runParalel([
                partial(
                    self.getTxAddrs,
                    session,
                    targetAddr,
                    targetName,
                    parentAddr,
                    nebula,
                    nodeType,
                    page
                ) for page in range(2, (totalPages + 1))
            ])
# End of ServerHandler class
