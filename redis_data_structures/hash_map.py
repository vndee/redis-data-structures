import logging
from typing import Any, Dict, List, Optional

from .base import RedisDataStructure, atomic_operation, handle_operation_error

logger = logging.getLogger(__name__)


class HashMap(RedisDataStructure):
    """A Redis-backed hash map implementation.

    This class implements a hash map data structure using Redis hashes, providing
    key-value storage with type preservation.
    """

    @atomic_operation
    @handle_operation_error
    def set(self, field: str, value: Any) -> bool:
        """Set a field in the hash map.

        Args:
            field (str): The field name
            value (Any): The value to store

        Returns:
            bool: True if successful, False otherwise
        """
        serialized = self.serializer.serialize(value)
        logger.debug(f"Setting field {field} with serialized value: {serialized}")
        return bool(self.connection_manager.execute("hset", self.key, field, serialized))

    @atomic_operation
    @handle_operation_error
    def get(self, field: str) -> Optional[Any]:
        """Get a field from the hash map.

        Args:
            field (str): The field name

        Returns:
            Optional[Any]: The value if successful, None otherwise
        """
        data = self.connection_manager.execute("hget", self.key, field)
        return self.serializer.deserialize(data) if data else None

    @atomic_operation
    @handle_operation_error
    def delete(self, field: str) -> bool:
        """Delete a field from the hash map.

        Args:
            field (str): The field name

        Returns:
            bool: True if successful, False otherwise
        """
        return bool(self.connection_manager.execute("hdel", self.key, field))

    @atomic_operation
    @handle_operation_error
    def exists(self, field: str) -> bool:
        """Check if a field exists in the hash map.

        Args:
            field (str): The field name

        Returns:
            bool: True if the field exists, False otherwise
        """
        return bool(self.connection_manager.execute("hexists", self.key, field))

    @atomic_operation
    @handle_operation_error
    def get_all(self) -> Dict[str, Any]:
        """Get all fields and values from the hash map.

        Returns:
            Dict[str, Any]: Dictionary of field-value pairs
        """
        data = self.connection_manager.execute("hgetall", self.key)
        if not data:
            return {}

        return {k.decode("utf-8"): self.serializer.deserialize(v) for k, v in data.items()}

    @atomic_operation
    @handle_operation_error
    def get_fields(self) -> List[str]:
        """Get all fields from the hash map.

        Returns:
            List[str]: List of field names
        """
        fields = self.connection_manager.execute("hkeys", self.key)
        return [
            field.decode("utf-8") if isinstance(field, bytes) else field for field in (fields or [])
        ]

    @atomic_operation
    @handle_operation_error
    def size(self) -> int:
        """Get the number of fields in the hash map.

        Returns:
            int: Number of fields
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
