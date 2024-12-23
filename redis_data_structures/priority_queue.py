from typing import Any, Optional, Tuple

from .base import RedisDataStructure


class PriorityQueue(RedisDataStructure):
    """A Redis-backed priority queue implementation.

    This class implements a priority queue using Redis sorted sets, where elements
    are ordered by their priority (lower number = higher priority). It's perfect for
    implementing task schedulers, job queues, and other systems where items need
    to be processed based on their relative importance or urgency.
    """

    def push(self, key: str, data: Any, priority: int = 0) -> bool:
        """Push an item onto the priority queue.

        Args:
            key (str): The Redis key for this priority queue
            data (Any): Data to be stored
            priority (int): Priority level (lower number = higher priority)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized = self._serialize(data)
            return bool(self.redis_client.zadd(key, {serialized: priority}))
        except Exception as e:
            print(f"Error pushing to priority queue: {e}")
            return False

    def pop(self, key: str) -> Optional[Tuple[Any, int]]:
        """Pop the highest priority item from the queue.

        Args:
            key (str): The Redis key for this priority queue

        Returns:
            Optional[Tuple[Any, int]]: Tuple of (data, priority) if successful, None otherwise
        """
        try:
            # Get the first item (lowest score = highest priority)
            items = self.redis_client.zrange(key, 0, 0, withscores=True)
            if not items:
                return None

            item, priority = items[0]
            # Handle bytes if Redis returns bytes
            if isinstance(item, bytes):
                item = item.decode("utf-8")

            # Remove the item from the queue
            self.redis_client.zrem(key, item)

            return self._deserialize(item), int(priority)
        except Exception as e:
            print(f"Error popping from priority queue: {e}")
            return None

    def peek(self, key: str) -> Optional[Tuple[Any, int]]:
        """Peek at the highest priority item without removing it.

        Args:
            key (str): The Redis key for this priority queue

        Returns:
            Optional[Tuple[Any, int]]: Tuple of (data, priority) if successful, None otherwise
        """
        try:
            items = self.redis_client.zrange(key, 0, 0, withscores=True)
            if not items:
                return None

            item, priority = items[0]
            # Handle bytes if Redis returns bytes
            if isinstance(item, bytes):
                item = item.decode("utf-8")

            return self._deserialize(item), int(priority)
        except Exception as e:
            print(f"Error peeking priority queue: {e}")
            return None

    def size(self, key: str) -> int:
        """Get the size of the priority queue.

        Args:
            key (str): The Redis key for this priority queue

        Returns:
            int: Number of elements in the priority queue
        """
        try:
            return self.redis_client.zcard(key)
        except Exception as e:
            print(f"Error getting priority queue size: {e}")
            return 0
