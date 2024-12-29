import logging
from typing import Any, Optional

from .base import RedisDataStructure, handle_operation_error

logger = logging.getLogger(__name__)


class Queue(RedisDataStructure):
    """A Redis-backed FIFO (First-In-First-Out) queue implementation.

    This class implements a queue data structure using Redis lists, where elements
    are added to the back and removed from the front, following FIFO order.
    """

    @handle_operation_error
    def push(self, data: Any) -> bool:
        """Push an item to the back of the queue.

        Args:
            data (Any): Data to be stored

        Returns:
            bool: True if successful, False otherwise
        """
        serialized = self.serializer.serialize(data)
        return bool(self.connection_manager.execute("rpush", self.key, serialized))

    @handle_operation_error
    def pop(self) -> Optional[Any]:
        """Pop an item from the front of the queue.

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        data = self.connection_manager.execute("lpop", self.key)
        return self.serializer.deserialize(data) if data else None

    @handle_operation_error
    def peek(self) -> Optional[Any]:
        """Peek at the front item without removing it.

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        data = self.connection_manager.execute("lindex", self.key, 0)
        return self.serializer.deserialize(data) if data else None

    @handle_operation_error
    def size(self) -> int:
        """Get the number of items in the queue.

        Returns:
            int: Number of items in the queue
        """
        return self.connection_manager.execute("llen", self.key) or 0

    @handle_operation_error
    def clear(self) -> bool:
        """Clear all items from the queue.

        Returns:
            bool: True if successful, False otherwise
        """
        return bool(self.connection_manager.execute("delete", self.key))
