# Imports
import ijson, asyncio
from .Base_Class import *
from ..Session import SessionManager
from dateutil import parser

# Class handling interaction with Trezor Blockbook API
class TrezorAPI(BaseAPI):
    def __init__(self, file="configFile.yaml"):
        # Open config file
        conf = yaml.safe_load(self.openConfigFile(file))["trezor"]
        # Init parent class
        super().__init__(conf["url"])
        self.semaphore = asyncio.Semaphore(40)

    # Returns latest sync date among with best block
    async def getCurrentSyncDate(self):
        async with SessionManager() as session:
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
        async with self.semaphore:
            try:
                currentSession = await session.get()
                async with currentSession.get(url, headers=self.headers, params=params, timeout=self.timeout) as response:
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
                Out.error(f"get(): {e}")
                return None

    # Get transactions for given address
    async def getJSONStream(self, session=None, endpoint="", params=None, key=None, queue=None):
        # Construct target URL
        url = self.url + endpoint
        for _ in range(0, 3):
            async with self.semaphore:
                try:
                    currentSession = await session.get()
                    async with currentSession.get(url, headers=self.headers, params=params, timeout=self.timeout) as response:
                        # Check response status
                        response.raise_for_status()
                        # Check for invalid response type
                        if response.content_type != "application/json":
                            continue

                        # Try to get key's value
                        if key:
                            async for prefix, _, value in ijson.parse_async(response.content):
                                if prefix == key:
                                    return value
                        else: # Return response content stream
                            async for tx in ijson.items_async(response.content, "transactions.item"):
                                await queue.put(tx)
                        break
                except TimeoutError:
                    Out.warning(f"Timeout for GET request, trying again")
                except Exception as e:
                    # Output exception
                    Out.error(f"getJSONStream(): {e}")
        # Signal end of queue
        if queue:
            await queue.put(None)
# TrezorAPI class end
