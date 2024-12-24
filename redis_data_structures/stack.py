import logging
from typing import Any, Optional

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


class Stack(RedisDataStructure):
    """A Redis-backed LIFO (Last-In-First-Out) stack implementation.

    This class implements a stack data structure using Redis lists, where elements
    are added to the front and removed from the front, following LIFO order.
    """

    def push(self, key: str, data: Any) -> bool:
        """Push an item onto the top of the stack.

        Args:
            key (str): The Redis key for this stack
            data (Any): Data to be stored. Can be any serializable Python object.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized = self.serialize(data, include_timestamp=False)
            result = self.connection_manager.execute("lpush", self._get_key(key), serialized)
            return bool(result)
        except Exception:
            logger.exception("Error pushing to stack")
            return False

    def pop(self, key: str) -> Optional[Any]:
        """Pop an item from the top of the stack.

        Args:
            key (str): The Redis key for this stack

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.connection_manager.execute("lpop", self._get_key(key))
            if data is not None:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self.deserialize(data)
            return None
        except Exception:
            logger.exception("Error popping from stack")
            return None

    def peek(self, key: str) -> Optional[Any]:
        """Peek at the top item without removing it.

        Args:
            key (str): The Redis key for this stack

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.connection_manager.execute("lindex", self._get_key(key), 0)
            if data is not None:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self.deserialize(data)
            return None
        except Exception:
            logger.exception("Error peeking stack")
            return None

    def size(self, key: str) -> int:
        """Get the size of the stack.

        Args:
            key (str): The Redis key for this stack

        Returns:
            int: Number of elements in the stack
        """
        try:
            result = self.connection_manager.execute("llen", self._get_key(key))
            return int(result) if result is not None else 0
        except Exception:
            logger.exception("Error getting stack size")
            return 0

    def clear(self, key: str) -> bool:
        """Remove all elements from the stack.

        Args:
            key (str): The Redis key for this stack

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.connection_manager.execute("delete", self._get_key(key))
            return True
        except Exception:
            logger.exception("Error clearing stack")
            return False
