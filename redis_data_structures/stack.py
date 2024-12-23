from typing import Any, Optional

from .base import RedisDataStructure


class Stack(RedisDataStructure):
    """A Redis-backed LIFO (Last-In-First-Out) stack implementation.

    This class implements a stack data structure using Redis lists, where elements
    are pushed and popped from the same end, following LIFO order. It's suitable for
    implementing features like undo systems, navigation history, and other scenarios
    where the most recently added item should be processed first.
    """

    def push(self, key: str, data: Any) -> bool:
        """Push an item onto the top of the stack.

        Args:
            key (str): The Redis key for this stack
            data (Any): Data to be stored

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized = self._serialize(data)
            result = self.redis_client.lpush(key, serialized)
            return bool(result)
        except Exception as e:
            print(f"Error pushing to stack: {e}")
            return False

    def pop(self, key: str) -> Optional[Any]:
        """Pop an item from the top of the stack.

        Args:
            key (str): The Redis key for this stack

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.redis_client.lpop(key)
            if data is not None:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data)
            return None
        except Exception as e:
            print(f"Error popping from stack: {e}")
            return None

    def peek(self, key: str) -> Optional[Any]:
        """Peek at the top item without removing it.

        Args:
            key (str): The Redis key for this stack

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.redis_client.lindex(key, 0)
            if data is not None:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data)
            return None
        except Exception as e:
            print(f"Error peeking stack: {e}")
            return None

    def size(self, key: str) -> int:
        """Get the size of the stack.

        Args:
            key (str): The Redis key for this stack

        Returns:
            int: Number of elements in the stack
        """
        try:
            result = self.redis_client.llen(key)
            return int(result)
        except Exception as e:
            print(f"Error getting stack size: {e}")
            return 0
