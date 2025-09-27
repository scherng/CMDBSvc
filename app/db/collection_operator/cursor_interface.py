from abc import ABC, abstractmethod
from typing import Any, Dict, List, Iterator, Union


class CursorInterface(ABC):
    """Abstract interface for database cursor operations."""

    @abstractmethod
    def skip(self, n: int) -> 'CursorInterface':
        """Skip n documents."""
        pass

    @abstractmethod
    def limit(self, n: int) -> 'CursorInterface':
        """Limit results to n documents."""
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over the cursor results."""
        pass


class ListCursor(CursorInterface):
    """Cursor wrapper for list-based results (used by in-memory connector)."""

    def __init__(self, data: List[Dict[str, Any]]):
        self._data = data
        self._skip_count = 0
        self._limit_count = None

    def skip(self, n: int) -> 'CursorInterface':
        """Skip n documents."""
        self._skip_count = n
        return self

    def limit(self, n: int) -> 'CursorInterface':
        """Limit results to n documents."""
        self._limit_count = n
        return self

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over the cursor results."""
        start = self._skip_count
        end = start + self._limit_count if self._limit_count is not None else None
        for doc in self._data[start:end]:
            yield doc


class MongoDBCursor(CursorInterface):
    """Cursor wrapper for MongoDB cursor objects."""

    def __init__(self, cursor):
        self._cursor = cursor

    def skip(self, n: int) -> 'CursorInterface':
        """Skip n documents."""
        self._cursor = self._cursor.skip(n)
        return self

    def limit(self, n: int) -> 'CursorInterface':
        """Limit results to n documents."""
        self._cursor = self._cursor.limit(n)
        return self

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over the cursor results."""
        for doc in self._cursor:
            yield doc