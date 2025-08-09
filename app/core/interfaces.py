"""
Core interfaces following SOLID principles.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

# Type variables for generic types
T = TypeVar('T')
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class RepositoryInterface(ABC, Generic[T]):
    """
    Repository interface following the Repository pattern.
    
    This interface defines the contract for data access operations,
    following the Dependency Inversion Principle.
    """
    
    @abstractmethod
    async def create(self, obj_in: CreateSchemaType) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        pass
    
    @abstractmethod
    async def update(self, id: Any, obj_in: UpdateSchemaType) -> Optional[T]:
        """Update an entity."""
        pass
    
    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete an entity."""
        pass
    
    @abstractmethod
    async def exists(self, id: Any) -> bool:
        """Check if entity exists."""
        pass


class ServiceInterface(ABC, Generic[T]):
    """
    Service interface following the Service pattern.
    
    This interface defines the contract for business logic operations,
    following the Single Responsibility Principle.
    """
    
    @abstractmethod
    async def create(self, obj_in: CreateSchemaType) -> T:
        """Create a new entity with business logic validation."""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID with business logic."""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with business logic."""
        pass
    
    @abstractmethod
    async def update(self, id: Any, obj_in: UpdateSchemaType) -> Optional[T]:
        """Update an entity with business logic validation."""
        pass
    
    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete an entity with business logic."""
        pass


class CacheInterface(ABC):
    """
    Cache interface following the Strategy pattern.
    
    This interface defines the contract for caching operations,
    allowing different caching strategies to be implemented.
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass


class EventPublisherInterface(ABC):
    """
    Event publisher interface following the Observer pattern.
    
    This interface defines the contract for publishing events,
    following the Open/Closed Principle.
    """
    
    @abstractmethod
    async def publish(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Publish an event."""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: callable) -> bool:
        """Subscribe to an event type."""
        pass


class LoggerInterface(ABC):
    """
    Logger interface following the Strategy pattern.
    
    This interface defines the contract for logging operations,
    allowing different logging strategies to be implemented.
    """
    
    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        pass
    
    @abstractmethod
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        pass 