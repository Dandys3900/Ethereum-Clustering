# Imports
from asyncio import Event
from Helpers import Out
from aiohttp import ClientSession

class SessionManager:
    def __init__(self, timeout=None):
        self.timeout = timeout
        # Init session to None
        self.session = None
        # Flag if session is being created
        self.creatingSession = Event()
        self.creatingSession.set()

    # Method trigger by entering context manager
    async def __aenter__(self):
        # Ensure session is initially created
        await self.createSession()
        return self

    # Method trigger by leaving context manager
    async def __aexit__(self, *args):
        await self.closeSession()

    # Getter for session object, if current closed, create and return new one
    async def getSession(self):
        # Don't get session if being currently created
        await self.creatingSession.wait()

        if not self.session or self.session.closed:
            # Create new one and close existing
            await self.createSession()
        return self.session

    async def createSession(self):
        self.creatingSession.clear()
        # Ensure current session is closed
        await self.closeSession()
        # Create new one
        self.session = ClientSession(timeout=self.timeout)
        self.creatingSession.set()
        Out.blank("Created new ClientSession")

    async def closeSession(self):
        try:
            assert self.session
            await self.session.close()
            self.session = None
            Out.blank("Closed current ClientSession")
        except:
            pass
# End of SessionManager class
