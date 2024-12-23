import json
from datetime import datetime, timezone
from typing import Any, Optional, TypedDict, cast

import redis


class SerializedData(TypedDict):
    """Type definition for serialized data structure."""

    data: Any
    timestamp: str


class RedisDataStructure:
    """Base class for Redis-backed data structures.

    This class provides common functionality for Redis-based data structures,
    including connection management, serialization, and basic operations.
    All Redis data structure implementations should inherit from this class.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        username: Optional[str] = None,
        password: Optional[str] = None,
        db: int = 0,
    ):
        """Initialize Redis data structure.

        Args:
            host: Redis host address
            port: Redis port number
            username: Redis username for authentication
            password: Redis password for authentication
            db: Redis database number
        """
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            username=username,
            password=password,
            db=db,
        )

    def _serialize(self, data: Any) -> str:
        """Serialize data to JSON string with timestamp."""
        item: SerializedData = {
            "data": data,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }
        return json.dumps(item)

    def _deserialize(self, data: str) -> SerializedData:
        """Deserialize JSON string to dictionary.

        Args:
            data: JSON string to deserialize

        Returns:
            SerializedData: Dictionary containing the deserialized data and timestamp
        """
        return cast(SerializedData, json.loads(data))

    def size(self, key: str) -> int:
        """Get the size of the data structure.

        Args:
            key (str): The Redis key for this data structure

        Returns:
            int: Number of elements in the data structure
        """
        raise NotImplementedError

    def clear(self, key: str) -> bool:
        """Clear all elements from the data structure.

        Args:
            key (str): The Redis key for this data structure

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Error clearing data structure: {e}")
            return False
