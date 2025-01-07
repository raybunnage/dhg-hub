from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic

T = TypeVar("T")


class SupabaseBase(ABC, Generic[T]):
    """Abstract base class for Supabase operations."""

    @abstractmethod
    async def get_all(self) -> List[T]:
        """Get all records."""
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get record by ID."""
        pass

    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> T:
        """Create a record."""
        pass

    @abstractmethod
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update a record."""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete a record."""
        pass
