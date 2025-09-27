from typing import Optional
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database
from app.db.interfaces.database_interface import DatabaseInterface
from app.db.interfaces.collection_interface import CollectionInterface
from .mongodb_collection import MongoDBCollection
import logging

logger = logging.getLogger(__name__)


class MongoDBAdapter(DatabaseInterface):
    """MongoDB implementation of DatabaseInterface."""

    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None

    def connect(self, connection_string: str, database_name: str) -> None:
        """Connect to the MongoDB database."""
        try:
            self.client = MongoClient(connection_string, server_api=ServerApi('1'))
            self.database = self.client[database_name]

            # Test the connection
            self.database.command('ping')
            logger.info(f"Successfully connected to MongoDB database: {database_name}")

            # Create indexes after successful connection
            self.create_indexes()

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from the MongoDB database."""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            logger.info("Disconnected from MongoDB")

    def get_collection(self, collection_name: str) -> CollectionInterface:
        """Get a collection interface."""
        if not self.database:
            raise ConnectionError("MongoDB is not connected. Call connect() first.")

        mongodb_collection = self.database[collection_name]
        return MongoDBCollection(mongodb_collection)

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

            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise

    def health_check(self) -> bool:
        """Check if the database connection is healthy."""
        try:
            if not self.database:
                return False
            self.database.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False