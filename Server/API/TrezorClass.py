# Imports
from .BaseClass import *

# Class handling interaction with Trezor Blockbook API
class TrezorAPI(BaseAPI):
    def __init__(self, file="configFile.yaml"):
        # Get elements for Sentinel
        conf = yaml.safe_load(file)["trezor"]
        # Init parent class
        super().__init__(conf["url"])

    # Initially tests connection with API
    def checkConnection(self):
        if self.get("api"):
            Out.success("Connection to Trezor API is active")
        else:
            Out.error("Failed connection to Trezor API")
# TrezorAPI class end
