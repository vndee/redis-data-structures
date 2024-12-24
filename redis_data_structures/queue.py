import logging
from typing import Any, Optional

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


class Queue(RedisDataStructure):
    """A Redis-backed FIFO (First-In-First-Out) queue implementation.

    This class implements a queue data structure using Redis lists, where elements
    are added to the back and removed from the front, following FIFO order.
    """

    def push(self, key: str, data: Any) -> bool:
        """Push an item to the back of the queue.

        Args:
            key (str): The Redis key for this queue
            data (Any): Data to be stored

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized = self.serialize(data)
            return bool(self.connection_manager.execute("rpush", self._get_key(key), serialized))
        except Exception:
            logger.exception("Error pushing to queue")
            return False

    def pop(self, key: str) -> Optional[Any]:
        """Pop an item from the front of the queue.

        Args:
            key (str): The Redis key for this queue

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.connection_manager.execute("lpop", self._get_key(key))
            if data:
                # Handle bytes response from Redis
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self.deserialize(data)
            return None
        except Exception:
            logger.exception("Error popping from queue")
            return None

    def peek(self, key: str) -> Optional[Any]:
        """Peek at the front item without removing it.

        Args:
            key (str): The Redis key for this queue

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.connection_manager.execute("lindex", self._get_key(key), 0)
            if data:
                # Handle bytes response from Redis
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self.deserialize(data)
            return None
        except Exception:
            logger.exception("Error peeking queue")
            return None

    def size(self, key: str) -> int:
        """Get the number of items in the queue.

        Args:
            key (str): The Redis key for this queue

        Returns:
            int: Number of items in the queue
        """
        try:
            return self.connection_manager.execute("llen", self._get_key(key)) or 0
        except Exception:
            logger.exception("Error getting queue size")
            return 0

    def clear(self, key: str) -> bool:
        """Clear all items from the queue.

        Args:
            key (str): The Redis key for this queue

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return bool(self.connection_manager.execute("delete", self._get_key(key)))
        except Exception:
            logger.exception("Error clearing queue")
            return False
