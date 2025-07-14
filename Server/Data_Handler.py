###################################
# @file Data_Handler.py
# @author Tomáš Daniel (xdanie14)
# @brief Requests and handles data for UI from server.
###################################

# Imports
import asyncio
from functools import partial
from Helpers import Out, Cache
from .API import *
from datetime import datetime

# Const representing value of 1 Wei
ETH_WEI = 1_000_000_000_000_000_000

class DataHandler():
    def __init__(self, nebulaAPI:NebulaAPI):
        try:
            # Create API instance
            self.trezor = TrezorAPI()
            # Store Nebula class instance
            self.nebula = nebulaAPI
            # Lists of addresses
            self.knownDepos = []
            self.knownExchs = []
            # Block limits (set by Heuristics class and by user)
            self.minBlock = None
            self.maxBlock = None
        except Exception as e:
            Out.error(e)
            # Exit on API error
            exit(-1)

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
            # Skip already processed blocks (otherwise start from initial (0) block (or value set by user))
            "from"    : self.minBlock if self.minBlock else Cache.get(addr, 0),
            # if set use user's max block limit, else stop and client's heighest parsed block
            "to"      : self.maxBlock if self.maxBlock else self.trezor.heighestBlock,
            "details" : "txslight"
        }

        # Iterate over received transaction records
        async for i, tx in enumerate(self.trezor.get(session, f"v2/address/{addr}", params=params)):
            try:
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

                # Get first valid exchange tx and store block height to skip it next refresh
                # Returned txs are sorted by block height in descending order (first tx is highest)
                if nodeType == "exchange" and i == 0:
                    # Get block height of newest tx
                    blockHeight = int(tx.get("blockHeight"))
                    Cache.set(addr, (blockHeight + 1))

                # Transaction contain target address with direction is TO target address and having send Ether > 0
                if addr in [txFROMAddr, txTOAddr] and addr == txTOAddr and txAmount > 0.0:
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
            except TypeError:
                Out.error("getTxAddrs(): given tx object contains unexpected None values, skipping")
            except Exception as e:
                Out.error(f"getTxAddrs(): {e}")

    # Collects all addresses targetAddr has any transactions with
    async def getLinkedAddrs(self, session=None, targetAddr="", targetName="", parentAddr="", nodeType=""):
        # Get total number of pages of transaction for target address
        totalPages = await anext(self.trezor.get(session, f"v2/address/{targetAddr}", key="totalPages", params={
            "details" : "txslight"
        }))
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
# End of DataHandler class
