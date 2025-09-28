from typing import Any, Dict, List, Optional, Set
from copy import deepcopy
from app.db.collection_operator.collection_interface import CollectionInterface
from app.db.collection_operator.cursor_interface import CursorInterface, ListCursor
import uuid
import logging

logger = logging.getLogger(__name__)


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

    def find(self, filter_dict: Optional[Dict[str, Any]] = None) -> CursorInterface:
        """Find all documents matching the filter and return a cursor."""
        filter_dict = filter_dict or {}
        results = []
        for doc in self._documents.values():
            if self._matches_filter(doc, filter_dict):
                results.append(deepcopy(doc))
        return ListCursor(results)
    
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

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a basic aggregation pipeline and return the results."""
        try:
            # Start with all documents
            results = [deepcopy(doc) for doc in self._documents.values()]

            # Process each stage in the pipeline
            for stage in pipeline:
                stage_name = list(stage.keys())[0]
                stage_config = stage[stage_name]

                if stage_name == "$match":
                    # Filter documents
                    results = [doc for doc in results if self._matches_filter(doc, stage_config)]

                elif stage_name == "$sort":
                    # Sort documents
                    def sort_key(doc):
                        keys = []
                        for field, direction in stage_config.items():
                            value = doc.get(field, 0)
                            # Handle different data types for sorting
                            if value is None:
                                value = ""
                            keys.append(value if direction == 1 else -value if isinstance(value, (int, float)) else value)
                        return keys

                    results.sort(key=sort_key, reverse=any(direction == -1 for direction in stage_config.values()))

                elif stage_name == "$limit":
                    # Limit results
                    results = results[:stage_config]

                elif stage_name == "$skip":
                    # Skip results
                    results = results[stage_config:]

                elif stage_name == "$project":
                    # Project fields
                    projected_results = []
                    for doc in results:
                        projected_doc = {}
                        for field, include in stage_config.items():
                            if include == 1 and field in doc:
                                projected_doc[field] = doc[field]
                            elif include == 0 and field != "_id":
                                # Exclude field (but include others)
                                for k, v in doc.items():
                                    if k != field:
                                        projected_doc[k] = v
                        # Always include _id unless explicitly excluded
                        if "_id" not in stage_config or stage_config.get("_id", 1) == 1:
                            if "_id" in doc:
                                projected_doc["_id"] = doc["_id"]
                        projected_results.append(projected_doc)
                    results = projected_results

                elif stage_name == "$group":
                    # Basic grouping support
                    groups = {}
                    group_id = stage_config.get("_id")

                    for doc in results:
                        # Determine group key
                        if group_id is None:
                            key = None
                        elif isinstance(group_id, str) and group_id.startswith("$"):
                            key = doc.get(group_id[1:])
                        else:
                            key = group_id

                        if key not in groups:
                            groups[key] = []
                        groups[key].append(doc)

                    # Process group operations
                    grouped_results = []
                    for group_key, group_docs in groups.items():
                        group_result = {"_id": group_key}

                        for field, operation in stage_config.items():
                            if field == "_id":
                                continue

                            if isinstance(operation, dict):
                                op_name = list(operation.keys())[0]
                                op_field = operation[op_name]

                                if op_name == "$sum":
                                    if op_field == 1:
                                        group_result[field] = len(group_docs)
                                    elif isinstance(op_field, str) and op_field.startswith("$"):
                                        field_name = op_field[1:]
                                        group_result[field] = sum(doc.get(field_name, 0) for doc in group_docs if isinstance(doc.get(field_name), (int, float)))

                                elif op_name == "$count":
                                    group_result[field] = len(group_docs)

                        grouped_results.append(group_result)

                    results = grouped_results

                elif stage_name == "$count":
                    # Count stage
                    count_field = stage_config if isinstance(stage_config, str) else "count"
                    results = [{count_field: len(results)}]

                else:
                    logger.warning(f"Unsupported aggregation stage: {stage_name}")

            logger.info(f"Aggregation pipeline executed on collection '{self.collection_name}', returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error executing aggregation pipeline on collection '{self.collection_name}': {e}")
            raise

    def count_documents(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching the filter."""
        try:
            filter_dict = filter_dict or {}
            count = 0
            for doc in self._documents.values():
                if self._matches_filter(doc, filter_dict):
                    count += 1

            logger.info(f"Document count query executed on collection '{self.collection_name}', found {count} documents")
            return count
        except Exception as e:
            logger.error(f"Error counting documents in collection '{self.collection_name}': {e}")
            raise

    def clear(self) -> None:
        """Clear all documents from the collection (for testing)."""
        self._documents.clear()
        self._indexes.clear()
        self._unique_indexes.clear()