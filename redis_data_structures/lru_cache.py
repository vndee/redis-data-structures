import logging
from typing import Any, Optional

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


class LRUCache(RedisDataStructure):
    """A Redis-backed LRU (Least Recently Used) cache implementation.

    This class implements an LRU cache using Redis lists and hashes, where the least
    recently used items are automatically removed when the cache reaches its capacity.
    """

    def __init__(self, capacity: int = 1000, **kwargs):
        """Initialize LRU cache.

        Args:
            capacity (int): Maximum number of items in the cache
            **kwargs: Additional Redis connection parameters
        """
        super().__init__(**kwargs)
        self.capacity = max(1, capacity)  # Ensure minimum capacity of 1

    def peek(self, key: str, field: str) -> Optional[Any]:
        """Get an item from the cache without updating its access time.

        Args:
            key (str): The Redis key for this cache
            field (str): The field name

        Returns:
            Optional[Any]: The value if successful, None otherwise
        """
        try:
            cache_key = self._get_key(key)
            # Get the value without updating access order
            data = self.connection_manager.execute("hget", cache_key, field)
            if not data:
                return None

            # Handle bytes response from Redis
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return self.deserialize(data)
        except Exception:
            logger.exception("Error peeking cache")
            return None

    def get_lru_order(self, key: str) -> list:
        """Get the list of keys in LRU order (least recently used to most recently used).

        Args:
            key (str): The Redis key for this cache

        Returns:
            list: List of keys in LRU order (least to most recently used)
        """
        try:
            cache_key = self._get_key(key)
            # Get the list in reverse order (most recently used to least)
            data = self.connection_manager.execute("lrange", f"{cache_key}:order", 0, -1)
            # Convert bytes to strings if necessary and reverse to get LRU order
            return [
                item.decode("utf-8") if isinstance(item, bytes) else item
                for item in reversed(data or [])
            ]
        except Exception:
            logger.exception("Error getting LRU order")
            return []

    def put(self, key: str, field: str, value: Any) -> bool:
        """Put an item in the cache.

        Args:
            key (str): The Redis key for this cache
            field (str): The field name
            value (Any): The value to store

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Start a Redis transaction
            pipeline = self.connection_manager.pipeline()
            cache_key = self._get_key(key)

            # Remove the field from the order list if it exists
            pipeline.lrem(f"{cache_key}:order", 0, field)
            # Add the field to the front of the order list
            pipeline.lpush(f"{cache_key}:order", field)
            # Store the value in the hash
            pipeline.hset(cache_key, field, self.serialize(value))

            # Check if we need to remove the least recently used item
            pipeline.llen(f"{cache_key}:order")
            results = pipeline.execute()

            if results[-1] > self.capacity:
                # Remove the least recently used item
                lru_field = self.connection_manager.execute("rpop", f"{cache_key}:order")
                if lru_field:
                    if isinstance(lru_field, bytes):
                        lru_field = lru_field.decode("utf-8")
                    self.connection_manager.execute("hdel", cache_key, lru_field)

            return True
        except Exception:
            logger.exception("Error putting to cache")
            return False

    def get(self, key: str, field: str) -> Optional[Any]:
        """Get an item from the cache.

        Args:
            key (str): The Redis key for this cache
            field (str): The field name

        Returns:
            Optional[Any]: The value if successful, None otherwise
        """
        try:
            cache_key = self._get_key(key)
            # Get the value
            data = self.connection_manager.execute("hget", cache_key, field)
            if not data:
                return None

            # Update access order in a pipeline
            pipeline = self.connection_manager.pipeline()
            pipeline.lrem(f"{cache_key}:order", 0, field)
            pipeline.lpush(f"{cache_key}:order", field)
            pipeline.execute()

            # Handle bytes response from Redis
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return self.deserialize(data)
        except Exception:
            logger.exception("Error getting from cache")
            return None

    def remove(self, key: str, field: str) -> bool:
        """Remove an item from the cache.

        Args:
            key (str): The Redis key for this cache
            field (str): The field name

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cache_key = self._get_key(key)
            pipeline = self.connection_manager.pipeline()
            pipeline.hdel(cache_key, field)
            pipeline.lrem(f"{cache_key}:order", 0, field)
            results = pipeline.execute()
            return bool(results[0])
        except Exception:
            logger.exception("Error removing from cache")
            return False

    def clear(self, key: str) -> bool:
        """Clear all items from the cache.

        Args:
            key (str): The Redis key for this cache

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cache_key = self._get_key(key)
            pipeline = self.connection_manager.pipeline()
            pipeline.delete(cache_key)
            pipeline.delete(f"{cache_key}:order")
            pipeline.execute()
            return True
        except Exception:
            logger.exception("Error clearing cache")
            return False

    def size(self, key: str) -> int:
        """Get the number of items in the cache.

        Args:
            key (str): The Redis key for this cache

        Returns:
            int: Number of items in the cache
        """
        try:
            return self.connection_manager.execute("hlen", self._get_key(key)) or 0
        except Exception:
            logger.exception("Error getting cache size")
            return 0

    def get_all(self, key: str) -> dict:
        """Get all items from the cache.

        Args:
            key (str): The Redis key for this cache

        Returns:
            dict: Dictionary of all field-value pairs in the cache
        """
        try:
            cache_key = self._get_key(key)
            data = self.connection_manager.execute("hgetall", cache_key)
            if not data:
                return {}

            # Convert from Redis response to dictionary
            result = {}
            if isinstance(data, list):
                it = iter(data)
                for field in it:
                    value = next(it)
                    if isinstance(field, bytes):
                        field = field.decode("utf-8")
                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    try:
                        result[field] = self.deserialize(value)
                    except Exception:
                        logger.exception(f"Error deserializing value for field {field}")
                        result[field] = None
            else:
                # If data is already a dict (some Redis clients return dict)
                for field, value in data.items():
                    try:
                        if isinstance(value, bytes):
                            value = value.decode("utf-8")
                        result[field] = self.deserialize(value)
                    except Exception:
                        logger.exception(f"Error deserializing value for field {field}")
                        result[field] = None
            return result
        except Exception:
            logger.exception("Error getting all items from cache")
            return {}
