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
            # Lists of addresses
            self.knownDepos = []
            self.knownExchs = []
        except Exception as e:
            Out.error(e)
            # Exit on API error
            exit(-1)

    def updateExchAddrs(self, value):
        self.knownExchs = value

    def updateDepoAddrsList(self, value):
        self.knownDepos = value

    # Submits tasks to the executor making them asynchronous
    async def runParalel(self, funcsList):
        tasks = [asyncio.create_task(func()) for func in funcsList]
        return await asyncio.gather(*tasks)

    # From given transactions, extract addresses
    # Store opposite address to found one in transaction
    async def getTxAddrs(self, session=None, addr="", addrName="", parentAddr="", nodeType="", page=1):
        # To ensure address consistency, capitalize them
        addr = addr.upper()
        params = {
            "page"    : page,
            "details" : "txslight"
        }
        # Prepare queue for results
        txQueue = asyncio.Queue()
        creator = asyncio.create_task(
            self.trezor.getJSONStream(session, f"v2/address/{addr}", params=params, queue=txQueue)
        )

        # Iterate over received transaction records (max 1000 txs)
        for _ in range(0, 1000):
            try:
                tx = await txQueue.get()
                if tx is None:
                    break

                txFROMAddr = str(tx.get("vin")[0].get("addresses")[0]).upper()
                txTOAddr   = str(tx.get("vout")[0].get("addresses")[0]).upper()
                # Convert from Wei -> Ether
                txAmount = float(tx.get("vout")[0].get("value")) / ETH_WEI
                # Also extract transaction ID and epoch time
                txID   = str(tx.get("txid"))
                txTime = datetime.fromtimestamp(float(tx.get("blockTime"))).strftime("%Y-%m-%d | %H:%M:%S")
                # Determine if EOA transaction
                eoaTx = (tx.get("ethereumSpecific").get("data") == "0x")

                # Transaction contain target address with direction is TO target address
                if addr in [txFROMAddr, txTOAddr] and addr == txTOAddr:
                    # Exclude known exchange addresses
                    if txFROMAddr in self.knownExchs:
                        continue
                    if nodeType == "leaf":
                        # Exclude non-EOA leaf addresses
                        # Exclude deposit addresses as leaf ones (if happens deposits transfer between each other, not valid)
                        if not eoaTx or txFROMAddr in self.knownDepos:
                            continue

                    # Add address to graph
                    await self.nebula.addNodeToGraph(
                        addr       = txFROMAddr,
                        addrName   = addrName,
                        parentAddr = parentAddr,
                        nodeType   = nodeType,
                        # Don't waste other edge's params, use separators
                        txParams   = f";{txID},{txTime},{txAmount}",
                        amount     = txAmount
                    )
            except Exception as e:
                Out.error(f"getTxAddrs(): {e}")
                continue
            finally:
                # Mark item as done
                txQueue.task_done()
        await creator

    # Collects all addresses targetAddr has any transactions with
    async def getLinkedAddrs(self, session=None, targetAddr="", targetName="", parentAddr="", nodeType=""):
        # Get total number of pages of transaction for target address
        totalPages = await self.trezor.getJSONStream(session, f"v2/address/{targetAddr}", key="totalPages", params={
            "details" : "txslight"
        })
        # Check if valid server response
        if not totalPages:
            return

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
