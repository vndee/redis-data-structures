import logging
from typing import Any, Iterator, List, Tuple
from typing import Dict as DictType

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


class Dict(RedisDataStructure):
    """A python-like dictionary data structure for Redis with separate redis key if you don't want to use HashMap with `HSET` and `HGET` commands."""  # noqa: E501

    def __init__(self, key: str, *args: Any, **kwargs: Any) -> None:
        """Initialize the Dict data structure.

        Args:
            key: The key for the dictionary
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(key, *args, **kwargs)
        self.key = key

    def set(self, key: str, value: Any) -> bool:
        """Set a key-value pair in the dictionary.

        Args:
            key: The key to set.
            value: The value to set.

        Returns:
            bool: True if the key-value pair was set successfully, False otherwise.
        """
        actual_key = f"{self.config.data_structures.prefix}:{self.key}:{key}"
        serialized_value = self.serializer.serialize(value)
        return bool(self.connection_manager.execute("set", actual_key, serialized_value))

    def get(self, key: str) -> Any:
        """Get a value from the dictionary.

        Args:
            key: The key to get.

        Returns:
            Any: The value associated with the key.
        """
        actual_key = f"{self.config.data_structures.prefix}:{self.key}:{key}"
        serialized_value = self.connection_manager.execute("get", actual_key)
        return self.serializer.deserialize(serialized_value)

    def delete(self, key: str) -> bool:
        """Delete a key-value pair from the dictionary.

        Args:
            key: The key to delete.

        Returns:
            bool: True if the key-value pair was deleted successfully, False otherwise.
        """
        actual_key = f"{self.config.data_structures.prefix}:{self.key}:{key}"
        return bool(self.connection_manager.execute("delete", actual_key))

    def keys(self) -> List[str]:
        """Get all keys in the dictionary.

        Returns:
            List[str]: A list of all keys in the dictionary.
        """
        return [
            key.split(b":")[-1].decode("utf-8")
            for key in self.connection_manager.execute(
                "keys",
                f"{self.config.data_structures.prefix}:{self.key}:*",
            )
        ]

    def values(self) -> List[Any]:
        """Get all values in the dictionary.

        Returns:
            List[Any]: A list of all values in the dictionary.
        """
        return [self.get(key) for key in self.keys()]

    def items(self) -> List[Tuple[str, Any]]:
        """Get all key-value pairs in the dictionary.

        Returns:
            List[Tuple[str, Any]]: A list of all key-value pairs in the dictionary.
        """
        return [(key.split(":")[-1], self.get(key)) for key in self.keys()]

    def clear(self) -> bool:
        """Clear the dictionary."""
        for key in self.keys():
            self.delete(key)
        return True

    def exists(self, key: str) -> bool:
        """Check if a key exists in the dictionary."""
        actual_key = f"{self.config.data_structures.prefix}:{self.key}:{key}"
        return bool(self.connection_manager.execute("exists", actual_key))

    def size(self) -> int:
        """Get the number of key-value pairs in the dictionary."""
        return len(self.keys())

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the dictionary."""
        return self.exists(key)

    def __getitem__(self, key: str) -> Any:
        """Get a value from the dictionary using the subscript operator.

        Args:
            key: The key to get.

        Returns:
            Any: The value associated with the key.

        Raises:
            KeyError: If the key does not exist.
        """
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a value in the dictionary using the subscript operator."""
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        """Delete a key-value pair from the dictionary using the subscript operator.

        Args:
            key: The key to delete.

        Raises:
            KeyError: If the key does not exist.
        """
        if not self.exists(key):
            raise KeyError(key)
        self.delete(key)

    def __iter__(self) -> Iterator[str]:
        """Iterate over the keys in the dictionary."""
        return iter(self.keys())

    def __len__(self) -> int:
        """Get the number of key-value pairs in the dictionary."""
        return len(self.keys())

    def __repr__(self) -> str:
        """Return a string representation of the dictionary."""
        return f"Dict(key={self.key}, items={self.items()})"

    def __str__(self) -> str:
        """Return a string representation of the dictionary."""
        return str(self.to_dict())

    def __eq__(self, other: object) -> bool:
        """Check if the dictionary is equal to another dictionary."""
        if not isinstance(other, Dict):
            return False

        return self.to_dict() == other.to_dict()

    def to_dict(self) -> DictType[str, Any]:
        """Return a dictionary representation of the dictionary."""
        return {key: self.get(key) for key in self.keys()}
