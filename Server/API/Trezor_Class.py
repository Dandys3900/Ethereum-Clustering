# Imports
from .Base_Class import *

# Class handling interaction with Trezor Blockbook API
class TrezorAPI(BaseAPI):
    def __init__(self, file="configFile.yaml"):
        # Open config file
        conf = yaml.safe_load(self.openConfigFile(file))["trezor"]
        # Init parent class
        super().__init__(conf["url"])
        # Check connection
        self.checkConnection()

    # Initially tests connection with API
    def checkConnection(self):
        if self.get("api"):
            Out.success("Connection to Trezor API is active")
        else:
            raise Exception("Failed connection to Trezor API")
# TrezorAPI class end
