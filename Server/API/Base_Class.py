# Imports
import requests, urllib3, yaml, aiohttp
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
        # TODO: Set timeout for each GET request to 10s
        self.timeout = aiohttp.ClientTimeout(total=10)

    # Handle GET request to given API endpoint
    async def get(self, session=None, endpoint="", params=None):
        # Construct target URL
        url = self.url + endpoint
        try:
            async with session.get(url, headers=self.headers, params=params) as response:
                # Check response status
                response.raise_for_status()
                # Return response content
                if response.content_type == 'application/json':
                    return await response.json()
                return None
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
