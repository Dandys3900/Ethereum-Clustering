# Performs clustering heuristics around target address
# Imports
import json
from aiohttp import ClientSession
from Helpers import Out
from .Data_Handler import ServerHandler, partial
from .API import NebulaAPI

class HeuristicsClass():
    def __init__(self):
        # Load list of all known exchange addresses
        with open("exchanges.json", "r", encoding="utf-8") as file:
            self.exchAddrs = json.load(file)
        # Init Nebula to interact with database
        self.nebula = NebulaAPI()
        # Init ServerData_Handler for communicating with blockchain client
        self.api = ServerHandler(self.nebula)
        # Set default (production) Nebula space
        self.targetSpace = "EthereumClustering"
        # Make sure space is created
        self.nebula.createSpace(self.targetSpace)

    # Setter for Nebula space (used by unitests)
    def setNebulaSpace(self, newSpace=""):
        self.targetSpace = newSpace

    async def addExchanges(self, scope):
        exchanges = list(self.exchAddrs.items())
        # Limit amount of processed addrs by given scope
        exchanges = exchanges[:int(len(exchanges) * (scope / 100))]
        # Add all exchanges to graph
        await self.api.runParalel([
            partial(
                self.api.nebula.addNodeToGraph,
                addr     = dexAddr,
                addrName = dexName,
                nodeType = "exchange"
            ) for dexAddr, dexName in exchanges
        ])

    async def addDepositAddrs(self):
        # Get all found deposit addresses
        exchAddrs = self.nebula.getAddrsOfType("exchange")
        # Store all known exchanges to exclude them as deposit addresses
        self.api.setExchangeAddrs(exchAddrs)

        # Create session for async requests
        async with ClientSession() as trezor_session:
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
        # Store all known deposits to exclude them as leaf addresses
        self.api.setDepositAddrs(exchDepos)
        # Store (parent) names of deposit addresses
        deposNames = self.nebula.getAddrsOfType("deposit", "v.address.name")

        # Create session for async requests
        async with ClientSession() as trezor_session:
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
        self.nebula.ExecNebulaCommand('CLEAR SPACE IF EXISTS EthereumClustering')

        # Use defined space
        self.nebula.ExecNebulaCommand('USE EthereumClustering')

        # Execute pipeline to construct graph
        await self.addExchanges(scope)
        await self.addDepositAddrs()
        await self.addClusteredAddrs()

        # When done, rebuild index with new data
        self.nebula.ExecNebulaCommand('REBUILD TAG INDEX addrs_index')
        Out.success("Refresh of DB was succesful")

    # Performs clustering around target address
    async def clusterAddrs(self, targetAddr=""):
        targetAddr = targetAddr.upper()
        # Use defined space
        self.nebula.ExecNebulaCommand(f'USE {self.targetSpace}')

        # Try and check if any known leaf matches this address
        if targetAddr not in self.nebula.getAddrsOfType("leaf"):
            Out.error(f"Given (leaf) address {targetAddr} not found in any cluster")
            # resultsList, resultsGraph
            return "", ""

        # Find deposit address(es) of target address
        targetAddrDepo = self.nebula.toArrayTransform(self.nebula.ExecNebulaCommand(
            f'MATCH (leaf:address)-->(deposit:address) WHERE id(leaf) == "{targetAddr}" RETURN id(deposit)'
        ), "id(deposit)")

        subGraphdata    = ""
        clustrAddrsList = ""
        # Iterate over all found deposit addresses
        for depoAddr in targetAddrDepo:
            # Construct data for subgraph containing these addresses
            subGraphdata += json.dumps(self.nebula.ExecNebulaCommand(
                f'GET SUBGRAPH WITH PROP 1 STEPS FROM "{depoAddr}" YIELD VERTICES AS nodes, EDGES AS links'
            ).dict_for_vis(), indent=2, sort_keys=True)

            # Find all leaf addresses with same deposit address
            clustrAddrsList += json.dumps(self.nebula.toArrayTransform(self.nebula.ExecNebulaCommand(
                f'MATCH (leaf:address)-->(deposit:address) WHERE id(deposit) == "{depoAddr}" AND leaf.address.type == "leaf" RETURN id(leaf)'
            ), "id(leaf)"), indent=2)

        # Return prepared data
        return clustrAddrsList, subGraphdata
# End of HeuristicsClass class
