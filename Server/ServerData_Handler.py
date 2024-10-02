# Requests data for UI from server and handles response
# Imports
from Helpers import Out
from .API import *

class ServerHandler():
    def __init__(self):
        # Create API instances
        try:
            self.erigon = ErigonAPI()
            self.trezor = TrezorAPI()
        except Exception as e:
            Out.error(e)
            # Exit when API error
            exit(-1)

    # Gets transaction from server and adds it to UI
    def getTransaction(self, txid=""):
        retVal = self.trezor.get(f"tx/{txid}")
        ### MOCK SETUP ###
        if retVal:
            # Get and return vin address
            return retVal.get("vin")[0].get("addresses")[0]
# End of ServerHandler class
