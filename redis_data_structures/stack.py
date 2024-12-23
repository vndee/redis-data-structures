from typing import Any, Optional
import logging

from .base import RedisDataStructure
from .metrics import track_operation

logger = logging.getLogger(__name__)


class Stack(RedisDataStructure):
    """A Redis-backed LIFO (Last-In-First-Out) stack implementation.

    This class implements a stack data structure using Redis lists, where elements
    are added to the front and removed from the front, following LIFO order.
    """

    @track_operation("push")
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
            return bool(
                self.connection_manager.execute(
                    "lpush",
                    self._get_key(key),
                    serialized
                )
            )
        except Exception as e:
            logger.error(f"Error pushing to stack: {e}")
            return False

    @track_operation("pop")
    def pop(self, key: str) -> Optional[Any]:
        """Pop an item from the top of the stack.

        Args:
            key (str): The Redis key for this stack

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.connection_manager.execute(
                "lpop",
                self._get_key(key)
            )
            if data:
                # Handle bytes response from Redis
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data)
            return None
        except Exception as e:
            logger.error(f"Error popping from stack: {e}")
            return None

    @track_operation("peek")
    def peek(self, key: str) -> Optional[Any]:
        """Peek at the top item without removing it.

        Args:
            key (str): The Redis key for this stack

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.connection_manager.execute(
                "lindex",
                self._get_key(key),
                0
            )
            if data:
                # Handle bytes response from Redis
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data)
            return None
        except Exception as e:
            logger.error(f"Error peeking stack: {e}")
            return None

    @track_operation("size")
    def size(self, key: str) -> int:
        """Get the size of the stack.

        Args:
            key (str): The Redis key for this stack

        Returns:
            int: Number of elements in the stack
        """
        try:
            return self.connection_manager.execute(
                "llen",
                self._get_key(key)
            ) or 0
        except Exception as e:
            logger.error(f"Error getting stack size: {e}")
            return 0
