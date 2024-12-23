from typing import Any, Optional
from typing import Set as PySet

from .base import RedisDataStructure


class Set(RedisDataStructure):
    """A Redis-backed set implementation.

    This class implements a set data structure using Redis sets, ensuring uniqueness
    of elements and providing O(1) add/remove operations. It's perfect for tracking
    unique items like user sessions, maintaining lists of unique identifiers, and
    implementing features that require set operations like unions and intersections.

    All operations (add, remove, contains) are O(1) as they leverage Redis's native
    set operations. The implementation handles serialization of complex Python objects
    while maintaining the performance characteristics of Redis sets.
    """

    def add(self, key: str, data: Any) -> bool:
        """Add an item to the set.

        This operation is O(1) as it uses Redis's SADD command directly.
        The data is serialized with type information to ensure proper
        deserialization later.

        Args:
            key: The Redis key for this set
            data: Data to be stored. Can be any serializable Python object.

        Returns:
            bool: True if the item was added, False if it was already present
        """
        try:
            serialized = self._serialize(data, include_timestamp=False)
            return bool(self.redis_client.sadd(key, serialized))
        except Exception as e:
            print(f"Error adding to set: {e}")
            return False

    def remove(self, key: str, data: Any) -> bool:
        """Remove an item from the set.

        This operation is O(1) as it uses Redis's SREM command directly.
        The data is serialized to match the stored format for removal.

        Args:
            key: The Redis key for this set
            data: Data to be removed

        Returns:
            bool: True if the item was removed, False if it wasn't present
        """
        try:
            serialized = self._serialize(data, include_timestamp=False)
            return bool(self.redis_client.srem(key, serialized))
        except Exception as e:
            print(f"Error removing from set: {e}")
            return False

    def contains(self, key: str, data: Any) -> bool:
        """Check if an item exists in the set.

        This operation is O(1) as it uses Redis's SISMEMBER command directly.
        The data is serialized to match the stored format for comparison.

        Args:
            key: The Redis key for this set
            data: Data to check for existence

        Returns:
            bool: True if the item exists, False otherwise
        """
        try:
            serialized = self._serialize(data, include_timestamp=False)
            return bool(self.redis_client.sismember(key, serialized))
        except Exception as e:
            print(f"Error checking set membership: {e}")
            return False

    def members(self, key: str) -> PySet[Any]:
        """Get all members of the set.

        This operation is O(N) where N is the size of the set.
        All items are deserialized back to their original Python types.

        Args:
            key: The Redis key for this set

        Returns:
            Set[Any]: Set containing all members with their original types
        """
        try:
            items = self.redis_client.smembers(key)
            if not items:
                return set()

            result = set()
            for item in items:
                try:
                    if isinstance(item, bytes):
                        item = item.decode("utf-8")
                    deserialized = self._deserialize(item, include_timestamp=False)
                    result.add(deserialized)
                except Exception as e:
                    print(f"Error deserializing item: {e}")
                    continue
            return result
        except Exception as e:
            print(f"Error getting set members: {e}")
            return set()

    def size(self, key: str) -> int:
        """Get the number of items in the set.

        This operation is O(1) as it uses Redis's SCARD command directly.

        Args:
            key: The Redis key for this set

        Returns:
            int: Number of items in the set
        """
        try:
            result = self.redis_client.scard(key)
            return int(result if result is not None else 0)
        except Exception as e:
            print(f"Error getting set size: {e}")
            return 0

    def pop(self, key: str) -> Optional[Any]:
        """Remove and return a random element from the set.

        This operation is O(1) as it uses Redis's SPOP command directly.

        Args:
            key: The Redis key for this set

        Returns:
            Optional[Any]: Random element if successful, None if set is empty
        """
        try:
            data = self.redis_client.spop(key)
            if data is not None:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data, include_timestamp=False)
            return None
        except Exception as e:
            print(f"Error popping from set: {e}")
            return None
