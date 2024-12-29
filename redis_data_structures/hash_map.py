import logging
from typing import Dict, Generic, List, Optional, Tuple, TypeVar

from .base import RedisDataStructure, atomic_operation, handle_operation_error

logger = logging.getLogger(__name__)

K = TypeVar("K")
V = TypeVar("V")


class HashMap(RedisDataStructure, Generic[K, V]):
    """A Redis-backed hash map implementation.

    This class implements a hash map data structure using Redis hashes, providing
    key-value storage with type preservation.
    """

    @atomic_operation
    @handle_operation_error
    def set(self, key: K, value: V) -> bool:
        """Set a key in the hash map.

        Args:
            key (K): The key to store
            value (V): The value to store

        Returns:
            bool: True if successful, False otherwise
        """
        serialized = self.serializer.serialize(value)
        key = self.serializer.serialize(key, force_compression=False, decode=True)

        logger.debug(f"Setting key {key} with serialized value: {serialized}")
        return bool(self.connection_manager.execute("hset", self.key, key, serialized))

    @atomic_operation
    @handle_operation_error
    def get(self, key: K) -> Optional[V]:
        """Get a key from the hash map.

        Args:
            key (K): The key to get

        Returns:
            Optional[V]: The value if successful, None otherwise
        """
        key = self.serializer.serialize(key, force_compression=False, decode=True)

        data = self.connection_manager.execute("hget", self.key, key)
        return self.serializer.deserialize(data) if data else None

    @atomic_operation
    @handle_operation_error
    def delete(self, key: K) -> bool:
        """Delete a key from the hash map.

        Args:
            key (K): The key to delete

        Returns:
            bool: True if successful, False otherwise
        """
        key = self.serializer.serialize(key, force_compression=False, decode=True)
        return bool(self.connection_manager.execute("hdel", self.key, key))

    @atomic_operation
    @handle_operation_error
    def exists(self, key: K) -> bool:
        """Check if a key exists in the hash map.

        Args:
            key (K): The key to check

        Returns:
            bool: True if the key exists, False otherwise
        """
        key = self.serializer.serialize(key, force_compression=False, decode=True)
        return bool(self.connection_manager.execute("hexists", self.key, key))

    @atomic_operation
    @handle_operation_error
    def get_all(self) -> Dict[K, V]:
        """Get all keys and values from the hash map.

        Returns:
            Dict[K, V]: Dictionary of key-value pairs
        """
        data = self.connection_manager.execute("hgetall", self.key)
        if not data:
            return {}

        return {
            self.serializer.deserialize(k): self.serializer.deserialize(v) for k, v in data.items()
        }

    @atomic_operation
    @handle_operation_error
    def get_keys(self) -> List[K]:
        """Get all keys from the hash map.

        Returns:
            List[K]: List of keys
        """
        keys = self.connection_manager.execute("hkeys", self.key)
        return [self.serializer.deserialize(key) for key in keys]

    @atomic_operation
    @handle_operation_error
    def size(self) -> int:
        """Get the number of fields in the hash map.

        Returns:
            int: Number of keys
        """
        return self.connection_manager.execute("hlen", self.key) or 0

    @atomic_operation
    @handle_operation_error
    def clear(self) -> bool:
        """Clear all fields from the hash map.

        Returns:
            bool: True if successful, False otherwise
        """
        self.connection_manager.execute("delete", self.key)
        return True

    @atomic_operation
    @handle_operation_error
    def keys(self) -> List[K]:
        """Get all keys from the hash map."""
        return self.get_keys()

    @atomic_operation
    @handle_operation_error
    def values(self) -> List[V]:
        """Get all values from the hash map."""
        return [self.get(key) for key in self.keys()]  # type: ignore[misc]

    @atomic_operation
    @handle_operation_error
    def items(self) -> List[Tuple[K, V]]:
        """Get all key-value pairs from the hash map."""
        return [(key, self.get(key)) for key in self.keys()]  # type: ignore[misc]

    @atomic_operation
    @handle_operation_error
    def __contains__(self, key: K) -> bool:
        """Check if a key exists in the hash map."""
        return self.exists(key)

    @atomic_operation
    @handle_operation_error
    def __getitem__(self, key: K) -> V:
        """Get a value from the hash map using the subscript operator."""
        return self.get(key)  # type: ignore[return-value]

    @atomic_operation
    @handle_operation_error
    def __setitem__(self, key: K, value: V) -> None:
        """Set a value in the hash map using the subscript operator."""
        self.set(key, value)

    @atomic_operation
    @handle_operation_error
    def __delitem__(self, key: K) -> None:
        """Delete a key-value pair from the hash map using the subscript operator."""
        self.delete(key)
