from enum import Enum
from typing import Optional
from app.db.interfaces.database_interface import DatabaseInterface
from app.db.adapters.mongodb_adapter import MongoDBAdapter
from app.db.adapters.memory_adapter import MemoryAdapter
import logging

logger = logging.getLogger(__name__)


class DatabaseType(str, Enum):
    MONGODB = "mongodb"
    MEMORY = "memory"


class DatabaseFactory:
    """Factory for creating database adapters."""

    _instance: Optional[DatabaseInterface] = None
    _database_type: Optional[DatabaseType] = None

    @classmethod
    def create_database(cls, db_type: DatabaseType) -> DatabaseInterface:
        """Create a database adapter based on the specified type."""
        if db_type == DatabaseType.MONGODB:
            return MongoDBAdapter()
        elif db_type == DatabaseType.MEMORY:
            return MemoryAdapter()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    @classmethod
    def initialize(cls, db_type: DatabaseType, connection_string: str, database_name: str) -> None:
        """Initialize the global database instance."""
        if cls._instance is not None:
            logger.warning("Database already initialized. Disconnecting previous instance.")
            cls._instance.disconnect()

        cls._instance = cls.create_database(db_type)
        cls._database_type = db_type
        cls._instance.connect(connection_string, database_name)
        logger.info(f"Database initialized with type: {db_type}")

    @classmethod
    def get_database(cls) -> DatabaseInterface:
        """Get the current database instance."""
        if cls._instance is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return cls._instance

    @classmethod
    def disconnect(cls) -> None:
        """Disconnect the current database instance."""
        if cls._instance is not None:
            cls._instance.disconnect()
            cls._instance = None
            cls._database_type = None
            logger.info("Database disconnected")

    @classmethod
    def get_database_type(cls) -> Optional[DatabaseType]:
        """Get the current database type."""
        return cls._database_type

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if the database is initialized."""
        return cls._instance is not None