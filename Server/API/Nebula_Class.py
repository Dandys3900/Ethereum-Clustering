# Imports
import atexit
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
        # Create Nebula session
        self.session = self.getNebulaPool().get_session('root', 'nebula')
        # Ensure cleanup at exit
        atexit.register(self.session.release)
        atexit.register(self.getNebulaPool().close)

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

    # Handles adding new node to graph
    def addNodeToGraph(self, addr="", addrName="", parentAddr="", nodeType="", amount=0.0):
        # Add node (vertex) to graph
        self.ExecNebulaCommand(
            f'INSERT VERTEX IF NOT EXISTS address(name, type) VALUES "{addr}": ("{addrName}", "{nodeType}")'
        )
        # Parent address is given so create a path to it
        if parentAddr != "":
            self.ExecNebulaCommand(
                f'UPSERT EDGE on linked_to "{addr}"->"{parentAddr}" SET amount = amount + {amount}'
            )

    # Helper to catch eventual execution errors
    def ExecNebulaCommand(self, command=""):
        # Ensure we have valid session
        assert self.session
        resp = self.session.execute(command)
        # Check for execution errors
        assert resp.is_succeeded(), resp.error_msg()
        # Return result (for compatibility reasons)
        return resp

    def toArrayTransform(self, result, pivot):
        if result.is_empty():
            return []
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
