# Performs clustering heuristics around target address
# Imports
import json
from aiohttp import ClientSession
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from GUI import App
from Helpers import Out
from .ServerData_Handler import ServerHandler, partial

class HeuristicsClass():
    def __init__(self, ui:App=None):
        # Store UI instance
        self.ui = ui
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

    def getAddrsOfType(self, addrType="", nebula_session=None):
        # Make query to get all addresses of given type
        result = nebula_session.execute(
            f'MATCH (v:address) WHERE v.address.type == "{addrType}" RETURN v'
        )
        # Check if any addresses found
        if result.is_empty():
            Out.error(f"No addresses of type {addrType} found")
            return []
        return result

    async def addExchanges(self, nebula_session=None):
        # Add all exchanges to graph
        await self.api.runParalel([
            partial(
                self.api.addNodeToGraph,
                dexAddr,
                dexName,
                nodeType="exchange",
                nebula=nebula_session
            ) for dexAddr, dexName in self.exchAddrs.items()
        ])

    async def addDepositAddrs(self, nebula_session=None):
        # Get all found deposit addresses
        exchAddrs = self.getAddrsOfType("exchange", nebula_session)
        # Create session for async requests
        async with ClientSession() as trezor_session:
            # Add all addresses interacting with known exchanges -> deposit addresses
            await self.api.runParalel([
                partial(
                    self.api.getLinkedAddrs,
                    trezor_session,
                    dexAddr,
                    nodeType="deposit",
                    nebula=nebula_session
                ) for dexAddr in exchAddrs
            ])

    async def addClusteredAddrs(self, nebula_session=None):
        # Get all found deposit addresses
        exchDepos = self.getAddrsOfType("deposit", nebula_session)
        # Create session for async requests
        async with ClientSession() as trezor_session:
            # Add all addresses interacting with known exchanges -> deposit addresses
            await self.api.runParalel([
                partial(
                    self.api.getLinkedAddrs,
                    trezor_session,
                    depoAddr,
                    nodeType="leaf",
                    nebula=nebula_session
                ) for depoAddr in exchDepos
            ])

    # Performs update of addresses connected to known exchanges
    async def updateExchangeConns(self):
        pool = self.getNebulaPool()
        with pool.session_context('root', 'nebula') as nebula_session:
            # Clear existing data
            nebula_session.execute('CLEAR SPACE IF EXISTS EthereumClustering')

            # Use defined space
            nebula_session.execute('USE EthereumClustering')
            # Create necessary index, tags and edges
            nebula_session.execute('CREATE TAG IF NOT EXISTS address(name string, type string)')
            nebula_session.execute('CREATE EDGE IF NOT EXISTS linked_to()')
            nebula_session.execute('CREATE TAG INDEX IF NOT EXISTS addrs_index ON address(name, type)')

            # Execute pipeline to construct graph
            await self.addExchanges(nebula_session)
            #await self.addDepositAddrs(nebula_session)
            #awaitself.addClusteredAddrs(nebula_session)
        # close the pool
        pool.close()

    # Performs clustering around target address
    async def clusterAddrs(self):
        # Load target address inserted by user
        targetAddr = self.ui.search_bar.get()
        # Avoid usage of empty address value
        if not targetAddr:
            return
        # Get all clustered addresses and check if target address is in any
        pool = self.getNebulaPool()
        with pool.session_context('root', 'nebula') as nebula_session:
            # Use defined space
            nebula_session.execute('USE EthereumClustering')

            if targetAddr in self.getAddrsOfType("leaf", nebula_session):
                print("FOUND")
        # close the pool
        pool.close()
        # Add result to UI
        #self.ui.addResultAddress(results)
# End of HeuristicsClass class

# Workflow:
    # find all addresses transfering funds to exchange addresses, but exclude ones same as exchange addresses
    # deposit address must forward constantly to the same exchange address
    # addresses sending to deposit addresses must be EOA, nor smart contracts, exchange or miner
