from abc import ABC, abstractmethod
from typing import Any, Dict
from .collection_interface import CollectionInterface


class DatabaseInterface(ABC):
    """Abstract interface for database operations."""

    @abstractmethod
    def connect(self, connection_string: str, database_name: str) -> None:
        """Connect to the database."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the database."""
        pass

    @abstractmethod
    def get_collection(self, collection_name: str) -> CollectionInterface:
        """Get a collection interface."""
        pass

    @abstractmethod
    def create_indexes(self) -> None:
        """Create necessary indexes for the database."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the database connection is healthy."""
        pass