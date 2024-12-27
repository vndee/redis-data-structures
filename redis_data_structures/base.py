import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, Optional, Type, TypeVar, Union

from pydantic import BaseModel

from .config import Config
from .connection import ConnectionManager
from .serializer import SerializableType, Serializer

PYDANTIC_AVAILABLE = True
try:
    from pydantic import BaseModel
except ImportError:
    PYDANTIC_AVAILABLE = False


logger = logging.getLogger(__name__)
T = TypeVar("T", bound=Union[BaseModel, SerializableType])


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

    def _register_type(self, type_class: Type[T]) -> None:
        """Register a type for type preservation.

        Args:
            type_class: The class to register.
                        Must be either a Pydantic model or inherit from SerializableType.

        Raises:
            ValueError: If the type is not a Pydantic model or SerializableType.
        """
        if PYDANTIC_AVAILABLE and issubclass(type_class, BaseModel):
            self.serializer.pydantic_type_registry.register(type_class.__name__, type_class)
        elif issubclass(type_class, SerializableType):
            self.serializer.custom_type_registry.register(type_class.__name__, type_class)
        else:
            raise ValueError(
                f"Type {type_class.__name__} must be a Pydantic model or "
                "inherit from SerializableType",
            )

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
            self._register_type(types)  # type: ignore[arg-type]

    def get_registered_types(self) -> Dict[str, Type]:
        """Get all registered types."""
        return self.serializer.get_registered_types()

    def set_ttl(self, key: str, ttl: Union[int, timedelta, datetime]) -> bool:
        """Set Time To Live (TTL) for a key."""
        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            elif isinstance(ttl, datetime):
                if ttl.tzinfo is None:
                    ttl = ttl.replace(tzinfo=timezone.utc)  # Make it timezone-aware
                    ttl = int((ttl - datetime.now(timezone.utc)).total_seconds())
                else:
                    ttl = int((ttl - datetime.now(ttl.tzinfo)).total_seconds())
            else:
                ttl = int(ttl)

            return bool(self.connection_manager.execute("expire", key, ttl))
        except Exception:
            logger.exception("Error setting TTL")
            return False

    def get_ttl(self, key: str) -> Any:
        """Get remaining Time To Live (TTL) for a key."""
        try:
            return self.connection_manager.execute("ttl", key)
        except Exception:
            logger.exception("Error getting TTL")
            return None

    def persist(self, key: str) -> bool:
        """Remove TTL from a key."""
        try:
            return bool(self.connection_manager.execute("persist", key))
        except Exception:
            logger.exception("Error removing TTL")
            return False

    def clear(self) -> bool:
        """Clear all elements from the data structure."""
        try:
            return bool(self.connection_manager.execute("delete", self.key))
        except Exception:
            logger.exception("Error clearing data structure")
            return False

    def close(self) -> None:
        """Close Redis connection."""
        self.connection_manager.close()
