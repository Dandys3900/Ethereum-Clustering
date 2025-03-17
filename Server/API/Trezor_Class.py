# Imports
from .Base_Class import *
from aiohttp import ClientSession
from dateutil import parser

# Class handling interaction with Trezor Blockbook API
class TrezorAPI(BaseAPI):
    def __init__(self, file="configFile.yaml"):
        # Open config file
        conf = yaml.safe_load(self.openConfigFile(file))["trezor"]
        # Init parent class
        super().__init__(conf["url"])

    # Returns latest sync date among with best block
    async def getCurrentSyncDate(self):
        async with ClientSession() as session:
            response = await (self.get(session, "api/status"))

            # Check if valid server response
            if not response or (response := response.get("blockbook", {})) == {}:
                return ";"

            return (f"{response.get("bestHeight", "")};\
                      {parser.isoparse(response.get("lastBlockTime", "")).strftime("%Y-%m-%d, %H:%M")}")
# TrezorAPI class end
