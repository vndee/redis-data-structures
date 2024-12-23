from typing import Any, Optional, List
from .base import RedisDataStructure


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
        return f"{key}:pos"

    def _get_current_position(self, key: str) -> int:
        """Get the current write position for the buffer."""
        try:
            pos = self.redis_client.get(self._get_position_key(key))
            return int(pos) if pos is not None else 0
        except Exception as e:
            print(f"Error getting position: {e}")
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
            serialized = self._serialize(data)
            
            # Use transaction to ensure atomicity
            pipe = self.redis_client.pipeline()
            
            # Get current size
            current_size = self.size(key)
            
            if current_size < self.capacity:
                # If we haven't reached capacity, just append
                pipe.rpush(key, serialized)
            else:
                # If at capacity, remove oldest and append new
                pipe.lpop(key)
                pipe.rpush(key, serialized)
            
            # Execute transaction
            pipe.execute()
            return True
        except Exception as e:
            print(f"Error pushing to ring buffer: {e}")
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
            items = self.redis_client.lrange(key, 0, -1)
            
            # Deserialize items
            return [
                self._deserialize(item.decode("utf-8") if isinstance(item, bytes) else item)
                for item in items
            ]
        except Exception as e:
            print(f"Error getting items from ring buffer: {e}")
            return []

    def get_latest(self, key: str, n: int = 1) -> List[Any]:
        """Get the n most recent items from the buffer.

        Args:
            key (str): The Redis key for this buffer
            n (int): Number of items to retrieve (default: 1)

        Returns:
            List[Any]: List of most recent items (newest to oldest)
        """
        try:
            # Get current size
            size = self.size(key)
            if size == 0:
                return []
            
            # Ensure n doesn't exceed buffer size
            n = min(n, size)
            
            # Get latest n items
            items = self.redis_client.lrange(key, -n, -1)
            
            # Deserialize items in reverse order (newest first)
            return [
                self._deserialize(item.decode("utf-8") if isinstance(item, bytes) else item)
                for item in reversed(items)
            ]
        except Exception as e:
            print(f"Error getting latest items from ring buffer: {e}")
            return []

    def clear(self, key: str) -> bool:
        """Clear the ring buffer.

        Args:
            key (str): The Redis key for this buffer

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Error clearing ring buffer: {e}")
            return False

    def size(self, key: str) -> int:
        """Get the current number of items in the buffer.

        Args:
            key (str): The Redis key for this buffer

        Returns:
            int: Number of items in the buffer
        """
        try:
            return self.redis_client.llen(key)
        except Exception as e:
            print(f"Error getting ring buffer size: {e}")
            return 0 