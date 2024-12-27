import logging
from typing import Any, Optional

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


class Queue(RedisDataStructure):
    """A Redis-backed FIFO (First-In-First-Out) queue implementation.

    This class implements a queue data structure using Redis lists, where elements
    are added to the back and removed from the front, following FIFO order.
    """

    def push(self, data: Any) -> bool:
        """Push an item to the back of the queue.

        Args:
            data (Any): Data to be stored

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized = self.serializer.serialize(data)
            return bool(self.connection_manager.execute("rpush", self.key, serialized))
        except Exception:
            logger.exception("Error pushing to queue")
            return False

    def pop(self) -> Optional[Any]:
        """Pop an item from the front of the queue.

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.connection_manager.execute("lpop", self.key)
            return self.serializer.deserialize(data) if data else None
        except Exception:
            logger.exception("Error popping from queue")
            return None

    def peek(self) -> Optional[Any]:
        """Peek at the front item without removing it.

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.connection_manager.execute("lindex", self.key, 0)
            return self.serializer.deserialize(data) if data else None
        except Exception:
            logger.exception("Error peeking queue")
            return None

    def size(self) -> int:
        """Get the number of items in the queue.

        Returns:
            int: Number of items in the queue
        """
        try:
            return self.connection_manager.execute("llen", self.key) or 0
        except Exception:
            logger.exception("Error getting queue size")
            return 0

    def clear(self) -> bool:
        """Clear all items from the queue.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return bool(self.connection_manager.execute("delete", self.key))
        except Exception:
            logger.exception("Error clearing queue")
            return False
