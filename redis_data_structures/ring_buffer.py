import logging
from typing import Any, Generic, List, TypeVar

from .base import RedisDataStructure, atomic_operation, handle_operation_error

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RingBuffer(RedisDataStructure, Generic[T]):
    """A Redis-backed ring buffer (circular buffer) implementation.

    This class implements a fixed-size circular buffer using Redis lists. When the buffer
    reaches its capacity, new elements overwrite the oldest ones. Perfect for scenarios
    like log rotation, streaming data processing, and sliding window analytics.

    The implementation uses Redis Lists for storage and a separate Redis key to track
    the current write position.
    """

    def __init__(self, key: str, capacity: int, **kwargs: Any) -> None:
        """Initialize the ring buffer.

        Args:
            key (str): The key for the ring buffer
            capacity (int): Maximum number of elements in the buffer
            **kwargs: Redis connection parameters
        """
        super().__init__(key, **kwargs)
        self.capacity = capacity

    @atomic_operation
    @handle_operation_error
    def _get_position_key(self) -> str:
        """Get the Redis key for storing the current write position."""
        return f"{self.key}:pos"

    @atomic_operation
    @handle_operation_error
    def get_current_position(self) -> int:
        """Get the current write position for the buffer."""
        pos = self.connection_manager.execute("get", self._get_position_key())
        return int(pos) if pos is not None else 0

    @atomic_operation
    @handle_operation_error
    def push(self, data: T) -> bool:
        """Push an item into the ring buffer.

        If the buffer is full, the oldest item will be overwritten.

        Args:
            data (T): Data to be stored

        Returns:
            bool: True if successful, False otherwise
        """
        serialized = self.serializer.serialize(data)

        current_size = self.size()
        pipe = self.connection_manager.pipeline()

        pos_key = self._get_position_key()

        pipe.incr(pos_key)

        if current_size < self.capacity:
            # If we haven't reached capacity, just append
            pipe.rpush(self.key, serialized)
        else:
            # If at capacity, remove oldest and append new
            pipe.lpop(self.key)
            pipe.rpush(self.key, serialized)

        # Execute pipeline
        pipe.execute()
        return True

    @atomic_operation
    @handle_operation_error
    def get_all(self) -> List[T]:
        """Get all items in the buffer in order.

        Returns:
            List[T]: List of items in order (oldest to newest)
        """
        items = self.connection_manager.execute("lrange", self.key, 0, -1)

        return [self.serializer.deserialize(item) for item in items]

    @atomic_operation
    @handle_operation_error
    def get_latest(self, n: int = 1) -> List[T]:
        """Get the n most recent items from the buffer.

        Args:
            n (int): Number of items to retrieve (default: 1)

        Returns:
            List[T]: List of items in reverse order (newest to oldest)
        """
        items = self.connection_manager.execute("lrange", self.key, -n, -1)
        return [self.serializer.deserialize(item) for item in reversed(items)]

    @atomic_operation
    @handle_operation_error
    def size(self) -> int:
        """Get the current number of items in the buffer.

        Returns:
            int: Number of items in the buffer
        """
        return self.connection_manager.execute("llen", self.key) or 0

    @atomic_operation
    @handle_operation_error
    def clear(self) -> bool:
        """Clear all items from the buffer.

        Returns:
            bool: True if successful, False otherwise
        """
        pipe = self.connection_manager.pipeline()
        pipe.delete(self.key)
        pipe.delete(self._get_position_key())
        pipe.execute()
        return True
