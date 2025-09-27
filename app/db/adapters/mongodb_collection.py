from typing import Any, Dict, List, Optional
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from app.db.interfaces.collection_interface import CollectionInterface
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

    def find(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Find all documents matching the filter."""
        filter_dict = filter_dict or {}
        return list(self._collection.find(filter_dict))

    def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> UpdateResult:
        """Update a single document and return the result."""
        return self._collection.update_one(filter_dict, update_dict)

    def update_many(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> UpdateResult:
        """Update multiple documents and return the result."""
        return self._collection.update_many(filter_dict, update_dict)

    def delete_one(self, filter_dict: Dict[str, Any]) -> DeleteResult:
        """Delete a single document and return the result."""
        return self._collection.delete_one(filter_dict)

    def delete_many(self, filter_dict: Dict[str, Any]) -> DeleteResult:
        """Delete multiple documents and return the result."""
        return self._collection.delete_many(filter_dict)

    def create_index(self, field: str, unique: bool = False) -> None:
        """Create an index on the specified field."""
        try:
            self._collection.create_index(field, unique=unique)
            logger.info(f"Index created on field '{field}' (unique={unique})")
        except Exception as e:
            logger.error(f"Error creating index on field '{field}': {e}")
            raise