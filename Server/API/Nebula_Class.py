# Imports
from .Base_Class import BaseAPI, yaml, Out
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

# Class handling interaction with NebulaGraph
class NebulaAPI(BaseAPI):
    def __init__(self, file="configFile.yaml"):
        # Open config file
        self.conf = yaml.safe_load(self.openConfigFile(file))["nebula"]
        # Init parent class
        super().__init__()
        # Create member to store current Nebula session (if any)
        self.nebula = None

    # Setter for Nebula session
    def setNebulaSession(self, session):
        self.nebula = session

    # Init connection to Nebula instance and return pool to use
    def getNebulaPool(self):
        try:
            # Define config
            config = Config()
            # Init connection pool
            connection_pool = ConnectionPool()
            # Check if connection to pool is valid
            if not connection_pool.init([(self.conf["addr"], self.conf["port"])], config):
                raise Exception("connection_pool.init() returned False")
            return connection_pool
        except Exception as e:
            Out.error(f"Error while creating Nebula connection: {e}")
            exit(-1)

    # Helper to catch eventual execution errors
    def ExecNebulaCommand(self, command=""):
        # Ensure we have valid session
        assert self.nebula
        resp = self.nebula.execute(command)
        # Check for execution errors
        assert resp.is_succeeded(), resp.error_msg()
        # Return result (for compatibility reasons)
        return resp

    def toArrayTransform(self, result, pivot):
        if result.is_empty():
            return []
        # Get values for specified pivot column
        columnVals = result.column_values(pivot)
        # Contains single element, return it
        if len(columnVals) == 1:
            return columnVals[0].as_string()
        # Create list and return it
        return [val.as_string() for val in result.column_values(pivot)]

    def getAddrsOfType(self, addrType=""):
        # Make query to get all addresses of given type
        result = self.ExecNebulaCommand(
            f'MATCH (v:address) WHERE v.address.type == "{addrType}" RETURN id(v)'
        )
        # Handle result
        return self.toArrayTransform(result, "id(v)")
# NebulaAPI class end
