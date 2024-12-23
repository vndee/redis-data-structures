from typing import Any, Optional
import logging

from .base import RedisDataStructure
from .metrics import track_operation

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
        self.capacity = capacity

    @track_operation("put")
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
            pipeline.hset(cache_key, field, self._serialize(value))

            # Check if we need to remove the least recently used item
            pipeline.llen(f"{cache_key}:order")
            results = pipeline.execute()

            if results[-1] > self.capacity:
                # Remove the least recently used item
                lru_field = self.connection_manager.execute(
                    "rpop",
                    f"{cache_key}:order"
                )
                if lru_field:
                    if isinstance(lru_field, bytes):
                        lru_field = lru_field.decode("utf-8")
                    self.connection_manager.execute(
                        "hdel",
                        cache_key,
                        lru_field
                    )

            return True
        except Exception as e:
            logger.error(f"Error putting to cache: {e}")
            return False

    @track_operation("get")
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
            data = self.connection_manager.execute(
                "hget",
                cache_key,
                field
            )
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
            return self._deserialize(data)
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None

    @track_operation("remove")
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
        except Exception as e:
            logger.error(f"Error removing from cache: {e}")
            return False

    @track_operation("clear")
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
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    @track_operation("size")
    def size(self, key: str) -> int:
        """Get the number of items in the cache.

        Args:
            key (str): The Redis key for this cache

        Returns:
            int: Number of items in the cache
        """
        try:
            return self.connection_manager.execute(
                "hlen",
                self._get_key(key)
            ) or 0
        except Exception as e:
            logger.error(f"Error getting cache size: {e}")
            return 0
