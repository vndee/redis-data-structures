from typing import Any, Optional

from .base import RedisDataStructure


class Queue(RedisDataStructure):
    """A Redis-backed FIFO (First-In-First-Out) queue implementation.

    This class implements a queue data structure using Redis lists, where elements
    are added to the back and removed from the front, following FIFO order.
    """

    def push(self, key: str, data: Any) -> bool:
        """Push an item to the back of the queue.

        Args:
            key (str): The Redis key for this queue
            data (Any): Data to be stored

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized = self._serialize(data)
            return bool(self.redis_client.rpush(key, serialized))
        except Exception as e:
            print(f"Error pushing to queue: {e}")
            return False

    def pop(self, key: str) -> Optional[Any]:
        """Pop an item from the front of the queue.

        Args:
            key (str): The Redis key for this queue

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.redis_client.lpop(key)
            if data:
                # Handle bytes response from Redis
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data)
            return None
        except Exception as e:
            print(f"Error popping from queue: {e}")
            return None

    def peek(self, key: str) -> Optional[Any]:
        """Peek at the front item without removing it.

        Args:
            key (str): The Redis key for this queue

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.redis_client.lindex(key, 0)
            if data:
                # Handle bytes response from Redis
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data)
            return None
        except Exception as e:
            print(f"Error peeking queue: {e}")
            return None

    def size(self, key: str) -> int:
        """Get the size of the queue.

        Args:
            key (str): The Redis key for this queue

        Returns:
            int: Number of elements in the queue
        """
        try:
            return self.redis_client.llen(key)
        except Exception as e:
            print(f"Error getting queue size: {e}")
            return 0
