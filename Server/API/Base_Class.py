# Imports
import requests, urllib3, yaml
from Helpers import Out

# Suppress InsecureRequestWarning related to session.verify set to False
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

# Base class for API interaction
class BaseAPI():
    def __init__(self, url="", header={}):
        self.url     = url
        self.headers = header
        self.session = requests.Session()
        # NOTE: Disabled for dev purposes!
        self.session.verify = False
        # Check connection
        self.checkConnection()

    # Base function for connection checking
    # NOTE: Raises exception if not overriden in child classes
    def checkConnection(self):
        raise NotImplementedError("Missing method body")

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
# BaseAPI class end
