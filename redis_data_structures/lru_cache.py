import logging
from typing import Any, Optional

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


class LRUCache(RedisDataStructure):
    """A Redis-backed LRU (Least Recently Used) cache implementation.

    This class implements an LRU cache using Redis lists and hashes, where the least
    recently used items are automatically removed when the cache reaches its capacity.
    """

    def __init__(self, key: str, capacity: int = 1000, **kwargs: Any) -> None:
        """Initialize LRU cache.

        Args:
            key (str): The key for the LRU cache
            capacity (int): Maximum number of items in the cache
            **kwargs: Additional Redis connection parameters

        Raises:
            ValueError: If capacity is less than 1
        """
        super().__init__(key, **kwargs)
        self.capacity = max(1, capacity)  # Ensure minimum capacity of 1

    def peek(self, field: str) -> Optional[Any]:
        """Get an item from the cache without updating its access time.

        Args:
            field (str): The field name

        Returns:
            Optional[Any]: The value if successful, None otherwise
        """
        try:
            cache_key = self.key
            data = self.connection_manager.execute("hget", cache_key, field)
            if not data:
                return None

            return self.serializer.deserialize(data)
        except Exception:
            logger.exception("Error peeking cache")
            return None

    def get_lru_order(self) -> list:
        """Get the list of keys in LRU order (least recently used to most recently used).

        Returns:
            list: List of keys in LRU order (least to most recently used)
        """
        try:
            cache_key = self.key
            data = self.connection_manager.execute("lrange", f"{cache_key}:order", 0, -1)
            return [
                item.decode("utf-8") if isinstance(item, bytes) else item
                for item in reversed(data or [])
            ]
        except Exception:
            logger.exception("Error getting LRU order")
            return []

    def put(self, field: str, value: Any) -> bool:
        """Put an item in the cache.

        Args:
            field (str): The field name
            value (Any): The value to store

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            pipeline = self.connection_manager.pipeline()
            cache_key = self.key

            pipeline.lrem(f"{cache_key}:order", 0, field)
            pipeline.lpush(f"{cache_key}:order", field)
            pipeline.hset(cache_key, field, self.serializer.serialize(value))

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

    def get(self, field: str) -> Optional[Any]:
        """Get an item from the cache.

        Args:
            field (str): The field name

        Returns:
            Optional[Any]: The value if successful, None otherwise
        """
        try:
            cache_key = self.key
            data = self.connection_manager.execute("hget", cache_key, field)
            if not data:
                return None

            pipeline = self.connection_manager.pipeline()
            pipeline.lrem(f"{cache_key}:order", 0, field)
            pipeline.lpush(f"{cache_key}:order", field)
            pipeline.execute()

            return self.serializer.deserialize(data)
        except Exception:
            logger.exception("Error getting from cache")
            return None

    def remove(self, field: str) -> bool:
        """Remove an item from the cache.

        Args:
            field (str): The field name

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cache_key = self.key
            pipeline = self.connection_manager.pipeline()
            pipeline.hdel(cache_key, field)
            pipeline.lrem(f"{cache_key}:order", 0, field)
            results = pipeline.execute()
            return bool(results[0])
        except Exception:
            logger.exception("Error removing from cache")
            return False

    def clear(self) -> bool:
        """Clear all items from the cache.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cache_key = self.key
            pipeline = self.connection_manager.pipeline()
            pipeline.delete(cache_key)
            pipeline.delete(f"{cache_key}:order")
            pipeline.execute()
            return True
        except Exception:
            logger.exception("Error clearing cache")
            return False

    def size(self) -> int:
        """Get the number of items in the cache.

        Returns:
            int: Number of items in the cache
        """
        try:
            return self.connection_manager.execute("hlen", self.key) or 0
        except Exception:
            logger.exception("Error getting cache size")
            return 0

    def get_all(self) -> dict:
        """Get all items from the cache.

        Returns:
            dict: Dictionary of all field-value pairs in the cache
        """
        cache_key = self.key
        data = self.connection_manager.execute("hgetall", cache_key)
        if not data:
            return {}

        return {k.decode("utf-8"): self.serializer.deserialize(v) for k, v in data.items()}
