# Performs clustering heuristics around target address
# Imports
import json
from Helpers import Out
from .Data_Handler import ServerHandler, partial
from .API import NebulaAPI
from .Session import SessionManager
from datetime import datetime

class HeuristicsClass():
    def __init__(self, targetSpace="EthereumClustering"):
        # Load list of all known exchange addresses
        with open("exchanges.json", "r", encoding="utf-8") as file:
            self.exchAddrs = json.load(file)
        # Init Nebula to interact with database
        self.nebula = NebulaAPI(targetSpace=targetSpace)
        # Init ServerData_Handler for communicating with blockchain client
        self.api = ServerHandler(self.nebula)

    def getExchangeCount(self):
        return len(self.exchAddrs)

    async def addExchanges(self, scope):
        # Limit amount of processed exchange addrs by given scope
        exchAddrs = list(self.exchAddrs.items())[:int(self.getExchangeCount() * (scope / 100))]

        # Add all exchanges to graph
        await self.api.runParalel([
            partial(
                self.api.nebula.addNodeToGraph,
                addr     = dexAddr,
                addrName = dexName,
                nodeType = "exchange"
            ) for dexAddr, dexName in exchAddrs
        ])

    async def addDepositAddrs(self):
        # Get all found deposit addresses
        exchAddrs = self.nebula.getAddrsOfType("exchange")
        # Update check-against list before searching for deposit addrs
        self.api.updateExchAddrs(self.exchAddrs.keys())

        # Create session for async requests
        async with SessionManager() as trezor_session:
            # Add all addresses interacting with known exchanges -> deposit addresses
            await self.api.runParalel([
                partial(
                    self.api.getLinkedAddrs,
                    session    = trezor_session,
                    targetAddr = dexAddr,
                    targetName = self.exchAddrs.get(dexAddr, ""), # Get name of (parent) exchange
                    parentAddr = dexAddr,
                    nodeType   = "deposit"
                ) for dexAddr in exchAddrs
            ])

    async def addClusteredAddrs(self):
        # Get all found deposit addresses
        exchDepos = self.nebula.getAddrsOfType("deposit")
        # Update check-against list before searching for leaf addrs
        self.api.updateDepoAddrsList(exchDepos)
        # Store (parent) names of deposit addresses
        deposNames = self.nebula.getAddrsOfType("deposit", "v.address.name")

        # Create session for async requests
        async with SessionManager() as trezor_session:
            # Add all addresses interacting with deposit addresss -> leaf addresses
            await self.api.runParalel([
                partial(
                    self.api.getLinkedAddrs,
                    session    = trezor_session,
                    targetAddr = depoAddr,
                    targetName = deposNames[index], # Get name of (parent) exchange
                    parentAddr = depoAddr,
                    nodeType   = "leaf"
                ) for index, depoAddr in enumerate(exchDepos)
            ])

    # Performs update of addresses connected to known exchanges
    # Scope in interval <0, 100> percentage
    async def updateAddrsDB(self, scope=100):
        Out.warning(f"Beginning refresh of DB with scope: {scope}")
        # Clear existing data
        #self.nebula.ExecNebulaCommand('CLEAR SPACE IF EXISTS EthereumClustering')

        # Execute pipeline to construct graph
        await self.addExchanges(scope)
        await self.addDepositAddrs()
        await self.addClusteredAddrs()

        # When done, rebuild index with new data
        self.nebula.ExecNebulaCommand('REBUILD TAG INDEX addrs_index')
        Out.success("Refresh of DB was succesful")

        with open("refreshend.txt", "w", encoding="utf-8") as file:
            file.write(f"Current Date and Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")

    # Performs clustering around target address
    async def clusterAddrs(self, targetAddr=""):
        targetAddr = targetAddr.upper()

        try: # Find deposit address(es) of target address
            targetAddrDepo = self.nebula.toArrayTransform(self.nebula.ExecNebulaCommand(
                f'MATCH (leaf:address)-->(deposit:address) WHERE id(leaf) == "{targetAddr}" AND deposit.address.type == "deposit" RETURN id(deposit)'
            ), "id(deposit)")
        except Exception:
            Out.error(f"Provided address is unknown or not leaf: {targetAddr}")
            return ""

        subGraphdata = ""
        # Iterate over all found deposit addresses
        for depoAddr in targetAddrDepo:
            # Construct data for subgraph containing these addresses
            subGraphdata += json.dumps(self.nebula.ExecNebulaCommand(
                f'GET SUBGRAPH WITH PROP 1 STEPS FROM "{depoAddr}" YIELD VERTICES AS nodes, EDGES AS links'
            ).dict_for_vis(), indent=2, sort_keys=True)

        # Return prepared data
        return subGraphdata
# End of HeuristicsClass class
