import logging
from typing import Any, Generic, Optional, TypeVar

from .base import RedisDataStructure, atomic_operation, handle_operation_error

logger = logging.getLogger(__name__)

K = TypeVar("K")
V = TypeVar("V")


class LRUCache(RedisDataStructure, Generic[K, V]):
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

    @atomic_operation
    @handle_operation_error
    def peek(self, field: K) -> Optional[V]:
        """Get an item from the cache without updating its access time.

        Args:
            field (K): The field name

        Returns:
            Optional[V]: The value if successful, None otherwise
        """
        cache_key = self.key
        if self.serializer.is_redis_key_acceptable_type(field):
            data = self.connection_manager.execute("hget", cache_key, field)
        else:
            data = self.connection_manager.execute(
                "hget",
                cache_key,
                self.serializer.serialize(field),
            )
        if not data:
            return None

        return self.serializer.deserialize(data)  # type: ignore[no-any-return]

    @atomic_operation
    @handle_operation_error
    def get_lru_order(self) -> list:
        """Get the list of keys in LRU order (least recently used to most recently used).

        Returns:
            list: List of keys in LRU order (least to most recently used)
        """
        cache_key = self.key
        data = self.connection_manager.execute("lrange", f"{cache_key}:order", 0, -1)
        return [
            item.decode("utf-8") if isinstance(item, bytes) else item
            for item in reversed(data or [])
        ]

    @atomic_operation
    @handle_operation_error
    def put(self, field: K, value: V) -> bool:
        """Put an item in the cache.

        Args:
            field (K): The field name
            value (V): The value to store

        Returns:
            bool: True if successful, False otherwise
        """
        pipeline = self.connection_manager.pipeline()
        cache_key = self.key

        if not self.serializer.is_redis_key_acceptable_type(field):
            field = self.serializer.serialize(field)

        pipeline.lrem(f"{cache_key}:order", 0, field)  # type: ignore[arg-type]
        pipeline.lpush(f"{cache_key}:order", field)  # type: ignore[arg-type]
        pipeline.hset(cache_key, field, self.serializer.serialize(value))  # type: ignore[arg-type]

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

    @atomic_operation
    @handle_operation_error
    def get(self, field: K) -> Optional[V]:
        """Get an item from the cache.

        Args:
            field (K): The field name

        Returns:
            Optional[V]: The value if successful, None otherwise
        """
        cache_key = self.key
        if not self.serializer.is_redis_key_acceptable_type(field):
            field = self.serializer.serialize(field)

        data = self.connection_manager.execute("hget", cache_key, field)
        if not data:
            return None

        pipeline = self.connection_manager.pipeline()
        pipeline.lrem(f"{cache_key}:order", 0, field)  # type: ignore[arg-type]
        pipeline.lpush(f"{cache_key}:order", field)  # type: ignore[arg-type]
        pipeline.execute()

        return self.serializer.deserialize(data)  # type: ignore[no-any-return]

    @atomic_operation
    @handle_operation_error
    def remove(self, field: K) -> bool:
        """Remove an item from the cache.

        Args:
            field (K): The field name

        Returns:
            bool: True if successful, False otherwise
        """
        cache_key = self.key
        pipeline = self.connection_manager.pipeline()
        if not self.serializer.is_redis_key_acceptable_type(field):
            field = self.serializer.serialize(field)

        pipeline.hdel(cache_key, field)  # type: ignore[arg-type]
        pipeline.lrem(f"{cache_key}:order", 0, field)  # type: ignore[arg-type]
        results = pipeline.execute()
        return bool(results[0])

    @atomic_operation
    @handle_operation_error
    def clear(self) -> bool:
        """Clear all items from the cache.

        Returns:
            bool: True if successful, False otherwise
        """
        cache_key = self.key
        pipeline = self.connection_manager.pipeline()
        pipeline.delete(cache_key)
        pipeline.delete(f"{cache_key}:order")
        pipeline.execute()
        return True

    @atomic_operation
    @handle_operation_error
    def size(self) -> int:
        """Get the number of items in the cache.

        Returns:
            int: Number of items in the cache
        """
        return self.connection_manager.execute("hlen", self.key) or 0

    @atomic_operation
    @handle_operation_error
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
