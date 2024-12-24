import logging
from typing import Any, List

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


class RingBuffer(RedisDataStructure):
    """A Redis-backed ring buffer (circular buffer) implementation.

    This class implements a fixed-size circular buffer using Redis lists. When the buffer
    reaches its capacity, new elements overwrite the oldest ones. Perfect for scenarios
    like log rotation, streaming data processing, and sliding window analytics.

    The implementation uses Redis Lists for storage and a separate Redis key to track
    the current write position.
    """

    def __init__(self, capacity: int, **kwargs):
        """Initialize the ring buffer.

        Args:
            capacity (int): Maximum number of elements in the buffer
            **kwargs: Redis connection parameters
        """
        super().__init__(**kwargs)
        self.capacity = capacity

    def _get_position_key(self, key: str) -> str:
        """Get the Redis key for storing the current write position."""
        return f"{self._get_key(key)}:pos"

    def get_current_position(self, key: str) -> int:
        """Get the current write position for the buffer."""
        try:
            pos = self.connection_manager.execute("get", self._get_position_key(key))
            return int(pos) if pos is not None else 0
        except Exception:
            logger.exception("Error getting position")
            return 0

    def push(self, key: str, data: Any) -> bool:
        """Push an item into the ring buffer.

        If the buffer is full, the oldest item will be overwritten.

        Args:
            key (str): The Redis key for this buffer
            data (Any): Data to be stored

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Serialize data
            serialized = self.serialize(data)

            # Get current size
            current_size = self.size(key)

            # Use pipeline for atomic operations
            pipe = self.connection_manager.pipeline()

            cache_key = self._get_key(key)
            pos_key = self._get_position_key(key)

            # Always increment position counter as it tracks total items pushed
            pipe.incr(pos_key)

            if current_size < self.capacity:
                # If we haven't reached capacity, just append
                pipe.rpush(cache_key, serialized)
            else:
                # If at capacity, remove oldest and append new
                pipe.lpop(cache_key)
                pipe.rpush(cache_key, serialized)

            # Execute pipeline
            pipe.execute()
            return True
        except Exception:
            logger.exception("Error pushing to ring buffer")
            return False

    def get_all(self, key: str) -> List[Any]:
        """Get all items in the buffer in order.

        Args:
            key (str): The Redis key for this buffer

        Returns:
            List[Any]: List of items in order (oldest to newest)
        """
        try:
            # Get all items
            items = self.connection_manager.execute("lrange", self._get_key(key), 0, -1)

            # Deserialize items
            return [
                self.deserialize(item.decode("utf-8") if isinstance(item, bytes) else item)
                for item in items
            ]
        except Exception:
            logger.exception("Error getting items from ring buffer")
            return []

    def get_latest(self, key: str, n: int = 1) -> List[Any]:
        """Get the n most recent items from the buffer.

        Args:
            key (str): The Redis key for this buffer
            n (int): Number of items to retrieve (default: 1)

        Returns:
            List[Any]: List of items in reverse order (newest to oldest)
        """
        try:
            # Get latest n items
            items = self.connection_manager.execute("lrange", self._get_key(key), -n, -1)

            # Deserialize items in reverse order
            return [
                self.deserialize(item.decode("utf-8") if isinstance(item, bytes) else item)
                for item in reversed(items)
            ]
        except Exception:
            logger.exception("Error getting latest items from ring buffer")
            return []

    def size(self, key: str) -> int:
        """Get the current number of items in the buffer.

        Args:
            key (str): The Redis key for this buffer

        Returns:
            int: Number of items in the buffer
        """
        try:
            return self.connection_manager.execute("llen", self._get_key(key)) or 0
        except Exception:
            logger.exception("Error getting ring buffer size")
            return 0

    def clear(self, key: str) -> bool:
        """Clear all items from the buffer.

        Args:
            key (str): The Redis key for this buffer

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            pipe = self.connection_manager.pipeline()
            pipe.delete(self._get_key(key))
            pipe.delete(self._get_position_key(key))
            pipe.execute()
            return True
        except Exception:
            logger.exception("Error clearing ring buffer")
            return False
