from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


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
    def find(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Find all documents matching the filter."""
        pass

    @abstractmethod
    def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> Any:
        """Update a single document and return the result."""
        pass

    @abstractmethod
    def update_many(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> Any:
        """Update multiple documents and return the result."""
        pass

    @abstractmethod
    def delete_one(self, filter_dict: Dict[str, Any]) -> Any:
        """Delete a single document and return the result."""
        pass

    @abstractmethod
    def delete_many(self, filter_dict: Dict[str, Any]) -> Any:
        """Delete multiple documents and return the result."""
        pass

    @abstractmethod
    def create_index(self, field: str, unique: bool = False) -> None:
        """Create an index on the specified field."""
        pass