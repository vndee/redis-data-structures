import json
from datetime import datetime, timezone
from typing import Any, TypedDict, cast

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

    Supported Redis connection parameters:
        - host (str): Redis host address (default: 'localhost')
        - port (int): Redis port number (default: 6379)
        - db (int): Redis database number (default: 0)
        - username (str): Redis username for authentication
        - password (str): Redis password for authentication
        - socket_timeout (float): Socket timeout in seconds
        - socket_connect_timeout (float): Socket connect timeout in seconds
        - socket_keepalive (bool): Socket keepalive settings
        - socket_keepalive_options (dict): Socket keepalive options
        - connection_pool (redis.ConnectionPool): Preconfigured connection pool
        - unix_socket_path (str): Path to unix socket file
        - encoding (str): Character encoding (default: 'utf-8')
        - encoding_errors (str): How to handle encoding errors (default: 'strict')
        - decode_responses (bool): Whether to decode responses (default: True)
        - retry_on_timeout (bool): Whether to retry on timeout
        - ssl (bool): Whether to use SSL
        - ssl_keyfile (str): Path to SSL key file
        - ssl_certfile (str): Path to SSL cert file
        - ssl_cert_reqs (str): SSL cert requirements
        - ssl_ca_certs (str): Path to SSL CA certs
        - max_connections (int): Maximum number of connections
    """

    def __init__(self, **kwargs):
        """Initialize Redis data structure.

        Args:
            **kwargs: Redis connection parameters. See class docstring for details.
                     Common parameters include host, port, username, password, and db.
        """
        default_params = {
            "host": "localhost",
            "port": 6379,
            "db": 0,
        }

        connection_params = {**default_params, **kwargs}

        try:
            self.redis_client = redis.Redis(**connection_params)
        except redis.RedisError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

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
        except redis.RedisError as e:
            print(f"Error clearing data structure: {e}")
            return False
