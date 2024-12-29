import logging
from typing import Any, Optional

from .base import RedisDataStructure, atomic_operation, handle_operation_error

logger = logging.getLogger(__name__)


class Deque(RedisDataStructure):
    """A Redis-backed double-ended queue implementation.

    This class implements a deque (double-ended queue) using Redis lists, allowing
    efficient insertion and removal of elements at both ends. It's ideal for
    implementing features like browser history navigation, work stealing queues,
    and other scenarios requiring bidirectional access to the data structure.
    """

    @atomic_operation
    @handle_operation_error
    def push_front(self, data: Any) -> bool:
        """Push an item to the front of the deque.

        Args:
            data (Any): Data to be stored

        Returns:
            bool: True if successful, False otherwise
        """
        serialized = self.serializer.serialize(data)
        return bool(self.connection_manager.execute("lpush", self.key, serialized))

    @atomic_operation
    @handle_operation_error
    def push_back(self, data: Any) -> bool:
        """Push an item to the back of the deque.

        Args:
            data (Any): Data to be stored

        Returns:
            bool: True if successful, False otherwise
        """
        serialized = self.serializer.serialize(data)
        return bool(self.connection_manager.execute("rpush", self.key, serialized))

    @atomic_operation
    @handle_operation_error
    def pop_front(self) -> Optional[Any]:
        """Pop an item from the front of the deque.

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        data = self.connection_manager.execute("lpop", self.key)
        return self.serializer.deserialize(data)

    @atomic_operation
    @handle_operation_error
    def pop_back(self) -> Optional[Any]:
        """Pop an item from the back of the deque.

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        data = self.connection_manager.execute("rpop", self.key)
        return self.serializer.deserialize(data)

    @atomic_operation
    @handle_operation_error
    def peek_front(self) -> Optional[Any]:
        """Peek at the front item without removing it.

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        data = self.connection_manager.execute("lindex", self.key, 0)
        return self.serializer.deserialize(data)

    @atomic_operation
    @handle_operation_error
    def peek_back(self) -> Optional[Any]:
        """Peek at the back item without removing it.

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        data = self.connection_manager.execute("lindex", self.key, -1)
        return self.serializer.deserialize(data)

    @atomic_operation
    @handle_operation_error
    def size(self) -> int:
        """Get the size of the deque.

        Returns:
            int: Number of elements in the deque
        """
        return self.connection_manager.execute("llen", self.key) or 0
