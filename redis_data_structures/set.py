from typing import Any, Optional
from typing import Set as PySet

from .base import RedisDataStructure


class Set(RedisDataStructure):
    """A Redis-backed set implementation.

    This class implements a set data structure using Redis sets, ensuring uniqueness
    of elements and providing O(1) add/remove operations. It's perfect for tracking
    unique items like user sessions, maintaining lists of unique identifiers, and
    implementing features that require set operations like unions and intersections.
    """

    def _find_item(self, key: str, data: Any) -> Optional[str]:
        """Find the serialized item in the set that matches the given data.

        Args:
            key (str): The Redis key for this set
            data (Any): Data to find

        Returns:
            Optional[str]: Serialized item if found, None otherwise
        """
        try:
            items = self.redis_client.smembers(key)
            if isinstance(items, (set, list)):
                for item in items:
                    if isinstance(item, bytes):
                        item_str = item.decode("utf-8")
                        if self._deserialize(item_str)["data"] == data:
                            return item_str
            return None
        except Exception as e:
            print(f"Error finding item: {e}")
            return None

    def add(self, key: str, data: Any) -> bool:
        """Add an item to the set.

        Args:
            key (str): The Redis key for this set
            data (Any): Data to be stored

        Returns:
            bool: True if the item was added, False if it already existed
        """
        try:
            # First check if the item already exists
            if self.contains(key, data):
                return False

            # If not, add it
            serialized = self._serialize(data)
            result = self.redis_client.sadd(key, serialized)
            return bool(result)
        except Exception as e:
            print(f"Error adding to set: {e}")
            return False

    def remove(self, key: str, data: Any) -> bool:
        """Remove an item from the set.

        Args:
            key (str): The Redis key for this set
            data (Any): Data to be removed

        Returns:
            bool: True if the item was removed, False if it didn't exist
        """
        try:
            # Find the actual serialized item
            items = self.redis_client.smembers(key)
            if not items:
                return False

            for item in items:
                item_str = item.decode("utf-8") if isinstance(item, bytes) else item
                if self._deserialize(item_str)["data"] == data:
                    result = self.redis_client.srem(key, item)
                    return bool(result)
            return False
        except Exception as e:
            print(f"Error removing from set: {e}")
            return False

    def contains(self, key: str, data: Any) -> bool:
        """Check if an item exists in the set.

        Args:
            key (str): The Redis key for this set
            data (Any): Data to check

        Returns:
            bool: True if the item exists, False otherwise
        """
        try:
            items = self.redis_client.smembers(key)
            if not items:
                return False

            for item in items:
                item_str = item.decode("utf-8") if isinstance(item, bytes) else item
                if self._deserialize(item_str)["data"] == data:
                    return True
            return False
        except Exception as e:
            print(f"Error checking set membership: {e}")
            return False

    def members(self, key: str) -> PySet[Any]:
        """Get all members of the set.

        Args:
            key (str): The Redis key for this set

        Returns:
            Set[Any]: Set of all members
        """
        try:
            items = self.redis_client.smembers(key)
            if not items:
                return set()

            result = set()
            for item in items:
                item_str = item.decode("utf-8") if isinstance(item, bytes) else item
                result.add(self._deserialize(item_str)["data"])
            return result
        except Exception as e:
            print(f"Error getting set members: {e}")
            return set()

    def size(self, key: str) -> int:
        """Get the size of the set.

        Args:
            key (str): The Redis key for this set

        Returns:
            int: Number of elements in the set
        """
        try:
            result = self.redis_client.scard(key)
            return int(result if result is not None else 0)
        except Exception as e:
            print(f"Error getting set size: {e}")
            return 0

    def pop(self, key: str) -> Optional[Any]:
        """Remove and return a random element from the set.

        Args:
            key (str): The Redis key for this set

        Returns:
            Optional[Any]: Random element if successful, None if set is empty
        """
        try:
            data = self.redis_client.spop(key)
            if data is not None:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data)["data"]
            return None
        except Exception as e:
            print(f"Error popping from set: {e}")
            return None
