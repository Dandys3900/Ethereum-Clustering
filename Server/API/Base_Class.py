# Imports
import requests, urllib3, yaml
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
        self.session = requests.Session()
        self.session.verify = False

    # Handle GET request to given API endpoint
    def get(self, endpoint="", params=None):
        # Construct target URL
        url = self.url + endpoint
        try:
            response = self.session.get(
                url,
                headers=self.headers,
                params=params
            )
            # Check response status
            response.raise_for_status()
            # Return the response if any
            return response.json() if (response.content and response.json()) else None
        except Exception as e:
            # Output exception
            Out.error(e)
            return None

    # Handle POST request to given API endpoint
    def post(self, endpoint="", json=None, data=None, auth=None):
        # Construct target URL
        url = self.url + endpoint
        try:
            response = self.session.post(
                url,
                headers=self.headers,
                json=json,
                data=data,
                auth=auth
            )
            # Check response status
            response.raise_for_status()
            # Return the response if any
            return response.json() if (response.content and response.json()) else None
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
