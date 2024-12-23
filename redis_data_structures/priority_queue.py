from typing import Any, Optional, Tuple
import logging

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


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
            cache_key = self._get_key(key)
            serialized = self._serialize(data)
            # Redis zadd expects mapping of {member: score}
            mapping = {serialized: float(priority)}
            return bool(
                self.connection_manager.execute(
                    "zadd",
                    cache_key,
                    mapping=mapping
                )
            )
        except Exception as e:
            logger.error(f"Error pushing to priority queue: {e}")
            return False

    def pop(self, key: str) -> Optional[Tuple[Any, int]]:
        """Pop the highest priority item from the queue.

        Args:
            key (str): The Redis key for this priority queue

        Returns:
            Optional[Tuple[Any, int]]: Tuple of (data, priority) if successful, None otherwise
        """
        try:
            cache_key = self._get_key(key)
            # Get the first item (lowest score = highest priority)
            items = self.connection_manager.execute(
                "zrange",
                cache_key,
                0,
                0,
                withscores=True
            )
            if not items:
                return None

            # Redis returns a list of tuples [(member, score)]
            item, priority = items[0]
            # Handle bytes if Redis returns bytes
            if isinstance(item, bytes):
                item = item.decode("utf-8")

            # Remove the item from the queue
            if not self.connection_manager.execute(
                "zrem",
                cache_key,
                item
            ):
                logger.error("Failed to remove item from priority queue")
                return None

            return self._deserialize(item), int(float(priority))
        except Exception as e:
            logger.error(f"Error popping from priority queue: {e}")
            return None

    def peek(self, key: str) -> Optional[Tuple[Any, int]]:
        """Peek at the highest priority item without removing it.

        Args:
            key (str): The Redis key for this priority queue

        Returns:
            Optional[Tuple[Any, int]]: Tuple of (data, priority) if successful, None otherwise
        """
        try:
            cache_key = self._get_key(key)
            # Get the first item without removing it
            items = self.connection_manager.execute(
                "zrange",
                cache_key,
                0,
                0,
                withscores=True
            )
            if not items:
                return None

            # Redis returns a list of tuples [(member, score)]
            item, priority = items[0]
            # Handle bytes if Redis returns bytes
            if isinstance(item, bytes):
                item = item.decode("utf-8")

            return self._deserialize(item), int(float(priority))
        except Exception as e:
            logger.error(f"Error peeking priority queue: {e}")
            return None

    def size(self, key: str) -> int:
        """Get the number of items in the priority queue.

        Args:
            key (str): The Redis key for this priority queue

        Returns:
            int: Number of items in the queue
        """
        try:
            return self.connection_manager.execute(
                "zcard",
                self._get_key(key)
            ) or 0
        except Exception as e:
            logger.error(f"Error getting priority queue size: {e}")
            return 0

    def clear(self, key: str) -> bool:
        """Clear all items from the priority queue.

        Args:
            key (str): The Redis key for this priority queue

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return bool(
                self.connection_manager.execute(
                    "delete",
                    self._get_key(key)
                )
            )
        except Exception as e:
            logger.error(f"Error clearing priority queue: {e}")
            return False

    def get_all(self, key: str) -> list:
        """Get all items in the priority queue without removing them.

        Args:
            key (str): The Redis key for this priority queue

        Returns:
            list: List of (data, priority) tuples in priority order
        """
        try:
            cache_key = self._get_key(key)
            items = self.connection_manager.execute(
                "zrange",
                cache_key,
                0,
                -1,
                withscores=True
            )
            if not items:
                return []

            result = []
            # items is a list of tuples [(member, score)]
            for item, priority in items:
                if isinstance(item, bytes):
                    item = item.decode("utf-8")
                result.append((self._deserialize(item), int(float(priority))))
            return result
        except Exception as e:
            logger.error(f"Error getting all items from priority queue: {e}")
            return []
