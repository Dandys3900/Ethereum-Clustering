# Performs clustering heuristics around target address
# Imports
import csv
from GUI import App
from .ServerData_Handler import ServerHandler, startThreading

class HeuristicsClass():
    def __init__(self, ui:App=None):
        # Store UI instance
        self.ui = ui
        # Init ServerData_Handler for communicating with blockchain client
        self.api = ServerHandler()

    # Performs clustering around target address
    def clusterAddrs(self):
        # Load target address inserted by user
        targetAddr = self.ui.search_bar.get()
        # Create lists for storing transactions of target address and known exchanegs
        addrTxs = []
        dexTxs  = []
        # Get all transactions for address and known exchanges
        with open("exchanges.csv", "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            # Construct functions list
            funcsList = [
                (self.api.getAccountTxs(targetAddr, addrTxs)),
                (self.api.getAccountTxs(dexAddr, dexTxs) for dexAddr in reader["address"])
            ]
            # Execute address collecting
            startThreading(funcsList)
            # From both lists exclude known exchange addresses
            addrTxs = filter(lambda x: x not in reader["address"], addrTxs)
            dexTxs  = filter(lambda x: x not in reader["address"], dexTxs)
        # Find all similar addresses
        sameAddrs = list(set(addrTxs) & set(dexTxs))
        # From found similar addresses get all addresses sending to them -> results
        results = []
        funcsList = [
            (self.api.getAccountTxs(depositAddr, results) for depositAddr in sameAddrs)
        ]
        # Execute address collecting
        startThreading(funcsList)
        # Add result to UI
        self.ui.addResultAddress(results)
# End of HeuristicsClass class

# Workflow:
# find all addresses transfering funds to exchange addresses, but exclude ones same as exchange addresses
# deposit address must forward constantly to the same exchange address
# addresses sending to deposit addresses must be EOA, nor smart contracts, exchange or miner
