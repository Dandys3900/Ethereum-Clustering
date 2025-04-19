# Imports
from aiohttp import ClientSession

class SessionManager:
    def __init__(self, timeout=None):
        self.timeout = timeout
        # Init session to None
        self.session = None

    # Method trigger by context manager
    async def __aenter__(self):
        # Ensure session is created
        self.session = ClientSession(timeout=self.timeout)
        return self

    # Method trigger by leaving context manager
    async def __aexit__(self, *args):
        await self.session.close()

    # Getter for session object, if current closed, create and return new one
    async def get(self):
        if self.session.closed:
            self.session = ClientSession(timeout=self.timeout)
        return self.session
# End of SessionManager class
