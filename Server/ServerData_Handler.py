# Requests data for UI from server and handles response
# Imports
import asyncio
from functools import partial
from Helpers import Out
from .API import *

class ServerHandler():
    def __init__(self):
        try: # Create API instances
            self.erigon = ErigonAPI()
            self.trezor = TrezorAPI()
        except Exception as e:
            Out.error(e)
            # Exit on API error
            exit(-1)

    # Submits tasks to the executor making them asynchronous
    async def runParalel(self, funcsList):
        await asyncio.gather(*funcsList)

    # From given transactions, extract addresses
    # NOTE: Store opposite address to find one in transaction
    def getTxAddrs(self, addr, results, page=1):
        apiResponse = (self.trezor.get(f"v2/address/{addr}", params={
            "page"    : page,
            "details" : "txslight"
        })).get("transactions")
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
    async def getLinkedAddrs(self, targetAddr, results:list):
        retVal = self.trezor.get(f"v2/address/{targetAddr}", params={
            "details"  : "txslight"
        })
        # Get total number of pages of transaction for target address
        totalPages = retVal.get("totalPages")
        # Process returned transactions (implicitily from first page)
        self.getTxAddrs(targetAddr, results)
        # Decide whether multi-thread
        if totalPages > 1:
            # Execute address collecting
            await self.runParalel([
                partial(self.getTxAddrs, targetAddr, results, page) for page in totalPages
            ])
# End of ServerHandler class
