# Performs clustering heuristics around target address
# Imports
from GUI import App
from .ServerData_Handler import ServerHandler

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
        ### MOCK SETUP ###
        retVal = self.api.getTransaction("0x676621c4a9d7b9f9d898254f190376fa17209651c387b4becf59ca430e1651ff")
        # Add result to UI
        self.ui.addResultAddress(retVal)
# End of HeuristicsClass class
