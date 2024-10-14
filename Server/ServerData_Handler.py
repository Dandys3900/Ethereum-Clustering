# Requests data for UI from server and handles response
# Imports
from Helpers import Out, startThreading
from .API import *

# From given transactions, extract addresses
# NOTE: Always store opposite address to find one in transaction
def gettxAddrs(apiResponse, addr, dest):
    for tx in apiResponse:
        txFROMAddr = tx.get("vin")[0].get("addresses")[0]
        txTOAddr   = tx.get("vout")[0].get("addresses")[0]
        # Transaction contain target address
        if addr in [txFROMAddr, txTOAddr]:
            dest.append(
                txTOAddr if addr == txFROMAddr else txFROMAddr
            )
        # Or where it sends tokens via smart contract (if any)
        tokenTrf = tx.get("tokenTransfers")[0] if tokenTrf else None
        if tokenTrf:
            # Store both from and to addresses
            fromAddr = tokenTrf.get("from")
            toAddr   = tokenTrf.get("to")
            # Token transaction contain target address
            if addr in [fromAddr, toAddr]:
                dest.append(
                    toAddr if addr == fromAddr else fromAddr
                )

class ServerHandler():
    def __init__(self):
        # Create API instances
        try:
            self.erigon = ErigonAPI()
            self.trezor = TrezorAPI()
        except Exception as e:
            Out.error(e)
            # Exit on API error
            exit(-1)

    # Returns current highest available block
    def getBlockNums(self):
        retVal = self.trezor.get("status")
        if retVal:
            return retVal.get("blockbook", {}).get("bestHeight")
        # Invalid value
        return None

    # Collects all transactions made by given addresses
    def getAccountTxs(self, addr, results:list):
        getTx = lambda results, addr, interval: results.extend(
            gettxAddrs(
                self.trezor.get(f"v2/address/{addr}", params={
                    "from"    : interval[0],
                    "to"      : interval[1],
                    "details" : "txslight"
                }),
                addr,
                results
            )
        )
        step = 1000
        # Generate functions list
        funcList = [
            getTx(results, addr, (start, start + (step - 1)))
                for start in range(0, self.getBlockNums(), step)
        ]
        # Divide each segment into thread
        startThreading(funcList)
# End of ServerHandler class
