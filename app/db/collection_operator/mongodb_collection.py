from typing import Any, Dict, List, Optional
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from app.db.collection_operator.collection_interface import CollectionInterface
from app.db.collection_operator.cursor_interface import CursorInterface, MongoDBCursor
import logging

logger = logging.getLogger(__name__)


class MongoDBCollection(CollectionInterface):
    """MongoDB implementation of CollectionInterface."""

    def __init__(self, collection: Collection):
        self._collection = collection

    def insert_one(self, document: Dict[str, Any]) -> InsertOneResult:
        """Insert a single document and return the result."""
        return self._collection.insert_one(document)

    def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document matching the filter."""
        return self._collection.find_one(filter_dict)

    def find(self, filter_dict: Optional[Dict[str, Any]] = None) -> CursorInterface:
        """Find all documents matching the filter and return a cursor."""
        filter_dict = filter_dict or {}
        mongodb_cursor = self._collection.find(filter_dict)
        return MongoDBCursor(mongodb_cursor)

    def create_index(self, field: str, unique: bool = False) -> None:
        """Create an index on the specified field."""
        try:
            self._collection.create_index(field, unique=unique)
            logger.info(f"Index created on field '{field}' (unique={unique})")
        except Exception as e:
            logger.error(f"Error creating index on field '{field}': {e}")
            raise

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute an aggregation pipeline and return the results."""
        try:
            cursor = self._collection.aggregate(pipeline)
            results = list(cursor)
            logger.info(f"Aggregation pipeline executed, returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error executing aggregation pipeline: {e}")
            raise

    def count_documents(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching the filter."""
        try:
            filter_dict = filter_dict or {}
            count = self._collection.count_documents(filter_dict)
            logger.info(f"Document count query executed, found {count} documents")
            return count
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            raise