# Imports
import urllib3, yaml, aiohttp
from asyncio.exceptions import TimeoutError
from Helpers import Out
from pathlib import Path

# Suppress InsecureRequestWarning related to session.verify set to False
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

# Base class for API interaction
class BaseAPI():
    def __init__(self, url="", header={}):
        # Declare connection variables
        self.url     = url
        self.headers = header
        # Set timeout for each GET request to 5mins
        self.timeout = aiohttp.ClientTimeout(total=300)

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

    # Try to open and load config
    def openConfigFile(self, fileName=""):
        # Get path to parent dir of this file (Server/)
        script_dir = Path(__file__).parent
        # Construct absolute path to customer config file
        file_path = script_dir / fileName
        # Load config file
        return open(file_path, "r")
# BaseAPI class end
