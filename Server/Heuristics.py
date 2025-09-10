###################################
# @file Heuristics.py
# @author Tomáš Daniel (xdanie14)
# @brief Performs clustering heuristics and cluster search for target address.
###################################

# Imports
import json, atexit
from Helpers import Out, Cache
from .Data_Handler import DataHandler, partial
from .API import NebulaAPI
from .Session import SessionManager

class HeuristicsClass():
    def __init__(self, targetSpace="EthereumClustering"):
        # Load list of all known exchange addresses
        with open("exchanges.json", "r", encoding="utf-8") as file:
            self.exchAddrs = json.load(file)

        # Init Nebula to interact with database
        self.nebula = NebulaAPI(targetSpace=targetSpace)
        # Init ServerData_Handler for communicating with blockchain client
        self.dataHandler = DataHandler(self.nebula)

        # Initialize cache
        Out.blank("Initializing cache")
        if not Cache.get("exchanges_cnt"):
            Cache.set("exchanges_cnt", len(self.nebula.getAddrsOfType("exchange")))
        if not Cache.get("deposits_list"):
            Cache.set("deposits_list", self.nebula.getAddrsOfType("deposit"))
        if not Cache.get("deposits_cnt"):
            Cache.set("deposits_cnt", len(Cache.get("deposits_list")))
        if not Cache.get("leafs_cnt"):
            Cache.set("leafs_cnt", len(self.nebula.getAddrsOfType("leaf")))
        Out.blank("Cache initialized")

        # At exit, write updated JSON exch list back to file
        atexit.register(
            lambda: json.dump(self.exchAddrs, open("exchanges.json", "w", encoding="utf-8"), indent=4)
        )

    async def addExchanges(self, scope):
        # Limit amount of processed exchange addrs by given scope
        exchAddrs = list(self.exchAddrs.items())[:int(len(self.exchAddrs) * (scope / 100))]

        # Add all exchanges to graph
        await self.dataHandler.runParalel([
            partial(
                self.dataHandler.nebula.addNodeToGraph,
                addr     = dexAddr,
                addrName = dexName,
                nodeType = "exchange"
            ) for dexAddr, dexName in exchAddrs
        ])
        Out.success("Adding exchanges done")

    async def addDepositAddrs(self):
        # Get all found deposit addresses
        exchAddrs = self.nebula.getAddrsOfType("exchange")
        # Update check-against list before searching for deposit addrs
        self.dataHandler.knownExchs = self.exchAddrs.keys()

        # Exchanges won't change till next clustering, cache them
        Cache.set("exchanges_cnt", len(exchAddrs))

        # Create session for async requests
        async with SessionManager() as trezor_session:
            # Add all addresses interacting with known exchanges -> deposit addresses
            await self.dataHandler.runParalel([
                partial(
                    self.dataHandler.getLinkedAddrs,
                    session    = trezor_session,
                    targetAddr = dexAddr,
                    targetName = self.exchAddrs.get(dexAddr, ""), # Get name of (parent) exchange
                    parentAddr = dexAddr,
                    nodeType   = "deposit"
                ) for dexAddr in exchAddrs
            ])
        Out.success("Adding deposits done")

    async def addClusteredAddrs(self):
        # Get all found deposit addresses
        exchDepos = self.nebula.getAddrsOfType("deposit")
        # Update check-against list before searching for leaf addrs
        self.dataHandler.knownDepos = exchDepos
        # Store (parent) names of deposit addresses
        deposNames = self.nebula.getAddrsOfType("deposit", "v.address.name")

        # Deposits won't change till next clustering, cache them
        Cache.set("deposits_list", exchDepos)
        Cache.set("deposits_cnt", len(exchDepos))

        # Create session for async requests
        async with SessionManager() as trezor_session:
            # Add all addresses interacting with deposit addresss -> leaf addresses
            await self.dataHandler.runParalel([
                partial(
                    self.dataHandler.getLinkedAddrs,
                    session    = trezor_session,
                    targetAddr = depoAddr,
                    targetName = deposNames[index], # Get name of (parent) exchange
                    parentAddr = depoAddr,
                    nodeType   = "leaf"
                ) for index, depoAddr in enumerate(exchDepos)
            ])

        # Leafs won't change till next clustering, cache them
        Cache.set("leafs_cnt", len(self.nebula.getAddrsOfType("leaf")))

        Out.success("Adding leafs done")

    # Performs update of addresses connected to known exchanges
    # Scope in interval <0, 100> percentage
    async def updateAddrsDB(self, scope=100, minHeight=0, maxHeight=0):
        Out.warning(f"Beginning refresh of DB with scope: {scope}")

        # If user selected custom scope, we are forced to clear DB and start again to match requested block scope
        if (self.dataHandler.minBlock != minHeight) or (self.dataHandler.maxBlock != maxHeight):
            # Update block limits
            self.dataHandler.minBlock = minHeight
            self.dataHandler.maxBlock = maxHeight

            Out.warning(f"Custom refresh scope: erasing current DB; selected block scope: <{minHeight};{maxHeight}>")
            self.nebula.execNebulaCommand('CLEAR SPACE IF EXISTS EthereumClustering')

        # Execute pipeline to construct graph
        await self.addExchanges(scope)
        await self.addDepositAddrs()
        await self.addClusteredAddrs()

        # When done, rebuild index with new data
        self.nebula.execNebulaCommand('REBUILD TAG INDEX addrs_index')

        Out.success("Refresh of DB was succesful")

    # Performs clustering around target address
    async def clusterAddrs(self, targetAddr=""):
        targetAddr = targetAddr.upper()

        try: # Find deposit address(es) of target address
            # If already deposit address, skip and return graph
            if targetAddr in Cache.get("deposits_list"):
                targetAddrDepo = [targetAddr]
            else:
                targetAddrDepo = self.nebula.toArrayTransform(self.nebula.execNebulaCommand(
                    f'MATCH (leaf:address)-->(deposit:address) WHERE id(leaf) == "{targetAddr}" AND deposit.address.type == "deposit" RETURN id(deposit)'
                ), "id(deposit)")

            # Check if found anything
            assert len(targetAddrDepo)
        except Exception:
            Out.error(f"Provided address is unknown or not leaf or deposit: {targetAddr}")
            return ""

        subGraphdata = ""
        # Iterate over all found deposit addresses
        for depoAddr in targetAddrDepo:
            # Construct data for subgraph containing these addresses
            subGraphdata += json.dumps(self.nebula.execNebulaCommand(
                f'GET SUBGRAPH WITH PROP 1 STEPS FROM "{depoAddr}" YIELD VERTICES AS nodes, EDGES AS links'
            ).dict_for_vis(), indent=2, sort_keys=True)

        # Return prepared data
        return subGraphdata
# End of HeuristicsClass class
