import logging
from typing import Any, List, Optional

from .base import RedisDataStructure, atomic_operation, handle_operation_error

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

    @atomic_operation
    @handle_operation_error
    def members(self) -> List[Any]:
        """Get all members of the set.

        This operation is O(N) where N is the size of the set.
        All items are deserialized back to their original Python types.

        Returns:
            Set[Any]: Set containing all members with their original types
        """
        items = self.connection_manager.execute("smembers", self.key)
        if not items:
            return []

        return [self.serializer.deserialize(item) for item in items]

    @atomic_operation
    @handle_operation_error
    def pop(self) -> Optional[Any]:
        """Remove and return a random element from the set.

        This operation is O(1) as it uses Redis's SPOP command directly.

        Returns:
            Optional[Any]: Random element if successful, None if set is empty
        """
        data = self.connection_manager.execute("spop", self.key)
        return self.serializer.deserialize(data) if data else None

    @atomic_operation
    @handle_operation_error
    def add(self, data: Any) -> bool:
        """Add an item to the set.

        This operation is O(1) as it uses Redis's SADD command directly.
        The data is serialized with type information to ensure proper
        deserialization later.

        Args:
            data: Data to be stored. Can be any serializable Python object.

        Returns:
            bool: True if the item was added, False if it was already present
        """
        serialized = self.serializer.serialize(data)
        result = self.connection_manager.execute("sadd", self.key, serialized)
        return bool(result)  # sadd returns 1 if added, 0 if already exists

    @atomic_operation
    @handle_operation_error
    def remove(self, data: Any) -> bool:
        """Remove an item from the set.

        This operation is O(1) as it uses Redis's SREM command directly.
        The data is serialized to match the stored format for removal.

        Args:
            data: Data to be removed

        Returns:
            bool: True if the item was removed, False if it wasn't present
        """
        serialized = self.serializer.serialize(data)
        result = self.connection_manager.execute("srem", self.key, serialized)
        return bool(result)  # srem returns 1 if removed, 0 if not found

    @atomic_operation
    @handle_operation_error
    def contains(self, data: Any) -> bool:
        """Check if an item exists in the set.

        This operation is O(1) as it uses Redis's SISMEMBER command directly.
        The data is serialized to match the stored format for comparison.

        Args:
            data: Data to check for existence

        Returns:
            bool: True if the item exists, False otherwise
        """
        serialized = self.serializer.serialize(data)
        result = self.connection_manager.execute("sismember", self.key, serialized)
        return bool(result)  # sismember returns 1 if exists, 0 otherwise

    @atomic_operation
    @handle_operation_error
    def size(self) -> int:
        """Get the number of items in the set.

        This operation is O(1) as it uses Redis's SCARD command directly.

        Returns:
            int: Number of items in the set
        """
        result = self.connection_manager.execute("scard", self.key)
        return int(result)  # scard returns integer count

    @atomic_operation
    @handle_operation_error
    def clear(self) -> bool:
        """Remove all elements from the set.

        This operation is O(1) as it uses Redis's DELETE command directly.

        Returns:
            bool: True if successful, False otherwise
        """
        self.connection_manager.execute("delete", self.key)
        return True
