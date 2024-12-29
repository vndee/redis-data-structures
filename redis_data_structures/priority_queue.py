import logging
from typing import Generic, Optional, Tuple, TypeVar

from .base import RedisDataStructure, atomic_operation, handle_operation_error

logger = logging.getLogger(__name__)

T = TypeVar("T")


class PriorityQueue(RedisDataStructure, Generic[T]):
    """A Redis-backed priority queue implementation.

    This class implements a priority queue using Redis sorted sets, where elements
    are ordered by their priority (lower number = higher priority). It's perfect for
    implementing task schedulers, job queues, and other systems where items need
    to be processed based on their relative importance or urgency.
    """

    @atomic_operation
    @handle_operation_error
    def push(self, data: T, priority: int = 0) -> bool:
        """Push an item onto the priority queue.

        Args:
            data (T): Data to be stored
            priority (int): Priority level (lower number = higher priority)

        Returns:
            bool: True if successful, False otherwise
        """
        serialized = self.serializer.serialize(data)
        # Redis zadd expects mapping of {member: score}
        mapping = {serialized: float(priority)}
        return bool(self.connection_manager.execute("zadd", self.key, mapping=mapping))

    @atomic_operation
    @handle_operation_error
    def pop(self) -> Optional[Tuple[T, int]]:
        """Pop the highest priority item from the queue.

        Returns:
            Optional[Tuple[T, int]]: Tuple of (data, priority) if successful, None otherwise
        """
        items = self.connection_manager.execute("zrange", self.key, 0, 0, withscores=True)
        if not items:
            return None

        # Redis returns a list of tuples [(member, score)]
        item, priority = items[0]

        # Remove the item from the queue
        if not self.connection_manager.execute("zrem", self.key, item):
            logger.exception("Failed to remove item from priority queue")
            return None

        return self.serializer.deserialize(item), int(float(priority))

    @atomic_operation
    @handle_operation_error
    def peek(self) -> Optional[Tuple[T, int]]:
        """Peek at the highest priority item without removing it.

        Returns:
            Optional[Tuple[T, int]]: Tuple of (data, priority) if successful, None otherwise
        """
        items = self.connection_manager.execute("zrange", self.key, 0, 0, withscores=True)
        if not items:
            return None

        # Redis returns a list of tuples [(member, score)]
        item, priority = items[0]

        return self.serializer.deserialize(item), int(float(priority))

    @atomic_operation
    @handle_operation_error
    def size(self) -> int:
        """Get the number of items in the priority queue.

        Returns:
            int: Number of items in the queue
        """
        return self.connection_manager.execute("zcard", self.key) or 0

    @atomic_operation
    @handle_operation_error
    def clear(self) -> bool:
        """Clear all items from the priority queue.

        Returns:
            bool: True if successful, False otherwise
        """
        return bool(self.connection_manager.execute("delete", self.key))

    @atomic_operation
    @handle_operation_error
    def get_all(self) -> list:
        """Get all items in the priority queue without removing them.

        Returns:
            list: List of (data, priority) tuples in priority order
        """
        items = self.connection_manager.execute("zrange", self.key, 0, -1, withscores=True)
        if not items:
            return []

        return [
            (self.serializer.deserialize(item), int(float(priority))) for item, priority in items
        ]
