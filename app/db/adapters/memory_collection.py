from typing import Any, Dict, List, Optional, Set
from copy import deepcopy
from app.db.interfaces.collection_interface import CollectionInterface
import uuid
import logging

logger = logging.getLogger(__name__)


class UpdateResult:
    """Mock UpdateResult for in-memory operations."""
    def __init__(self, matched_count: int, modified_count: int):
        self.matched_count = matched_count
        self.modified_count = modified_count


class DeleteResult:
    """Mock DeleteResult for in-memory operations."""
    def __init__(self, deleted_count: int):
        self.deleted_count = deleted_count


class InsertOneResult:
    """Mock InsertOneResult for in-memory operations."""
    def __init__(self, inserted_id: str):
        self.inserted_id = inserted_id


class MemoryCollection(CollectionInterface):
    """In-memory implementation of CollectionInterface for testing."""

    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._indexes: Dict[str, Set[Any]] = {}
        self._unique_indexes: Set[str] = set()

    def insert_one(self, document: Dict[str, Any]) -> InsertOneResult:
        """Insert a single document and return the result."""
        doc_copy = deepcopy(document)
        doc_id = str(uuid.uuid4())
        doc_copy["_id"] = doc_id

        # Check unique constraints
        for field in self._unique_indexes:
            if field in doc_copy:
                value = doc_copy[field]
                if any(existing_doc.get(field) == value for existing_doc in self._documents.values()):
                    raise ValueError(f"Duplicate key error: {field}={value}")

        self._documents[doc_id] = doc_copy

        # Update indexes
        for field, index in self._indexes.items():
            if field in doc_copy:
                index.add(doc_copy[field])

        return InsertOneResult(doc_id)

    def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document matching the filter."""
        for doc in self._documents.values():
            if self._matches_filter(doc, filter_dict):
                return deepcopy(doc)
        return None

    def find(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Find all documents matching the filter."""
        filter_dict = filter_dict or {}
        results = []
        for doc in self._documents.values():
            if self._matches_filter(doc, filter_dict):
                results.append(deepcopy(doc))
        return results

    def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> UpdateResult:
        """Update a single document and return the result."""
        for doc_id, doc in self._documents.items():
            if self._matches_filter(doc, filter_dict):
                original_doc = deepcopy(doc)
                updated_doc = self._apply_update(doc, update_dict)

                # Check unique constraints for updated fields
                for field in self._unique_indexes:
                    if field in updated_doc and updated_doc[field] != original_doc.get(field):
                        value = updated_doc[field]
                        if any(other_doc.get(field) == value
                              for other_id, other_doc in self._documents.items()
                              if other_id != doc_id):
                            raise ValueError(f"Duplicate key error: {field}={value}")

                self._documents[doc_id] = updated_doc
                modified = updated_doc != original_doc
                return UpdateResult(matched_count=1, modified_count=1 if modified else 0)

        return UpdateResult(matched_count=0, modified_count=0)

    def update_many(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> UpdateResult:
        """Update multiple documents and return the result."""
        matched_count = 0
        modified_count = 0

        for doc_id, doc in list(self._documents.items()):
            if self._matches_filter(doc, filter_dict):
                matched_count += 1
                original_doc = deepcopy(doc)
                updated_doc = self._apply_update(doc, update_dict)

                # Check unique constraints for updated fields
                for field in self._unique_indexes:
                    if field in updated_doc and updated_doc[field] != original_doc.get(field):
                        value = updated_doc[field]
                        if any(other_doc.get(field) == value
                              for other_id, other_doc in self._documents.items()
                              if other_id != doc_id):
                            raise ValueError(f"Duplicate key error: {field}={value}")

                self._documents[doc_id] = updated_doc
                if updated_doc != original_doc:
                    modified_count += 1

        return UpdateResult(matched_count=matched_count, modified_count=modified_count)

    def delete_one(self, filter_dict: Dict[str, Any]) -> DeleteResult:
        """Delete a single document and return the result."""
        for doc_id, doc in self._documents.items():
            if self._matches_filter(doc, filter_dict):
                del self._documents[doc_id]
                return DeleteResult(deleted_count=1)
        return DeleteResult(deleted_count=0)

    def delete_many(self, filter_dict: Dict[str, Any]) -> DeleteResult:
        """Delete multiple documents and return the result."""
        to_delete = []
        for doc_id, doc in self._documents.items():
            if self._matches_filter(doc, filter_dict):
                to_delete.append(doc_id)

        for doc_id in to_delete:
            del self._documents[doc_id]

        return DeleteResult(deleted_count=len(to_delete))

    def create_index(self, field: str, unique: bool = False) -> None:
        """Create an index on the specified field."""
        if field not in self._indexes:
            self._indexes[field] = set()

        if unique:
            self._unique_indexes.add(field)

        # Add existing values to index
        for doc in self._documents.values():
            if field in doc:
                self._indexes[field].add(doc[field])

        logger.info(f"Index created on field '{field}' (unique={unique}) for collection '{self.collection_name}'")

    def _matches_filter(self, document: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Check if a document matches the filter criteria."""
        for key, value in filter_dict.items():
            if key not in document:
                return False
            if document[key] != value:
                return False
        return True

    def _apply_update(self, document: Dict[str, Any], update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Apply MongoDB-style update operations to a document."""
        doc = deepcopy(document)

        for operation, updates in update_dict.items():
            if operation == "$set":
                for field, value in updates.items():
                    doc[field] = value
            elif operation == "$unset":
                for field in updates:
                    doc.pop(field, None)
            elif operation == "$inc":
                for field, increment in updates.items():
                    doc[field] = doc.get(field, 0) + increment
            elif operation == "$addToSet":
                for field, value in updates.items():
                    if field not in doc:
                        doc[field] = []
                    if value not in doc[field]:
                        doc[field].append(value)
            elif operation == "$pull":
                for field, value in updates.items():
                    if field in doc and isinstance(doc[field], list):
                        doc[field] = [item for item in doc[field] if item != value]
            else:
                # Direct field updates (non-operator syntax)
                doc.update(update_dict)
                break

        return doc

    def clear(self) -> None:
        """Clear all documents from the collection (for testing)."""
        self._documents.clear()
        self._indexes.clear()
        self._unique_indexes.clear()