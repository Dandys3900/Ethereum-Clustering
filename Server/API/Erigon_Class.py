# Imports
import os
from .Base_Class import *

# Class handling interaction with Erigon API
class ErigonAPI(BaseAPI):
    def __init__(self, file="configFile.yaml"):
        # Open config file
        conf = yaml.safe_load(self.openConfigFile(file))["erigon"]
        # Init parent class
        super().__init__(conf["url"], conf["header"])
# ErigonAPI class end
