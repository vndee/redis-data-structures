from typing import Any, Optional
import logging

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


class Deque(RedisDataStructure):
    """A Redis-backed double-ended queue implementation.

    This class implements a deque (double-ended queue) using Redis lists, allowing
    efficient insertion and removal of elements at both ends. It's ideal for
    implementing features like browser history navigation, work stealing queues,
    and other scenarios requiring bidirectional access to the data structure.
    """

    def push_front(self, key: str, data: Any) -> bool:
        """Push an item to the front of the deque.

        Args:
            key (str): The Redis key for this deque
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
            logger.error(f"Error pushing to front of deque: {e}")
            return False

    def push_back(self, key: str, data: Any) -> bool:
        """Push an item to the back of the deque.

        Args:
            key (str): The Redis key for this deque
            data (Any): Data to be stored

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized = self._serialize(data)
            return bool(
                self.connection_manager.execute(
                    "rpush",
                    self._get_key(key),
                    serialized
                )
            )
        except Exception as e:
            logger.error(f"Error pushing to back of deque: {e}")
            return False

    def pop_front(self, key: str) -> Optional[Any]:
        """Pop an item from the front of the deque.

        Args:
            key (str): The Redis key for this deque

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
            logger.error(f"Error popping from front of deque: {e}")
            return None

    def pop_back(self, key: str) -> Optional[Any]:
        """Pop an item from the back of the deque.

        Args:
            key (str): The Redis key for this deque

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.connection_manager.execute(
                "rpop",
                self._get_key(key)
            )
            if data:
                # Handle bytes response from Redis
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data)
            return None
        except Exception as e:
            logger.error(f"Error popping from back of deque: {e}")
            return None

    def peek_front(self, key: str) -> Optional[Any]:
        """Peek at the front item without removing it.

        Args:
            key (str): The Redis key for this deque

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
            logger.error(f"Error peeking front of deque: {e}")
            return None

    def peek_back(self, key: str) -> Optional[Any]:
        """Peek at the back item without removing it.

        Args:
            key (str): The Redis key for this deque

        Returns:
            Optional[Any]: The data if successful, None otherwise
        """
        try:
            data = self.connection_manager.execute(
                "lindex",
                self._get_key(key),
                -1
            )
            if data:
                # Handle bytes response from Redis
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data)
            return None
        except Exception as e:
            logger.error(f"Error peeking back of deque: {e}")
            return None

    def size(self, key: str) -> int:
        """Get the size of the deque.

        Args:
            key (str): The Redis key for this deque

        Returns:
            int: Number of elements in the deque
        """
        try:
            return self.connection_manager.execute(
                "llen",
                self._get_key(key)
            ) or 0
        except Exception as e:
            logger.error(f"Error getting deque size: {e}")
            return 0
