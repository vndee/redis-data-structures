import logging
from typing import Generic, Optional, TypeVar

from .base import RedisDataStructure, atomic_operation, handle_operation_error

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Queue(RedisDataStructure, Generic[T]):
    """A Redis-backed FIFO (First-In-First-Out) queue implementation.

    This class implements a queue data structure using Redis lists, where elements
    are added to the back and removed from the front, following FIFO order.
    """

    @atomic_operation
    @handle_operation_error
    def push(self, data: T) -> bool:
        """Push an item to the back of the queue.

        Args:
            data (T): Data to be stored

        Returns:
            bool: True if successful, False otherwise
        """
        serialized = self.serializer.serialize(data)
        return bool(self.connection_manager.execute("rpush", self.key, serialized))

    @atomic_operation
    @handle_operation_error
    def pop(self) -> Optional[T]:
        """Pop an item from the front of the queue.

        Returns:
            Optional[T]: The data if successful, None otherwise
        """
        data = self.connection_manager.execute("lpop", self.key)
        return self.serializer.deserialize(data) if data else None

    @atomic_operation
    @handle_operation_error
    def peek(self) -> Optional[T]:
        """Peek at the front item without removing it.

        Returns:
            Optional[T]: The data if successful, None otherwise
        """
        data = self.connection_manager.execute("lindex", self.key, 0)
        return self.serializer.deserialize(data) if data else None

    @atomic_operation
    @handle_operation_error
    def size(self) -> int:
        """Get the number of items in the queue.

        Returns:
            int: Number of items in the queue
        """
        return self.connection_manager.execute("llen", self.key) or 0

    @atomic_operation
    @handle_operation_error
    def clear(self) -> bool:
        """Clear all items from the queue.

        Returns:
            bool: True if successful, False otherwise
        """
        return bool(self.connection_manager.execute("delete", self.key))
