import logging
from typing import Any, Optional

from .base import RedisDataStructure, atomic_operation, handle_operation_error

logger = logging.getLogger(__name__)


class Stack(RedisDataStructure):
    """A Redis-backed LIFO (Last-In-First-Out) stack implementation.

    This class implements a stack data structure using Redis lists, where elements
    are added to the front and removed from the front, following LIFO order.
    """

    @atomic_operation
    @handle_operation_error
    def push(self, data: Any) -> bool:
        """Push an item onto the top of the stack.

        Args:
            data (Any): Data to be stored. Can be any serializable Python object.

        Returns:
            bool: True if successful, False otherwise
        """
        serialized = self.serializer.serialize(data)
        result = self.connection_manager.execute("lpush", self.key, serialized)
        return bool(result)

    @atomic_operation
    @handle_operation_error
    def pop(self) -> Optional[Any]:
        """Pop an item from the top of the stack.

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        data = self.connection_manager.execute("lpop", self.key)
        return self.serializer.deserialize(data) if data else None

    @atomic_operation
    @handle_operation_error
    def peek(self) -> Optional[Any]:
        """Peek at the top item without removing it.

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        data = self.connection_manager.execute("lindex", self.key, 0)
        return self.serializer.deserialize(data) if data else None

    @atomic_operation
    @handle_operation_error
    def size(self) -> int:
        """Get the size of the stack.

        Returns:
            int: Number of elements in the stack
        """
        result = self.connection_manager.execute("llen", self.key)
        return int(result) if result is not None else 0

    @atomic_operation
    @handle_operation_error
    def clear(self) -> bool:
        """Remove all elements from the stack.

        Returns:
            bool: True if successful, False otherwise
        """
        self.connection_manager.execute("delete", self.key)
        return True
