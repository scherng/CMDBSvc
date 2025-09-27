from typing import Dict
from app.db.interfaces.database_interface import DatabaseInterface
from app.db.interfaces.collection_interface import CollectionInterface
from .memory_collection import MemoryCollection
import logging

logger = logging.getLogger(__name__)


class MemoryAdapter(DatabaseInterface):
    """In-memory implementation of DatabaseInterface for testing."""

    def __init__(self):
        self._collections: Dict[str, MemoryCollection] = {}
        self._connected = False
        self._database_name = ""

    def connect(self, connection_string: str, database_name: str) -> None:
        """Connect to the in-memory database."""
        self._database_name = database_name
        self._connected = True
        logger.info(f"Connected to in-memory database: {database_name}")

        # Create indexes after connection
        self.create_indexes()

    def disconnect(self) -> None:
        """Disconnect from the in-memory database."""
        self._collections.clear()
        self._connected = False
        self._database_name = ""
        logger.info("Disconnected from in-memory database")

    def get_collection(self, collection_name: str) -> CollectionInterface:
        """Get a collection interface."""
        if not self._connected:
            raise ConnectionError("In-memory database is not connected. Call connect() first.")

        if collection_name not in self._collections:
            self._collections[collection_name] = MemoryCollection(collection_name)

        return self._collections[collection_name]

    def create_indexes(self) -> None:
        """Create necessary indexes for the database."""
        try:
            # Create indexes for users collection
            users_collection = self.get_collection("users")
            users_collection.create_index("ci_id", unique=True)
            users_collection.create_index("user_id", unique=True)
            users_collection.create_index("name")

            # Create indexes for applications collection
            apps_collection = self.get_collection("applications")
            apps_collection.create_index("ci_id", unique=True)
            apps_collection.create_index("app_id", unique=True)
            apps_collection.create_index("name")

            logger.info("In-memory database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating in-memory indexes: {e}")
            raise

    def health_check(self) -> bool:
        """Check if the database connection is healthy."""
        return self._connected

    def clear_all_collections(self) -> None:
        """Clear all collections (for testing)."""
        for collection in self._collections.values():
            collection.clear()
        logger.info("All in-memory collections cleared")