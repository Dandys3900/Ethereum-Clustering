# Imports
import threading
from .CustomOutput import Out

# Custom dictionary class
class custDict(dict):
    # Init thread lock to ensure thread-safety
    lock = threading.Lock()

    # Override dict.get() method to throw a warning when trying to access non-existing key value
    def get(self, key, default=None):
        with self.lock:
            if key not in self:
                Out.warning(f"Using non-existing key: {key}")
            return super().get(key, default)
# End of custDict class
