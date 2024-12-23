import json
import redis
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, ClassVar, Dict, Optional, Type, TypedDict, Union, cast

try:
    from pydantic import BaseModel

    PYDANTIC_AVAILABLE = True
except ImportError:
    BaseModel = object
    PYDANTIC_AVAILABLE = False


class SerializedData(TypedDict):
    """Type definition for serialized data structure."""

    data: Any
    timestamp: str
    _type: str


class CustomRedisDataType:
    """Base class for creating custom Redis data types.

    This class automatically registers custom types that users create,
    allowing for automatic serialization/deserialization of these types
    when storing them in Redis.

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

    _registered_types: ClassVar[Dict[str, Type]] = {}

    def __init_subclass__(cls, **kwargs):
        """Initialize subclass and register type."""
        super().__init_subclass__(**kwargs)

        # Check if it's a Pydantic model
        if PYDANTIC_AVAILABLE and issubclass(cls, BaseModel):
            cls._registered_types[cls.__name__] = cls
            # Add Pydantic model methods if not overridden
            if not hasattr(cls, "to_dict"):
                cls.to_dict = lambda self: self.model_dump()
            if not hasattr(cls, "from_dict"):
                cls.from_dict = classmethod(lambda cls, data: cls.model_validate(data))
        # Check for standard class with required methods
        elif hasattr(cls, "to_dict") and hasattr(cls, "from_dict"):
            cls._registered_types[cls.__name__] = cls

    @classmethod
    def get_type(cls, type_name: str) -> Optional[Type]:
        """Get registered type by name."""
        return cls._registered_types.get(type_name)

    def to_dict(self) -> dict:
        """Convert instance to dictionary.

        Must be implemented by subclasses unless using Pydantic.
        For Pydantic models, this is automatically implemented.
        """
        raise NotImplementedError("Subclasses must implement to_dict()")

    @classmethod
    def from_dict(cls, data: dict) -> "CustomRedisDataType":
        """Create instance from dictionary.

        Must be implemented by subclasses unless using Pydantic.
        For Pydantic models, this is automatically implemented.
        """
        raise NotImplementedError("Subclasses must implement from_dict()")


class RedisDataStructure:
    """Base class for Redis-backed data structures.

    This class provides the Redis connection and serialization methods for
    storing and retrieving data from Redis. It handles both built-in types
    and custom types created with CustomRedisDataType.
    """

    def __init__(self, **kwargs):
        """Initialize Redis data structure."""
        default_params = {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "decode_responses": True,
        }

        connection_params = {**default_params, **kwargs}

        try:
            self.redis_client = redis.Redis(**connection_params)
            self.redis_client.ping()
        except redis.RedisError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

        # Initialize default type handlers
        self.type_handlers: Dict[Type, Dict[str, Callable]] = {
            tuple: {
                "serialize": lambda x: {
                    "_type": "tuple",
                    "value": [self._serialize_value(item) for item in x],
                },
                "deserialize": lambda x: tuple(
                    self._deserialize_value(item) for item in x["value"]
                ),
            },
            set: {
                "serialize": lambda x: {
                    "_type": "set",
                    "value": [self._serialize_value(item) for item in sorted(x)],
                },
                "deserialize": lambda x: set(self._deserialize_value(item) for item in x["value"]),
            },
            bytes: {
                "serialize": lambda x: {
                    "_type": "bytes",
                    "value": x.hex(),
                },
                "deserialize": lambda x: bytes.fromhex(x["value"]),
            },
            datetime: {
                "serialize": lambda x: {
                    "_type": "datetime",
                    "value": x.isoformat(),
                },
                "deserialize": lambda x: datetime.fromisoformat(x["value"]),
            },
            timedelta: {
                "serialize": lambda x: {
                    "_type": "timedelta",
                    "value": x.total_seconds(),
                },
                "deserialize": lambda x: timedelta(seconds=float(x["value"])),
            },
        }

    def _serialize_value(self, val: Any) -> Any:
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
                return handlers["serialize"](val)

        # Handle lists
        if isinstance(val, list):
            return {
                "_type": "list",
                "value": [self._serialize_value(item) for item in val],
            }

        # Handle dictionaries
        if isinstance(val, dict):
            return {
                "_type": "dict",
                "value": {str(k): self._serialize_value(v) for k, v in val.items()},
            }

        # Handle custom user types (created with CustomRedisDataType)
        if type(type(val)) == CustomRedisDataType:
            return {
                "_type": val.__class__.__name__,
                "value": val.to_dict(),
            }

        # Default to string representation for unknown types
        return {
            "_type": "str",
            "value": str(val),
        }

    def _deserialize_value(self, val: Any) -> Any:
        """Helper method to deserialize a single value."""
        # Handle non-dict or missing _type values
        if not isinstance(val, dict) or "_type" not in val:
            return val

        type_name = val["_type"]
        data = val.get("value")

        # Handle None type
        if type_name == "NoneType":
            return None

        # Handle primitive types first
        if type_name in ("int", "float", "str", "bool"):
            return data

        # Handle custom user types
        custom_type = CustomRedisDataType.get_type(type_name)
        if custom_type is not None:
            return custom_type.from_dict(data)

        # Handle registered types
        for type_class, handlers in self.type_handlers.items():
            if type_class.__name__ == type_name:
                return handlers["deserialize"](val)

        # Handle built-in collection types
        if type_name == "tuple":
            return tuple(self._deserialize_value(item) for item in data)
        if type_name == "list":
            return [self._deserialize_value(item) for item in data]
        if type_name == "set":
            return set(self._deserialize_value(item) for item in data)
        if type_name == "dict":
            return {k: self._deserialize_value(v) for k, v in data.items()}

        # Default to string for unknown types
        return str(data)

    def _serialize(self, data: Any, include_timestamp: bool = True) -> str:
        """Serialize data to JSON string with timestamp and type information."""
        serialized = self._serialize_value(data)
        if include_timestamp:
            serialized["timestamp"] = datetime.now(timezone.utc).isoformat()

        return json.dumps(serialized, ensure_ascii=False)

    def _deserialize(self, data: str, include_timestamp: bool = True) -> SerializedData:
        """Deserialize JSON string to dictionary with type restoration."""
        try:
            if not data:
                return cast(SerializedData, {"value": None, "_type": "NoneType"})

            deserialized = json.loads(data)

            # Handle simple string values that couldn't be parsed as JSON
            if not isinstance(deserialized, dict):
                return cast(
                    SerializedData,
                    {
                        "value": deserialized,
                        "_type": type(deserialized).__name__,
                    },
                )

            result = cast(
                SerializedData,
                {
                    "value": self._deserialize_value(deserialized),
                    "_type": deserialized.get(
                        "_type",
                        (
                            type(deserialized.get("value")).__name__
                            if "value" in deserialized
                            else "str"
                        ),
                    ),
                },
            )

            if include_timestamp and "timestamp" in deserialized:
                result["timestamp"] = deserialized["timestamp"]

            return result["value"]
        except json.JSONDecodeError:
            return cast(
                SerializedData,
                {
                    "value": data,
                    "_type": "str",
                },
            )

    def set_ttl(self, key: str, ttl: Union[int, timedelta]) -> bool:
        """Set Time To Live (TTL) for a key.
        
        Args:
            key: The key to set TTL for
            ttl: Time to live in seconds (int) or timedelta
        
        Returns:
            bool: True if TTL was set, False otherwise
        """
        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            return bool(self.redis_client.expire(key, ttl))
        except redis.RedisError as e:
            print(f"Error setting TTL: {e}")
            return False

    def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining Time To Live (TTL) for a key.
        
        Args:
            key: The key to get TTL for
        
        Returns:
            Optional[int]: Remaining time in seconds, None if key has no TTL,
                          -2 if key does not exist, -1 if key exists but has no TTL
        """
        try:
            return self.redis_client.ttl(key)
        except redis.RedisError as e:
            print(f"Error getting TTL: {e}")
            return None

    def persist(self, key: str) -> bool:
        """Remove TTL from a key, making it persistent.
        
        Args:
            key: The key to remove TTL from
        
        Returns:
            bool: True if TTL was removed, False otherwise
        """
        try:
            return bool(self.redis_client.persist(key))
        except redis.RedisError as e:
            print(f"Error removing TTL: {e}")
            return False

    def set_expire_at(self, key: str, timestamp: Union[datetime, int]) -> bool:
        """Set key to expire at a specific timestamp.
        
        Args:
            key: The key to set expiration for
            timestamp: Unix timestamp (int) or datetime object
        
        Returns:
            bool: True if expiration was set, False otherwise
        """
        try:
            if isinstance(timestamp, datetime):
                timestamp = int(timestamp.timestamp())
            return bool(self.redis_client.expireat(key, timestamp))
        except redis.RedisError as e:
            print(f"Error setting expiration: {e}")
            return False

    def size(self, key: str) -> int:
        """Get the size of the data structure."""
        try:
            if not self.redis_client.exists(key):
                return 0
            return self.redis_client.strlen(key)
        except redis.RedisError as e:
            print(f"Error getting size: {e}")
            return 0

    def clear(self, key: str) -> bool:
        """Clear all elements from the data structure."""
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError as e:
            print(f"Error clearing data structure: {e}")
            return False
