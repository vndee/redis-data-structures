import logging
from typing import Any, Generic, Iterator, List, Tuple, TypeVar
from typing import Dict as DictType

from .base import RedisDataStructure, atomic_operation, handle_operation_error

logger = logging.getLogger(__name__)

K = TypeVar("K")
V = TypeVar("V")


class Dict(RedisDataStructure, Generic[K, V]):
    """A python-like dictionary data structure for Redis with separate redis key if you don't want to use HashMap with `HSET` and `HGET` commands."""

    def __init__(self, key: str, *args: Any, **kwargs: Any) -> None:
        """Initialize the Dict data structure.

        Args:
            key: The key for the dictionary
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(key, *args, **kwargs)
        self.key = key
        self.key_separator = "`"

    @atomic_operation
    @handle_operation_error
    def set(self, key: K, value: V) -> bool:
        """Set a key-value pair in the dictionary.

        Args:
            key: The key to set.
            value: The value to set.

        Returns:
            bool: True if the key-value pair was set successfully, False otherwise.
        """
        key = self.serializer.serialize(key, force_compression=False, decode=True)
        actual_key = f"{self.config.data_structures.prefix}{self.key_separator}{self.key}{self.key_separator}{key}"
        serialized_value = self.serializer.serialize(value)
        return bool(self.connection_manager.execute("set", actual_key, serialized_value))

    @atomic_operation
    @handle_operation_error
    def get(self, key: K) -> V:
        """Get a value from the dictionary.

        Args:
            key: The key to get.

        Returns:
            Any: The value associated with the key.
        """
        key = self.serializer.serialize(key, force_compression=False, decode=True)
        actual_key = f"{self.config.data_structures.prefix}{self.key_separator}{self.key}{self.key_separator}{key}"
        serialized_value = self.connection_manager.execute("get", actual_key)
        return self.serializer.deserialize(serialized_value)  # type: ignore[no-any-return]

    @atomic_operation
    @handle_operation_error
    def delete(self, key: K) -> bool:
        """Delete a key-value pair from the dictionary.

        Args:
            key: The key to delete.

        Returns:
            bool: True if the key-value pair was deleted successfully, False otherwise.
        """
        key = self.serializer.serialize(key, force_compression=False, decode=True)
        actual_key = f"{self.config.data_structures.prefix}{self.key_separator}{self.key}{self.key_separator}{key}"
        return bool(self.connection_manager.execute("delete", actual_key))

    @atomic_operation
    @handle_operation_error
    def keys(self) -> List[K]:
        """Get all keys in the dictionary.

        Returns:
            List[str]: A list of all keys in the dictionary.
        """
        k = [
            key.decode().split(self.key_separator)[-1]
            for key in self.connection_manager.execute(
                "keys",
                f"{self.config.data_structures.prefix}{self.key_separator}{self.key}{self.key_separator}*",
            )
        ]

        return [self.serializer.deserialize(key.encode()) for key in k]

    @atomic_operation
    @handle_operation_error
    def values(self) -> List[V]:
        """Get all values in the dictionary.

        Returns:
            List[T]: A list of all values in the dictionary.
        """
        return [self.get(key) for key in self.keys()]

    @atomic_operation
    @handle_operation_error
    def items(self) -> List[Tuple[K, V]]:
        """Get all key-value pairs in the dictionary.

        Returns:
            List[Tuple[str, T]]: A list of all key-value pairs in the dictionary.
        """
        return [(key.split(self.key_separator)[-1], self.get(key)) for key in self.keys()]  # type: ignore[attr-defined]

    @atomic_operation
    @handle_operation_error
    def clear(self) -> bool:
        """Clear the dictionary."""
        for key in self.keys():
            self.delete(key)
        return True

    @atomic_operation
    @handle_operation_error
    def exists(self, key: K) -> bool:
        """Check if a key exists in the dictionary."""
        key = self.serializer.serialize(key, force_compression=False, decode=True)
        actual_key = f"{self.config.data_structures.prefix}{self.key_separator}{self.key}{self.key_separator}{key}"
        return bool(self.connection_manager.execute("exists", actual_key))

    @atomic_operation
    @handle_operation_error
    def size(self) -> int:
        """Get the number of key-value pairs in the dictionary."""
        return len(self.keys())

    @atomic_operation
    @handle_operation_error
    def __contains__(self, key: K) -> bool:
        """Check if a key exists in the dictionary."""
        return self.exists(key)

    @atomic_operation
    @handle_operation_error
    def __getitem__(self, key: K) -> V:
        """Get a value from the dictionary using the subscript operator.

        Args:
            key: The key to get.

        Returns:
            T: The value associated with the key.

        Raises:
            KeyError: If the key does not exist.
        """
        value = self.get(key)
        if value is None:
            raise KeyError(f"Key {key} does not exist")
        return value

    @atomic_operation
    @handle_operation_error
    def __setitem__(self, key: K, value: V) -> None:
        """Set a value in the dictionary using the subscript operator."""
        self.set(key, value)

    @atomic_operation
    @handle_operation_error
    def __delitem__(self, key: K) -> None:
        """Delete a key-value pair from the dictionary using the subscript operator.

        Args:
            key: The key to delete.

        Raises:
            KeyError: If the key does not exist.
        """
        if not self.exists(key):
            raise KeyError(f"Key {key} does not exist")
        self.delete(key)

    @atomic_operation
    @handle_operation_error
    def __iter__(self) -> Iterator[K]:
        """Iterate over the keys in the dictionary."""
        return iter(self.keys())

    @atomic_operation
    @handle_operation_error
    def __len__(self) -> int:
        """Get the number of key-value pairs in the dictionary."""
        return len(self.keys())

    @atomic_operation
    @handle_operation_error
    def __repr__(self) -> str:
        """Return a string representation of the dictionary."""
        return f"Dict(key={self.key}, items={self.items()})"

    @atomic_operation
    @handle_operation_error
    def __str__(self) -> str:
        """Return a string representation of the dictionary."""
        return str(self.to_dict())

    @atomic_operation
    @handle_operation_error
    def __eq__(self, other: object) -> bool:
        """Check if the dictionary is equal to another dictionary."""
        if not isinstance(other, Dict):
            return False

        return self.to_dict() == other.to_dict()

    @atomic_operation
    @handle_operation_error
    def to_dict(self) -> DictType[K, V]:
        """Return a dictionary representation of the dictionary."""
        return {key: self.get(key) for key in self.keys()}
