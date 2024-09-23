# Imports
import os
from .Base_Class import *

# Class handling interaction with Erigon API
class ErigonAPI(BaseAPI):
    def __init__(self, file="configFile.yaml"):
        # Get elements for Sentinel
        conf = yaml.safe_load(file)["erigon"]
        # Init parent class
        super().__init__(conf["url"], conf["header"])

    # Initially tests connection with API
    def checkConnection(self):
        if (os.system("ping " + self.url)) == 0:
            Out.success("Connection to Erigon API is active")
        else:
            Out.error("Failed connection to Erigon API")
# ErigonAPI class end
