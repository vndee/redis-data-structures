import logging
from typing import Any, Dict, List, Optional

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


class HashMap(RedisDataStructure):
    """A Redis-backed hash map implementation.

    This class implements a hash map data structure using Redis hashes, providing
    key-value storage with type preservation.
    """

    def set(self, field: str, value: Any) -> bool:
        """Set a field in the hash map.

        Args:
            field (str): The field name
            value (Any): The value to store

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized = self.serializer.serialize(value)
            logger.debug(f"Setting field {field} with serialized value: {serialized}")
            return bool(self.connection_manager.execute("hset", self.key, field, serialized))
        except Exception:
            logger.exception("Error setting hash field")
            return False

    def get(self, field: str) -> Optional[Any]:
        """Get a field from the hash map.

        Args:
            field (str): The field name

        Returns:
            Optional[Any]: The value if successful, None otherwise
        """
        try:
            data = self.connection_manager.execute("hget", self.key, field)
            return self.serializer.deserialize(data) if data else None
        except Exception:
            logger.exception("Error getting hash field")
            return None

    def delete(self, field: str) -> bool:
        """Delete a field from the hash map.

        Args:
            field (str): The field name

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return bool(self.connection_manager.execute("hdel", self.key, field))
        except Exception:
            logger.exception("Error deleting hash field")
            return False

    def exists(self, field: str) -> bool:
        """Check if a field exists in the hash map.

        Args:
            field (str): The field name

        Returns:
            bool: True if the field exists, False otherwise
        """
        try:
            return bool(self.connection_manager.execute("hexists", self.key, field))
        except Exception:
            logger.exception("Error checking hash field existence")
            return False

    def get_all(self) -> Dict[str, Any]:
        """Get all fields and values from the hash map.

        Returns:
            Dict[str, Any]: Dictionary of field-value pairs
        """
        data = self.connection_manager.execute("hgetall", self.key)
        if not data:
            return {}

        return {k.decode("utf-8"): self.serializer.deserialize(v) for k, v in data.items()}

    def get_fields(self) -> List[str]:
        """Get all fields from the hash map.

        Returns:
            List[str]: List of field names
        """
        try:
            fields = self.connection_manager.execute("hkeys", self.key)
            return [
                field.decode("utf-8") if isinstance(field, bytes) else field
                for field in (fields or [])
            ]
        except Exception:
            logger.exception("Error getting hash fields")
            return []

    def size(self) -> int:
        """Get the number of fields in the hash map.

        Returns:
            int: Number of fields
        """
        try:
            return self.connection_manager.execute("hlen", self.key) or 0
        except Exception:
            logger.exception("Error getting hash size")
            return 0

    def clear(self) -> bool:
        """Clear all fields from the hash map.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.connection_manager.execute("delete", self.key)
            return True
        except Exception:
            logger.exception("Error clearing hash")
            return False
