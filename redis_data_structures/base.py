import logging
from datetime import datetime, timedelta
from functools import wraps
from threading import RLock
from typing import Any, Callable, Dict, Iterable, Optional, Type, TypeVar, Union

from redis.exceptions import RedisError

from .config import Config
from .connection import ConnectionManager
from .exceptions import RedisDataStructureError
from .serializer import SerializableType, Serializer

try:
    from pydantic import BaseModel

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Union[BaseModel, SerializableType])
R = TypeVar("R")


def handle_operation_error(func: Callable[..., R]) -> Callable[..., R]:
    """Decorator for handling Redis operation errors."""

    @wraps(func)
    def wrapper(self: "RedisDataStructure", *args: Any, **kwargs: Any) -> R:
        try:
            return func(self, *args, **kwargs)
        except RedisError as e:
            raise e from e
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error executing operation")
            raise RedisDataStructureError(f"Error executing operation: {e}") from e

    return wrapper


def atomic_operation(func: Callable[..., R]) -> Callable[..., R]:
    """Decorator for atomic operations."""

    @wraps(func)
    def wrapper(self: "RedisDataStructure", *args: Any, **kwargs: Any) -> R:
        with self._lock:
            return func(self, *args, **kwargs)

    return wrapper


class RedisDataStructure:
    """Base class for Redis-backed data structures."""

    def __init__(
        self,
        key: str,
        connection_manager: Optional[ConnectionManager] = None,
        config: Optional[Config] = None,
        **kwargs: Any,
    ):
        """Initialize Redis data structure."""
        self.config = config or Config.from_env()
        if kwargs:
            for key, value in kwargs.items():
                if hasattr(self.config.redis, key):
                    setattr(self.config.redis, key, value)

        self.connection_manager = connection_manager or ConnectionManager(
            **self.config.redis.__dict__,
        )

        if self.config.data_structures.debug_enabled:
            logger.setLevel(logging.DEBUG)

        self.serializer = Serializer(
            compression_threshold=self.config.data_structures.compression_threshold,
        )
        self.key = f"{self.config.data_structures.prefix}:{key}"
        self._lock = RLock()

    @atomic_operation
    def _register_type(self, type_class: Type[T]) -> None:
        """Register a type for type preservation.

        Args:
            type_class: The class to register.
                        Must be either a Pydantic model or inherit from SerializableType.

        Raises:
            TypeError: If the type is not a Pydantic model or SerializableType.
        """
        if PYDANTIC_AVAILABLE and issubclass(type_class, BaseModel):
            self.serializer.pydantic_type_registry.register(type_class.__name__, type_class)
        elif issubclass(type_class, SerializableType):
            self.serializer.serializable_type_registry.register(type_class.__name__, type_class)
        else:
            raise TypeError(
                f"Type {type_class.__name__} must be a Pydantic model or "
                "inherit from SerializableType",
            )

    @atomic_operation
    def register_types(self, types: Union[Iterable[Type[T]], Type[T], None] = None) -> None:
        """Register multiple types at once.

        Args:
            types: The types to register.

        Examples:
            Register a single type:
                register_types(types=MyType)
            Register multiple types:
                register_types(types=[MyType1, MyType2])
        """
        if isinstance(types, Iterable):
            for type_class in types:
                self._register_type(type_class)
        else:
            self._register_type(types)

    @atomic_operation
    def get_registered_types(self) -> Dict[str, Type]:
        """Get all registered types."""
        return self.serializer.get_registered_types()

    @atomic_operation
    @handle_operation_error
    def set_ttl(self, key: str, ttl: Union[int, timedelta, datetime]) -> bool:
        """Set Time To Live (TTL) for a key."""
        if isinstance(ttl, timedelta):
            ttl = int(ttl.total_seconds())
        elif isinstance(ttl, datetime):
            if ttl.tzinfo is None:
                ttl = int((ttl - datetime.now()).total_seconds())
            else:
                ttl = int((ttl - datetime.now(ttl.tzinfo)).total_seconds())
        else:
            ttl = int(ttl)

        if not bool(self.connection_manager.execute("expire", key, ttl)):
            raise RedisDataStructureError(
                f"Failed to set TTL for key {key} to {ttl}. Key {key} might not exist.",
            )

        return True

    @atomic_operation
    @handle_operation_error
    def get_ttl(self, key: str) -> Any:
        """Get remaining Time To Live (TTL) for a key."""
        return self.connection_manager.execute("ttl", key)

    @atomic_operation
    @handle_operation_error
    def persist(self, key: str) -> bool:
        """Remove TTL from a key."""
        return bool(self.connection_manager.execute("persist", key))

    @atomic_operation
    @handle_operation_error
    def clear(self) -> bool:
        """Clear all elements from the data structure."""
        return bool(self.connection_manager.execute("delete", self.key))

    @atomic_operation
    @handle_operation_error
    def close(self) -> None:
        """Close Redis connection."""
        self.connection_manager.close()
