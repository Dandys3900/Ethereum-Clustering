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
        # Set timeout for each GET request
        self.timeout = aiohttp.ClientTimeout(
            total        = 1080,
            connect      = 120,
            sock_connect = 120,
            sock_read    = 780
        )

    # Try to open and load config
    def openConfigFile(self, fileName=""):
        # Get path to parent dir of this file (Server/)
        script_dir = Path(__file__).parent
        # Construct absolute path to customer config file
        file_path = script_dir / fileName
        # Load config file
        return open(file_path, "r")
# BaseAPI class end
