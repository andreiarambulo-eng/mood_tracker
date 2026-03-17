"""MongoDB connection manager with singleton pattern."""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config.app import CONNECTION_STRING, DATABASE_NAME
import time


class MongoDBManager:
    """Singleton MongoDB connection manager."""

    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._connect()
        return cls._instance

    @classmethod
    def _connect(cls, max_retries=5, retry_delay=5):
        """Establish MongoDB connection with retry logic."""
        for attempt in range(max_retries):
            try:
                cls._client = MongoClient(
                    CONNECTION_STRING,
                    serverSelectionTimeoutMS=5000
                )
                cls._client.admin.command('ping')
                cls._db = cls._client[DATABASE_NAME]
                print(f"Connected to MongoDB: {DATABASE_NAME}")
                return
            except ConnectionFailure:
                if attempt < max_retries - 1:
                    print(f"MongoDB connection attempt {attempt + 1} failed. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    raise

    @classmethod
    def get_db(cls):
        """Get database instance."""
        if cls._db is None:
            cls()
        return cls._db

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a collection by name."""
        db = cls.get_db()
        return db[collection_name]

    @classmethod
    def ping(cls) -> bool:
        """Check MongoDB connectivity."""
        try:
            if cls._client is None:
                cls()
            cls._client.admin.command('ping')
            return True
        except Exception:
            return False
