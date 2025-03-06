# Requests data for UI from server and handles response
# Imports
import asyncio
from functools import partial
from Helpers import Out
from .API import *
from datetime import datetime

# Const representing value of 1 Wei
ETH_WEI = 1_000_000_000_000_000_000

class ServerHandler():
    def __init__(self, nebulaAPI:NebulaAPI):
        try:
            # Create API instance
            self.trezor = TrezorAPI()
            # Store Nebula class instance
            self.nebula = nebulaAPI
        except Exception as e:
            Out.error(e)
            # Exit on API error
            exit(-1)

    # Submits tasks to the executor making them asynchronous
    async def runParalel(self, funcsList):
        tasks = [func() for func in funcsList]
        return await asyncio.gather(*tasks)

    # From given transactions, extract addresses
    # NOTE: Store opposite address to found one in transaction
    async def getTxAddrs(self, session=None, addr="", addrName="", parentAddr="", nodeType="", page=1):
        # To ensure address consistency, capitalize them
        addr = addr.upper()

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
                txFROMAddr = str(tx.get("vin")[0].get("addresses")[0]).upper()
                txTOAddr   = str(tx.get("vout")[0].get("addresses")[0]).upper()
                # Convert from Wei -> Ether
                txAmount = float(tx.get("vout")[0].get("value")) / ETH_WEI
                # Also extract transaction ID and epoch time
                txID    = str(tx.get("txid"))
                txTime = datetime.fromtimestamp(float(tx.get("blockTime"))).strftime("%Y-%m-%d | %H:%M:%S")

                # Transaction contain target address and direction is TO target address
                if addr in [txFROMAddr, txTOAddr] and addr == txTOAddr:
                    # Add address to graph
                    await self.nebula.addNodeToGraph(
                        addr       = txFROMAddr,
                        addrName   = addrName,
                        parentAddr = parentAddr,
                        nodeType   = nodeType,
                        # Don't waste other edge's params, use separators
                        txParams       = f";{txID},{txTime},{txAmount}",
                        amount     = txAmount
                    )
            except Exception as e:
                Out.error(f"getTxAddrs() error: {e}")
                continue

    # Collects all addresses targetAddr has any transactions with
    async def getLinkedAddrs(self, session=None, targetAddr="", targetName="", parentAddr="", nodeType=""):
        retVal = await self.trezor.get(session, f"v2/address/{targetAddr}", params={
            "details" : "txslight"
        })
        # Check if valid server response
        if not retVal or not retVal.get("totalPages"):
            return

        # Get total number of pages of transaction for target address
        totalPages = retVal.get("totalPages")
        # Execute address collecting
        await self.runParalel([
            partial(
                self.getTxAddrs,
                session    = session,
                addr       = targetAddr,
                addrName   = targetName,
                parentAddr = parentAddr,
                nodeType   = nodeType,
                page       = page
            ) for page in range(1, (totalPages + 1))
        ])
# End of ServerHandler class
