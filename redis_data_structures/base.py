import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, TypedDict, TypeVar, Union

from .config import Config
from .connection import ConnectionManager
from .exceptions import SerializationError

try:
    from pydantic import BaseModel

    PYDANTIC_AVAILABLE = True
except ImportError:
    BaseModel = object
    PYDANTIC_AVAILABLE = False

logger = logging.getLogger(__name__)
T = TypeVar("T")


class SerializedData(TypedDict):
    """Type definition for serialized data structure."""

    data: Any
    timestamp: str
    _type: str


class CustomRedisDataType:
    """Base class for creating custom Redis data types.

    Example with standard class:
        ```python
        class User(CustomRedisDataType):
            def __init__(self, name: str, age: int):
                self.name = name
                self.age = age

            def to_dict(self) -> dict:
                return {"name": self.name, "age": self.age}

            @classmethod
            def from_dict(cls, data: dict) -> 'User':
                return cls(data["name"], data["age"])
        ```

    Example with Pydantic:
        ```python
        class UserModel(CustomRedisDataType, BaseModel):
            name: str
            age: int
            joined: datetime
        ```
    """

    def to_dict(self) -> dict:
        """Convert instance to dictionary."""
        raise NotImplementedError("Subclasses must implement to_dict()")

    @classmethod
    def from_dict(cls, data: dict) -> "CustomRedisDataType":
        """Create instance from dictionary."""
        raise NotImplementedError("Subclasses must implement from_dict()")


class RedisDataStructure:
    """Base class for Redis-backed data structures."""

    def __init__(
        self,
        key: str,
        config: Optional[Config] = None,
        connection_manager: Optional[ConnectionManager] = None,
        **kwargs,
    ):
        """Initialize Redis data structure."""
        # Initialize configuration
        self.config = config or Config.from_env()
        if kwargs:
            # Update config with any provided kwargs
            for key, value in kwargs.items():
                if hasattr(self.config.redis, key):
                    setattr(self.config.redis, key, value)

        # Initialize connection manager
        self.connection_manager = connection_manager or ConnectionManager(
            **self.config.redis.__dict__,
        )

        # Set up logging
        if self.config.data_structures.debug_enabled:
            logger.setLevel(logging.DEBUG)

        # Initialize type handlers
        self.type_handlers = {
            tuple: {
                "serialize": lambda x: [self.serialize_value(item) for item in x],
                "deserialize": lambda x: tuple(self.deserialize_value(item) for item in x),
            },
            set: {
                "serialize": lambda x: [self.serialize_value(item) for item in x],
                "deserialize": lambda x: set(self.deserialize_value(item) for item in x),
            },
            bytes: {
                "serialize": lambda x: x.hex(),
                "deserialize": lambda x: bytes.fromhex(x),
            },
            datetime: {
                "serialize": lambda x: x.isoformat(),
                "deserialize": lambda x: datetime.fromisoformat(x),
            },
            timedelta: {
                "serialize": lambda x: x.total_seconds(),
                "deserialize": lambda x: timedelta(seconds=float(x)),
            },
        }

        self.key = f"{self.config.data_structures.prefix}:{key}"

    def serialize_value(self, val: Any) -> Any:
        """Helper method to serialize a single value."""
        # Handle None and primitive types
        if val is None or isinstance(val, (int, float, str, bool)):
            return {
                "value": val,
                "_type": type(val).__name__ if val is not None else "NoneType",
            }

        # Handle registered type handlers
        for type_class, handlers in self.type_handlers.items():
            if isinstance(val, type_class):
                return {
                    "_type": type_class.__name__,
                    "value": handlers["serialize"](val),
                }

        # Handle lists
        if isinstance(val, list):
            return {
                "_type": "list",
                "value": [self.serialize_value(item) for item in val],
            }

        # Handle dictionaries
        if isinstance(val, dict):
            return {
                "_type": "dict",
                "value": {str(k): self.serialize_value(v) for k, v in val.items()},
            }

        # Handle custom types
        if isinstance(val, CustomRedisDataType):
            return {
                "_type": val.__class__.__name__,
                "module": val.__class__.__module__,
                "value": val.to_dict(),
            }

        # Handle Pydantic models
        if PYDANTIC_AVAILABLE and isinstance(val, BaseModel):
            return {
                "_type": val.__class__.__name__,
                "module": val.__class__.__module__,
                "value": val.model_dump(mode="json"),
            }

        # Default to string representation
        return {
            "_type": "str",
            "value": str(val),
        }

    def deserialize_value(self, val: Any) -> Any:
        """Helper method to deserialize a single value."""
        if not isinstance(val, dict) or "_type" not in val:
            return val

        type_name = val["_type"]
        data = val.get("value")
        module_name = val.get("module")

        # Handle None
        if type_name == "NoneType":
            return None

        # Handle primitive types
        if type_name in ("int", "float", "str", "bool"):
            return data

        # Handle registered types
        for type_class, handlers in self.type_handlers.items():
            if type_class.__name__ == type_name:
                return handlers["deserialize"](data)

        # Handle collections
        if type_name == "list":
            return [self.deserialize_value(item) for item in data]
        if type_name == "dict":
            return {k: self.deserialize_value(v) for k, v in data.items()}
        if type_name == "set":
            return {self.deserialize_value(item) for item in data}
        if type_name == "tuple":
            return tuple(self.deserialize_value(item) for item in data)

        # Try to find custom type or Pydantic model
        if module_name:
            try:
                import importlib

                module = importlib.import_module(module_name)
                type_class = getattr(module, type_name)

                if issubclass(type_class, CustomRedisDataType):
                    return type_class.from_dict(data)
                if PYDANTIC_AVAILABLE and issubclass(type_class, BaseModel):
                    return type_class.model_validate(data)
            except (ImportError, AttributeError) as e:
                logger.warning(f"Failed to import type {type_name} from {module_name}: {e}")

        return data

    def serialize(self, value: Any, include_timestamp: bool = True) -> str:
        """Serialize value to string.

        Args:
            value: The value to serialize
            include_timestamp: Whether to include a timestamp in the serialized data.
                             Defaults to True. Set to False for data structures that
                             need exact value matching (e.g. sets).

        Returns:
            str: The serialized value
        """
        try:
            serialized = self.serialize_value(value)
            if include_timestamp:
                serialized["timestamp"] = datetime.now(timezone.utc).isoformat()

            result = json.dumps(serialized)

            # Apply compression if enabled and threshold met
            if (
                self.config.data_structures.compression_enabled
                and len(result) >= self.config.data_structures.compression_threshold
            ):
                import zlib

                result = zlib.compress(result.encode())

            return result
        except Exception:
            logger.exception("Failed to serialize value")
            raise SerializationError("Failed to serialize value")

    def deserialize(self, data: str) -> Any:
        """Deserialize string to value."""
        try:
            # Check if data is compressed
            if self.config.data_structures.compression_enabled and isinstance(data, bytes):
                import zlib

                data = zlib.decompress(data).decode()

            if not data:
                return None

            deserialized = json.loads(data)
            return self.deserialize_value(deserialized)
        except Exception as e:
            raise SerializationError(f"Failed to deserialize data: {e}")

    def set_ttl(self, key: str, ttl: Union[int, timedelta]) -> bool:
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

    def get_ttl(self, key: str) -> Optional[int]:
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

    def close(self):
        """Close Redis connection."""
        self.connection_manager.close()
