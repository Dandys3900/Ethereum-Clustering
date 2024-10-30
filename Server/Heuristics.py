# Performs clustering heuristics around target address
# Imports
import json
from aiohttp import ClientSession
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from Helpers import Out
from .ServerData_Handler import ServerHandler, partial

class HeuristicsClass():
    def __init__(self):
        # Load list of all known exchange addresses
        with open("exchanges.json", "r", encoding="utf-8") as file:
            self.exchAddrs = json.load(file)
        # Init ServerData_Handler for communicating with blockchain client
        self.api = ServerHandler([addr[0] for addr in self.exchAddrs.items()])

    # Init connection to Nebula instance and return pool to use
    def getNebulaPool(self):
        try:
            # Define config
            config = Config()
            # Init connection pool
            connection_pool = ConnectionPool()
            # Check if connection to pool is valid
            if not connection_pool.init([('127.0.0.1', 9669)], config):
                raise Exception("connection_pool.init() returned False")
            return connection_pool
        except Exception as e:
            Out.error(f"Error while creating Nebula connection: {e}")
            exit(-1)

    def getAddrsOfType(self, addrType=""):
        # Make query to get all addresses of given type
        result = self.api.ExecNebulaCommand(
            f'MATCH (v:address) WHERE v.address.type == "{addrType}" RETURN id(v)'
        )
        # Check if any addresses found
        if result.is_empty():
            Out.error(f"No addresses of type {addrType} found")
            return []
        return [val.as_string() for val in result.column_values("id(v)")]

    async def addExchanges(self):
        # Add all exchanges to graph
        await self.api.runParalel([
            partial(
                self.api.addNodeToGraph,
                dexAddr,
                dexName,
                nodeType="exchange"
            ) for dexAddr, dexName in self.exchAddrs.items()
        ])

    async def addDepositAddrs(self):
        # Get all found deposit addresses
        exchAddrs = self.getAddrsOfType("exchange")
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
        exchDepos = self.getAddrsOfType("deposit")
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
    async def updateAddrsDB(self):
        pool = self.getNebulaPool()
        with pool.session_context('root', 'nebula') as nebula_session:
            # Assign this session to server
            self.api.nebula = nebula_session

            # Clear existing data
            self.api.ExecNebulaCommand('CLEAR SPACE IF EXISTS EthereumClustering')

            # Use defined space
            self.api.ExecNebulaCommand('USE EthereumClustering')

            # Create necessary index, tags and edges
            self.api.ExecNebulaCommand('CREATE TAG IF NOT EXISTS address(name string, type string)')
            self.api.ExecNebulaCommand('CREATE TAG INDEX IF NOT EXISTS addrs_index ON address(type(10))')
            self.api.ExecNebulaCommand('CREATE EDGE IF NOT EXISTS linked_to()')

            # Execute pipeline to construct graph
            await self.addExchanges()
            await self.addDepositAddrs()
            await self.addClusteredAddrs()
        # close the pool
        pool.close()

    # Performs clustering around target address
    async def clusterAddrs(self, targetAddr=""):
        # Avoid usage of empty address value
        if not targetAddr:
            return
        # Get all clustered addresses and check if target address is in any
        pool = self.getNebulaPool()
        with pool.session_context('root', 'nebula') as nebula_session:
            # Use defined space
            self.api.ExecNebulaCommand('USE EthereumClustering')

            if targetAddr in self.getAddrsOfType("leaf", nebula_session):
                print("FOUND")
        # close the pool
        pool.close()
        # Add result to UI
        #ui.addResultAddress(results)
# End of HeuristicsClass class

# Workflow:
    # find all addresses transfering funds to exchange addresses, but exclude ones same as exchange addresses
    # deposit address must forward constantly to the same exchange address
    # addresses sending to deposit addresses must be EOA, nor smart contracts, exchange or miner
