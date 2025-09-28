from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from .cursor_interface import CursorInterface


class CollectionInterface(ABC):
    """Abstract interface for database collection operations."""

    @abstractmethod
    def insert_one(self, document: Dict[str, Any]) -> Any:
        """Insert a single document and return the result."""
        pass

    @abstractmethod
    def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document matching the filter."""
        pass

    @abstractmethod
    def find(self, filter_dict: Optional[Dict[str, Any]] = None) -> CursorInterface:
        """Find all documents matching the filter and return a cursor."""
        pass
    
    @abstractmethod
    def create_index(self, field: str, unique: bool = False) -> None:
        """Create an index on the specified field."""
        pass

    @abstractmethod
    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute an aggregation pipeline and return the results."""
        pass

    @abstractmethod
    def count_documents(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching the filter."""
        pass