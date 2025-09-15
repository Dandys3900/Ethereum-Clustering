# Imports
import shelve, atexit

# Static class for accessing shelve cache
class Cache:
    db     = None
    dbPath = "cache.db"

    @classmethod
    def init(cls):
        if cls.db is None:
            cls.db = shelve.open(cls.dbPath, writeback=True)
            # Ensure cleanup on end
            atexit.register(cls.close)

    @classmethod
    def set(cls, key, value):
        cls.init()
        cls.db[key] = value

    @classmethod
    def get(cls, key, default=None):
        cls.init()
        return cls.db.get(key, default)

    @classmethod
    def delete(cls, key):
        cls.init()
        if key in cls.db:
            del cls.db[key]

    @classmethod
    def close(cls):
        if cls.db is not None:
            cls.db.close()
            cls.db = None
# End of Cache class
