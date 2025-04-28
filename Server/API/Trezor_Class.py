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
        self.semaphore = asyncio.Semaphore(30)
        # Block sending GET() when session is being re-creating
        self.sessionCreating = asyncio.Event()
        self.sessionCreating.set()

    # Returns latest sync date among with best block
    async def getCurrentSyncDate(self):
        async with SessionManager() as session:
            # Extract needed items
            bestHeight    = await anext(self.get(session, "api/status", key="blockbook.bestHeight"))
            lastBlockTime = await anext(self.get(session, "api/status", key="blockbook.lastBlockTime"))
            # Check if valid server response
            if not bestHeight or not lastBlockTime:
                return ";"

            return (f"{bestHeight};\
                      {parser.isoparse(lastBlockTime).strftime("%Y-%m-%d, %H:%M")}")

    async def get(self, session=None, endpoint="", params=None, key=None):
        # Construct target URL
        url = self.url + endpoint
        async with self.semaphore:
            for attempt in range(1, 4):
                try:
                    await self.sessionCreating.wait()
                    currentSession = await session.getSession()
                    async with currentSession.get(url, headers=self.headers, params=params, timeout=self.timeout, ssl=False) as response:
                        # Check response status
                        response.raise_for_status()
                        # Check for invalid response type
                        if response.content_type != "application/json":
                            continue

                        # Try to get key's value
                        if key:
                            async for prefix, _, value in ijson.parse_async(response.content):
                                if prefix == key:
                                    yield value
                        else: # Return response content stream
                            async for tx in ijson.items_async(response.content, "transactions.item"):
                                yield tx
                        break
                except aiohttp.ClientConnectorError as e:
                    Out.error(f"get(): Connector error: {e}, remaining attemps {3 - attempt}")
                    # Other coroutine already re-creating session, skip
                    if not session.creatingSession.is_set():
                        continue
                    # Block other coroutines from sending GET()
                    self.sessionCreating.clear()
                    # Re-create session
                    await session.createSession()
                    self.sessionCreating.set()
                except (Exception, asyncio.TimeoutError, asyncio.CancelledError) as e:
                    # Output exception
                    Out.error(f"get(): {e}, remaining attemps {3 - attempt}")
        # End of stream
        yield None
# TrezorAPI class end
