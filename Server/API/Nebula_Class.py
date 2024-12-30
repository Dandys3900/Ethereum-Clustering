# Imports
import atexit, time
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

    # Check if given Nebula object (space, index, edge) already exists
    def objectExists(self, assertName, objName):
        result = self.ExecNebulaCommand(f'SHOW {objName}')
        if not result.is_empty():
            return assertName in [val.as_string() for val in result.column_values("Name")]
        return False

    # Ensures all spaces are already present
    def createSpace(self, spaceName=""):
        # Create new space
        if not self.objectExists(spaceName, "SPACES"):
            Out.warning(f"Creating new space: {spaceName}")
            self.ExecNebulaCommand(f'CREATE SPACE IF NOT EXISTS {spaceName} (partition_num=10, replica_factor=1, vid_type=FIXED_STRING(42))')
            # Wait 20s to make sure space is created properly
            time.sleep(20)
            Out.success(f"Space {spaceName} created succesfully")

        # Use defined space
        self.ExecNebulaCommand(f'USE {spaceName}')

        # Create necessary index, tags and edges
        if not (noChangeMade := self.objectExists("address", "TAGS")):
            Out.warning("Creating needed tag(s)")
            self.ExecNebulaCommand('CREATE TAG IF NOT EXISTS address(name string, type string)')
            Out.warning("Creating needed index(s)")
            self.ExecNebulaCommand('CREATE TAG INDEX IF NOT EXISTS addrs_index ON address(type(10))')

        if not (noChangeMade := self.objectExists("linked_to", "EDGES")):
            Out.warning("Creating needed edge(s)")
            self.ExecNebulaCommand('CREATE EDGE IF NOT EXISTS linked_to(amount float DEFAULT 0.0)')

        # Ensure new objects are properly made
        if not noChangeMade:
            time.sleep(20)
            Out.success(f"Tags and index created succesfully")

    # Handles adding new node to graph
    async def addNodeToGraph(self, addr="", addrName="", parentAddr="", nodeType="", amount=0.0):
        print(f"Adding {addr}")
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
