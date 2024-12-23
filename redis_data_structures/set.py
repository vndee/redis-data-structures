from typing import Any, Optional, Tuple
from typing import Set as PySet
import json
import logging

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


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

    def _restore_type(self, value: Any) -> Any:
        """Restore original type from deserialized value."""
        if not isinstance(value, dict) or "_type" not in value:
            return value

        type_name = value.get("_type")
        data = value.get("value")

        if type_name == "NoneType":
            return None
        elif type_name in ("int", "float", "str", "bool"):
            return data
        elif type_name == "list":
            return [self._restore_type(item) for item in data]
        elif type_name == "dict":
            return {k: self._restore_type(v) for k, v in data.items()}
        elif type_name == "tuple":
            return tuple(self._restore_type(item) for item in data)
        elif type_name == "set":
            return set(self._restore_type(item) for item in data)
        
        return data

    def _make_hashable(self, value: Any) -> Any:
        """Convert value to a hashable type."""
        if isinstance(value, (int, float, str, bool, tuple)) or value is None:
            return value
        if isinstance(value, list):
            return tuple(self._make_hashable(item) for item in value)
        if isinstance(value, dict):
            return tuple(sorted((k, self._make_hashable(v)) for k, v in value.items()))
        if isinstance(value, set):
            return tuple(sorted(self._make_hashable(item) for item in value))
        return str(value)

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
            items = self.connection_manager.execute(
                "smembers",
                self._get_key(key)
            )
            if not items:
                return set()

            result = []
            for item in items:
                try:
                    if isinstance(item, bytes):
                        item = item.decode("utf-8")
                    deserialized = self._deserialize(item)
                    restored = self._restore_type(deserialized)
                    result.append(restored)
                except Exception as e:
                    logger.error(f"Error processing item: {e}")
                    continue

            return result
        except Exception as e:
            logger.error(f"Error getting set members: {e}")
            return set()

    def pop(self, key: str) -> Optional[Any]:
        """Remove and return a random element from the set.

        This operation is O(1) as it uses Redis's SPOP command directly.

        Args:
            key: The Redis key for this set

        Returns:
            Optional[Any]: Random element if successful, None if set is empty
        """
        try:
            data = self.connection_manager.execute(
                "spop",
                self._get_key(key)
            )
            if data is not None:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                deserialized = self._deserialize(data)
                return self._restore_type(deserialized)
            return None
        except Exception as e:
            logger.error(f"Error popping from set: {e}")
            return None

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
            # Serialize the data directly without making it hashable
            serialized = self._serialize(data, include_timestamp=False)
            result = self.connection_manager.execute(
                "sadd",
                self._get_key(key),
                serialized
            )
            return bool(result)  # sadd returns 1 if added, 0 if already exists
        except Exception as e:
            logger.error(f"Error adding to set: {e}")
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
            # Serialize the data directly without making it hashable
            serialized = self._serialize(data, include_timestamp=False)
            result = self.connection_manager.execute(
                "srem",
                self._get_key(key),
                serialized
            )
            return bool(result)  # srem returns 1 if removed, 0 if not found
        except Exception as e:
            logger.error(f"Error removing from set: {e}")
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
            # Serialize the data directly without making it hashable
            serialized = self._serialize(data, include_timestamp=False)
            result = self.connection_manager.execute(
                "sismember",
                self._get_key(key),
                serialized
            )
            return bool(result)  # sismember returns 1 if exists, 0 otherwise
        except Exception as e:
            logger.error(f"Error checking set membership: {e}")
            return False

    def size(self, key: str) -> int:
        """Get the number of items in the set.

        This operation is O(1) as it uses Redis's SCARD command directly.

        Args:
            key: The Redis key for this set

        Returns:
            int: Number of items in the set
        """
        try:
            result = self.connection_manager.execute(
                "scard",
                self._get_key(key)
            )
            return int(result)  # scard returns integer count
        except Exception as e:
            logger.error(f"Error getting set size: {e}")
            return 0

    def clear(self, key: str) -> bool:
        """Remove all elements from the set.

        This operation is O(1) as it uses Redis's DELETE command directly.

        Args:
            key: The Redis key for this set

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.connection_manager.execute(
                "delete",
                self._get_key(key)
            )
            return True
        except Exception as e:
            logger.error(f"Error clearing set: {e}")
            return False
