"""MongoDB connection manager."""
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from app.core.config import settings


class MongoClientManager:
    """Singleton MongoDB client manager."""
    
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize MongoDB client and database connection."""
        if cls._client is None:
            cls._client = MongoClient(settings.mongodb_uri)
            cls._db = cls._client[settings.mongodb_db]
    
    @classmethod
    def close(cls) -> None:
        """Close MongoDB connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._db = None
    
    @classmethod
    def get_db(cls) -> Database:
        """Get database instance. Initializes if needed."""
        if cls._db is None:
            cls.initialize()
        return cls._db
    
    @classmethod
    def get_collection(cls, name: str) -> Collection:
        """Get collection by name."""
        db = cls.get_db()
        return db[name]


# Convenience functions
def get_db() -> Database:
    """Get database instance."""
    return MongoClientManager.get_db()


def get_collection(name: str) -> Collection:
    """Get collection by name."""
    return MongoClientManager.get_collection(name)
