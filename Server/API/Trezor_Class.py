# Imports
import ijson
from .Base_Class import *
from aiohttp import ClientSession
from dateutil import parser

# Class handling interaction with Trezor Blockbook API
class TrezorAPI(BaseAPI):
    def __init__(self, file="configFile.yaml"):
        # Open config file
        conf = yaml.safe_load(self.openConfigFile(file))["trezor"]
        # Init parent class
        super().__init__(conf["url"])

    # Returns latest sync date among with best block
    async def getCurrentSyncDate(self):
        async with ClientSession() as session:
            response = await (self.get(session, "api/status"))

            # Check if valid server response
            if not response or (response := response.get("blockbook", {})) == {}:
                return ";"

            return (f"{response.get("bestHeight", "")};\
                      {parser.isoparse(response.get("lastBlockTime", "")).strftime("%Y-%m-%d, %H:%M")}")

    # Handle GET request to given API endpoint
    async def get(self, session=None, endpoint="", params=None, retryCount=3):
        # Construct target URL
        url = self.url + endpoint
        try:
            async with session.get(url, headers=self.headers, params=params, timeout=self.timeout) as response:
                # Check response status
                response.raise_for_status()
                # Return response content
                if response.content_type == 'application/json':
                    return await response.json()
                return None
        except TimeoutError:
            # Timeout happened 3 times in row, return None
            if retryCount == 1:
                return None
            Out.warning(f"Timeout for GET request, remaining tries: {(retryCount - 1)}")
            # Repeat request with decremented retryCount
            return await self.get(session, endpoint, params, (retryCount - 1))
        except Exception as e:
            # Output exception
            Out.error(e)
            return None

    # Get transactions for given address
    async def getAddrTxs(self, session=None, endpoint="", params=None, retryCount=3):
        # Construct target URL
        url = self.url + endpoint
        while retryCount > 0:
            try:
                async with session.get(url, headers=self.headers, params=params, timeout=self.timeout) as response:
                    # Check response status
                    response.raise_for_status()

                    # Return response content
                    if response.content_type == "application/json":
                        async for tx in ijson.items_async(response.content, "transactions.item"):
                            yield tx
                    break
            except TimeoutError:
                retryCount -= 1
                Out.warning(f"Timeout for GET request, remaining tries: {retryCount}")
            except Exception as e:
                # Output exception
                Out.error(e)
                break
# TrezorAPI class end
