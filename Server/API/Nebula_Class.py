###################################
# @file Nebula_Class.py
# @author Tomáš Daniel (xdanie14)
# @brief Class for interaction with database client.
###################################

# Imports
import atexit, time
from .Base_Class import BaseAPI, yaml, Out
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

# Class handling interaction with NebulaGraph
class NebulaAPI(BaseAPI):
    def __init__(self, file="configFile.yaml", targetSpace="EthereumClustering"):
        time.sleep(40)
        # Open config file
        self.conf = yaml.safe_load(self.openConfigFile(file))["nebula"]
        # Init parent class
        super().__init__()
        # Create Nebula session
        self.targetSpace    = targetSpace
        self.connectionPool = None
        self.session        = None

        self.getNebulaPool()
        self.ensureConnect(skipSpaceSelection=True)
        self.createSpace()
        # Ensure index is used for querying
        self.execNebulaCommand('REBUILD TAG INDEX addrs_index')
        Out.blank("Tag index rebuild done")

        # Ensure cleanup at exit
        atexit.register(self.closeConnection)

    # Init connection to Nebula instance and return pool to use
    def getNebulaPool(self):
        try:
            config = Config()
            # Init connection pool
            self.connectionPool = ConnectionPool()
            # Check if connection to pool is valid
            if not self.connectionPool.init([(self.conf["addr"], self.conf["port"])], config):
                raise Exception("connectionPool.init() returned False")
        except Exception as e:
            Out.error(f"Error while creating Nebula connection pool: {e}")
            exit(-1)

    def isSessionValid(self):
        try:
            result = self.session.execute("YIELD 1")
            return result.is_succeeded()
        except Exception:
            return False

    # Makes sure connection is valid, otherwise creates new one
    def ensureConnect(self, skipSpaceSelection=False):
        try:
            # Create session
            if not self.session or not self.isSessionValid():
                # Release previous session
                if self.session:
                    self.session.release()
                Out.blank("Created new Nebula session")
                self.session = self.connectionPool.get_session("root", "nebula")
                if not skipSpaceSelection:
                    # Re-select space
                    self.execNebulaCommand(f'USE {self.targetSpace}')
        except Exception as e:
            Out.error(f"Error while creating Nebula connection: {e}")
            exit(-1)

    # Closes and release nebula session and pool
    def closeConnection(self):
        try:
            if self.session:
                self.session.release()
            if self.connectionPool:
                self.connectionPool.close()
        except Exception as e:
            Out.error(f"Error while closing connection: {e}")

    # Check if given Nebula object (space, index, edge) already exists
    def objectExists(self, assertName, objName, name="Name"):
        result = self.execNebulaCommand(f'SHOW {objName}')
        if result and not result.is_empty():
            return assertName in [val.as_string() for val in result.column_values(name)]
        return False

    # Ensures all spaces are already present
    def createSpace(self):
        if self.objectExists(self.targetSpace, "SPACES"):
            # Space exists
            Out.blank(f"Space: {self.targetSpace} already exists")
        else:
            # Create new space
            Out.warning(f"Creating new space: {self.targetSpace}")
            self.execNebulaCommand(f'CREATE SPACE {self.targetSpace} (partition_num=10, replica_factor=1, vid_type=FIXED_STRING(42))')
            # Wait 20s to make sure space is created properly
            time.sleep(20)
            Out.success(f"Space {self.targetSpace} created succesfully")

        # Use created space
        self.execNebulaCommand(f'USE {self.targetSpace}')

        # Create necessary index, tags and edges
        if not (skipChange := self.objectExists("address", "TAGS")):
            Out.warning("Creating needed tag(s)")
            self.execNebulaCommand('CREATE TAG address(name string, type string)')
            Out.warning("Creating needed index(s)")
            self.execNebulaCommand('CREATE TAG INDEX addrs_index ON address(type(10))')

        if not (skipChange := self.objectExists("linked_to", "EDGES")):
            Out.warning("Creating needed edge(s)")
            self.execNebulaCommand('CREATE EDGE linked_to(amount float DEFAULT 0.0, txs string DEFAULT "")')

        # Ensure new objects are properly made
        if not skipChange:
            time.sleep(20)
            Out.success(f"All needed components created succesfully")

    # Handles adding new node to graph
    async def addNodeToGraph(self, addr="", addrName="", parentAddr="", nodeType="", txParams="", amount=0.0):
        print(f"Adding type: {nodeType} ; name: {addrName} ; {addr}")
        # Add node (vertex) to graph
        self.execNebulaCommand(
            f'INSERT VERTEX IF NOT EXISTS address(name, type) VALUES "{addr}": ("{addrName}", "{nodeType}")'
        )
        # Parent address is given so create a path to it
        if parentAddr != "":
            self.execNebulaCommand(
                f'UPSERT EDGE on linked_to "{addr}"->"{parentAddr}" SET amount = amount + {amount}, txs = txs + "{txParams}"'
            )

    # Helper to catch eventual execution errors
    def execNebulaCommand(self, command="", cnt=1):
        try:
            assert self.session
            resp = self.session.execute(command)
            # Check for execution errors
            assert resp.is_succeeded(), resp.error_msg()
            # Return result (required in some use-cases)
            return resp
        except Exception as e:
            Out.error(f"execNebulaCommand(): {e}")
            # Tried again with new session, but still fails, return
            if cnt == 0:
                return None
            # Ensure we have valid session
            self.ensureConnect()
            return self.execNebulaCommand(command, cnt=(cnt-1))

    def toArrayTransform(self, result=None, pivot=""):
        if not result or result.is_empty():
            return []
        # Create list and return it
        return [val.cast_primitive() for val in result.column_values(pivot)]

    def getAddrsOfType(self, addrType="", targetParam="id(v)"):
        # Make query to get all addresses of given type
        result = self.execNebulaCommand(
            f'MATCH (v:address) WHERE v.address.type == "{addrType}" RETURN {targetParam}'
        )
        # Handle result
        return self.toArrayTransform(result, targetParam)
# NebulaAPI class end
