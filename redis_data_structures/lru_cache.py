import time
from typing import Any, Dict, List, Optional

from .base import RedisDataStructure


class LRUCache(RedisDataStructure):
    """A Redis-backed LRU (Least Recently Used) cache implementation.

    This class implements an LRU cache using Redis sorted sets for tracking access order
    and Redis hashes for storing values. It automatically evicts the least recently used
    items when the cache reaches its capacity. Perfect for caching database queries,
    API responses, and other scenarios requiring a size-limited cache with automatic
    eviction of least recently used items.

    The implementation uses:
    - A Redis hash to store the key-value pairs
    - A Redis sorted set to track access times for LRU eviction
    """

    def __init__(self, capacity: int = 1000, **kwargs):
        """Initialize the LRU cache with the given capacity.

        Args:
            capacity (int): Maximum number of items the cache can hold
            **kwargs: Redis connection parameters
        """
        super().__init__(**kwargs)
        self.capacity = max(1, capacity)  # Ensure minimum capacity of 1

    def _get_hash_key(self, key: str) -> str:
        """Get the Redis key for the hash storing values."""
        return f"{key}:values"

    def _get_order_key(self, key: str) -> str:
        """Get the Redis key for the sorted set tracking access order."""
        return f"{key}:order"

    def get(self, key: str, field: str) -> Optional[Any]:
        """Get a value from the cache and update its access time.

        Args:
            key (str): The Redis key for this cache
            field (str): The field to get

        Returns:
            Optional[Any]: The value if it exists, None otherwise
        """
        try:
            hash_key = self._get_hash_key(key)
            order_key = self._get_order_key(key)

            # Get the value
            data = self.redis_client.hget(hash_key, field)
            if data is None:
                return None

            # Update access time
            current_time = time.time()
            self.redis_client.zadd(order_key, {field: current_time})

            # Deserialize and return the value
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return self._deserialize(data)

        except Exception as e:
            print(f"Error getting from cache: {e}")
            return None

    def put(self, key: str, field: str, value: Any) -> bool:
        """Put a value in the cache, evicting least recently used item if necessary.

        Args:
            key (str): The Redis key for this cache
            field (str): The field to set
            value (Any): The value to store

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            hash_key = self._get_hash_key(key)
            order_key = self._get_order_key(key)

            # Start a Redis transaction
            pipeline = self.redis_client.pipeline()

            # Check current size if the field doesn't exist
            if not self.redis_client.hexists(hash_key, field):
                current_size = self.size(key)
                if current_size >= self.capacity:
                    # Get the least recently used item
                    oldest = self.redis_client.zrange(order_key, 0, 0)
                    if oldest:
                        oldest_field = oldest[0]
                        if isinstance(oldest_field, bytes):
                            oldest_field = oldest_field.decode("utf-8")
                        # Remove the oldest item
                        pipeline.hdel(hash_key, oldest_field)
                        pipeline.zrem(order_key, oldest_field)

            # Add the new item
            try:
                serialized = self._serialize(value)
                pipeline.hset(hash_key, field, serialized)
                pipeline.zadd(order_key, {field: time.time()})
                pipeline.execute()
                return True
            except Exception as e:
                print(f"Error serializing data: {e}")
                return False

        except Exception as e:
            print(f"Error putting to cache: {e}")
            return False

    def peek(self, key: str, field: str) -> Optional[Any]:
        """Get a value without updating its access time.

        Args:
            key (str): The Redis key for this cache
            field (str): The field to peek

        Returns:
            Optional[Any]: The value if it exists, None otherwise
        """
        try:
            hash_key = self._get_hash_key(key)
            data = self.redis_client.hget(hash_key, field)
            if data is None:
                return None

            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return self._deserialize(data)

        except Exception as e:
            print(f"Error peeking cache: {e}")
            return None

    def remove(self, key: str, field: str) -> bool:
        """Remove a value from the cache.

        Args:
            key (str): The Redis key for this cache
            field (str): The field to remove

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            hash_key = self._get_hash_key(key)
            order_key = self._get_order_key(key)

            pipeline = self.redis_client.pipeline()
            pipeline.hdel(hash_key, field)
            pipeline.zrem(order_key, field)
            results = pipeline.execute()
            return any(results)

        except Exception as e:
            print(f"Error removing from cache: {e}")
            return False

    def clear(self, key: str) -> bool:
        """Clear all values from the cache.

        Args:
            key (str): The Redis key for this cache

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            hash_key = self._get_hash_key(key)
            order_key = self._get_order_key(key)

            pipeline = self.redis_client.pipeline()
            pipeline.delete(hash_key)
            pipeline.delete(order_key)
            pipeline.execute()
            return True

        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

    def size(self, key: str) -> int:
        """Get the number of items in the cache.

        Args:
            key (str): The Redis key for this cache

        Returns:
            int: Number of items in the cache
        """
        try:
            hash_key = self._get_hash_key(key)
            return self.redis_client.hlen(hash_key)
        except Exception as e:
            print(f"Error getting cache size: {e}")
            return 0

    def get_all(self, key: str) -> Dict[str, Any]:
        """Get all items in the cache.

        Args:
            key (str): The Redis key for this cache

        Returns:
            Dict[str, Any]: Dictionary of all field-value pairs
        """
        try:
            hash_key = self._get_hash_key(key)
            items = self.redis_client.hgetall(hash_key)
            result = {}

            for field, value in items.items():
                if isinstance(field, bytes):
                    field = field.decode("utf-8")
                if isinstance(value, bytes):
                    value = value.decode("utf-8")
                result[field] = self._deserialize(value)

            return result

        except Exception as e:
            print(f"Error getting all cache items: {e}")
            return {}

    def get_lru_order(self, key: str) -> List[str]:
        """Get fields in order of least recently used to most recently used.

        Args:
            key (str): The Redis key for this cache

        Returns:
            List[str]: List of fields in LRU order
        """
        try:
            order_key = self._get_order_key(key)
            items = self.redis_client.zrange(order_key, 0, -1)
            return [item.decode("utf-8") if isinstance(item, bytes) else item for item in items]

        except Exception as e:
            print(f"Error getting LRU order: {e}")
            return []
