"""MongoDB database manager with singleton pattern."""
from pymongo import MongoClient, ASCENDING, DESCENDING
from config.app import CONNECTION_STRING, DATABASE_NAME


class DatabaseManager:
    """Singleton MongoDB database manager."""

    _client = None
    _db = None

    @classmethod
    def _get_db(cls):
        if cls._db is None:
            cls._client = MongoClient(CONNECTION_STRING)
            cls._db = cls._client[DATABASE_NAME]
            cls._ensure_indexes()
        return cls._db

    @classmethod
    def _ensure_indexes(cls):
        """Create indexes on first connection."""
        db = cls._db
        db.users.create_index("email", unique=True)
        db.moods.create_index([("user_id", ASCENDING), ("logged_date", ASCENDING)], unique=True)
        db.moods.create_index("user_id")
        db.moods.create_index("logged_date")

    @classmethod
    def get_collection(cls, name: str):
        """Get a MongoDB collection."""
        return cls._get_db()[name]

    @classmethod
    def ping(cls) -> bool:
        """Check database connectivity."""
        try:
            cls._get_db().command("ping")
            return True
        except Exception:
            return False
