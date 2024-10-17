# Requests data for UI from server and handles response
# Imports
import asyncio
from functools import partial
from Helpers import Out
from .API import *

class ServerHandler():
    def __init__(self):
        try: # Create API instances
            self.trezor = TrezorAPI()
        except Exception as e:
            Out.error(e)
            # Exit on API error
            exit(-1)

    # Submits tasks to the executor making them asynchronous
    async def runParalel(self, funcsList):
        tasks = [func() for func in funcsList]
        await asyncio.gather(*tasks)

    # From given transactions, extract addresses
    # NOTE: Store opposite address to found one in transaction
    async def getTxAddrs(self, session, addr, results:list, page=1):
        apiResponse = await (self.trezor.get(session, f"v2/address/{addr}", params={
            "page"    : page,
            "details" : "txslight"
        }))
        # Check if valid server response
        if not apiResponse:
            return
        # Get list of transactions
        apiResponse = apiResponse.get("transactions")
        # Iterate over received transaction records
        for tx in apiResponse:
            txFROMAddr = tx.get("vin")[0].get("addresses")[0]
            txTOAddr   = tx.get("vout")[0].get("addresses")[0]
            # Transaction contain target address
            if addr in [txFROMAddr, txTOAddr]:
                results.append(
                    txTOAddr if addr == txFROMAddr else txFROMAddr
                )

    # Collects all addresses targetAddr has any transactions with
    async def getLinkedAddrs(self, session, targetAddr, results:list):
        retVal = await self.trezor.get(session, f"v2/address/{targetAddr}", params={
            "details"  : "txslight"
        })
        # Check if valid server response
        if not retVal:
            return
        # Get total number of pages of transaction for target address
        totalPages = retVal.get("totalPages")
        # Process returned transactions (implicitily from first page)
        await self.getTxAddrs(session, targetAddr, results)
        # Decide whether multi-thread
        if totalPages > 1:
            # Execute address collecting
            self.runParalel([
                partial(self.getTxAddrs, session, targetAddr, results, page) for page in totalPages
            ])
# End of ServerHandler class
