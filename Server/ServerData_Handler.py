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
            # Create member to store current Nebula session (if any)
            self.nebula = None
            # Create list of invalidated deposit addresses
            self.prohibDeposAddrs = []
        except Exception as e:
            Out.error(e)
            # Exit on API error
            exit(-1)

    # Helper to catch eventual execution errors
    def ExecNebulaCommand(self, command=""):
        # Ensure we have valid session
        assert self.nebula
        resp = self.nebula.execute(command)
        # Check for execution errors
        assert resp.is_succeeded(), resp.error_msg()
        # Return result (for compatibility reasons)
        return resp

    # Submits tasks to the executor making them asynchronous
    async def runParalel(self, funcsList):
        tasks = [func() for func in funcsList]
        return await asyncio.gather(*tasks)

    # Handles adding new node to graph
    async def addNodeToGraph(self, addr="", addrName="", parentAddr="", nodeType=""):
        # Skip already invalidated deposit address
        if addr in self.prohibDeposAddrs:
            return
        # Add node (vertex) to graph
        self.ExecNebulaCommand(
            f'INSERT VERTEX IF NOT EXISTS address(name, type) VALUES "{addr}": ("{addrName}", "{nodeType}")'
        )
        # Parent address is given so create a path to it
        if parentAddr != "":
            self.ExecNebulaCommand(
                f'INSERT EDGE IF NOT EXISTS linked_to() VALUES "{addr}"->"{parentAddr}": ()'
            )
        # Add additional policy for "deposit" node
        if nodeType == "deposit":
            # Ensure deposit address transfers constantly to the same exchange, otherwise remove it
            result = self.ExecNebulaCommand(
                f'MATCH (v)-[e:linked_to]->() WHERE id(v) == "{addr}" RETURN COUNT(e)'
            )
            # If deposit node has more than one edge, our policy is broken so remove the node
            if result.column_values("COUNT(e)")[0].as_int() != 1:
                self.ExecNebulaCommand(
                    f'DELETE VERTEX {addr}'
                )
                # Add it to blacklist
                self.prohibDeposAddrs.append(addr)

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

                # Transaction contain target address and it's NOT known exchange
                if addr in [txFROMAddr, txTOAddr]:
                    # Determine which address record to add
                    addrKey = (txTOAddr if addr == txFROMAddr else txFROMAddr)
                    if addrKey in self.exchAddrs:
                        return
                    # Add address to graph
                    await self.addNodeToGraph(
                        addrKey,
                        addrName,
                        parentAddr,
                        nodeType
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
                session,
                targetAddr,
                targetName,
                parentAddr,
                nodeType,
                page
            ) for page in range(1, (totalPages + 1))
        ])
# End of ServerHandler class
