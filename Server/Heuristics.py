# Performs clustering heuristics around target address
# Imports
import json
from aiohttp import ClientSession
from Helpers import Out
from .ServerData_Handler import ServerHandler, partial
from .API import NebulaAPI

class HeuristicsClass():
    def __init__(self):
        # Load list of all known exchange addresses
        with open("exchanges.json", "r", encoding="utf-8") as file:
            self.exchAddrs = json.load(file)
        # Init Nebula to interact with database
        self.nebula = NebulaAPI()
        # Init ServerData_Handler for communicating with blockchain client
        self.api = ServerHandler([addr[0] for addr in self.exchAddrs.items()], self.nebula)

    async def addExchanges(self, scope):
        exchanges = list(self.exchAddrs.items())
        # Limit amount of processed addrs by given scope
        exchanges = exchanges[:int(len(exchanges) * (scope / 100))]
        # Add all exchanges to graph
        await self.api.runParalel([
            partial(
                self.api.addNodeToGraph,
                dexAddr,
                dexName,
                nodeType="exchange"
            ) for dexAddr, dexName in exchanges
        ])

    async def addDepositAddrs(self):
        # Get all found deposit addresses
        exchAddrs = self.nebula.getAddrsOfType("exchange")
        # Create session for async requests
        async with ClientSession() as trezor_session:
            # Add all addresses interacting with known exchanges -> deposit addresses
            await self.api.runParalel([
                partial(
                    self.api.getLinkedAddrs,
                    trezor_session,
                    dexAddr,
                    parentAddr=dexAddr,
                    nodeType="deposit"
                ) for dexAddr in exchAddrs
            ])

    async def addClusteredAddrs(self):
        # Get all found deposit addresses
        exchDepos = self.nebula.getAddrsOfType("deposit")
        # Create session for async requests
        async with ClientSession() as trezor_session:
            # Add all addresses interacting with known exchanges -> deposit addresses
            await self.api.runParalel([
                partial(
                    self.api.getLinkedAddrs,
                    trezor_session,
                    depoAddr,
                    parentAddr=depoAddr,
                    nodeType="leaf"
                ) for depoAddr in exchDepos
            ])

    # Performs update of addresses connected to known exchanges
    # Scope in interval <0, 100> percentage
    async def updateAddrsDB(self, scope=100):
        pool = self.nebula.getNebulaPool()
        with pool.session_context('root', 'nebula') as nebula_session:
            # Store this session to server
            self.nebula.setNebulaSession(nebula_session)

            # Clear existing data
            self.nebula.ExecNebulaCommand('CLEAR SPACE IF EXISTS EthereumClustering')

            # Use defined space
            self.nebula.ExecNebulaCommand('USE EthereumClustering')

            # Create necessary index, tags and edges
            self.nebula.ExecNebulaCommand('CREATE TAG IF NOT EXISTS address(name string, type string)')
            self.nebula.ExecNebulaCommand('CREATE TAG INDEX IF NOT EXISTS addrs_index ON address(type(10))')
            #self.nebula.ExecNebulaCommand('CREATE EDGE IF NOT EXISTS linked_to()')
            self.nebula.ExecNebulaCommand('CREATE EDGE IF NOT EXISTS linked_to(amount float DEFAULT 0.0)')

            # Execute pipeline to construct graph
            await self.addExchanges(scope)
            await self.addDepositAddrs()
            await self.addClusteredAddrs()

            # When done, rebuild index with new data
            self.nebula.ExecNebulaCommand('REBUILD TAG INDEX addrs_index')
        # close the pool
        pool.close()

    # Performs clustering around target address
    async def clusterAddrs(self, targetAddr=""):
        # Get all clustered addresses and check if target address is in any
        pool = self.nebula.getNebulaPool()
        with pool.session_context('root', 'nebula') as nebula_session:
            # Store this session to server
            self.nebula.setNebulaSession(nebula_session)

            # Use defined space
            self.nebula.ExecNebulaCommand('USE EthereumClustering')

            # Try and check if any known leaf matches this address
            if targetAddr.upper() not in self.nebula.getAddrsOfType("leaf"):
                return "", ""

            # Find deposit address(es) of target address
            targetAddrDepo = self.nebula.toArrayTransform(self.nebula.ExecNebulaCommand(
                f'MATCH (leaf:address)-->(deposit:address) WHERE id(leaf) == "{targetAddr}" RETURN id(deposit)'
            ), "id(deposit)")

            subGraphdata = ""
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
        # close the pool
        pool.close()
        # Return prepared data
        return clustrAddrsList, subGraphdata
# End of HeuristicsClass class

# Workflow:
    # find all addresses transfering funds to exchange addresses, but exclude ones same as exchange addresses
    # deposit address must forward constantly to the same exchange address
    # addresses sending to deposit addresses must be EOA, nor smart contracts, exchange or miner
