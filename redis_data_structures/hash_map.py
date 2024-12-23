from typing import Any, Dict, List, Optional
import logging

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


class HashMap(RedisDataStructure):
    """A Redis-backed hash map implementation.

    This class implements a hash map data structure using Redis hashes, providing
    key-value storage with type preservation.
    """

    def set(self, key: str, field: str, value: Any) -> bool:
        """Set a field in the hash map.

        Args:
            key (str): The Redis key for this hash map
            field (str): The field name
            value (Any): The value to store

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized = self._serialize(value)
            logger.debug(f"Setting field {field} with serialized value: {serialized}")
            return bool(
                self.connection_manager.execute(
                    "hset",
                    self._get_key(key),
                    field,
                    serialized
                )
            )
        except Exception as e:
            logger.error(f"Error setting hash field: {e}")
            return False

    def get(self, key: str, field: str) -> Optional[Any]:
        """Get a field from the hash map.

        Args:
            key (str): The Redis key for this hash map
            field (str): The field name

        Returns:
            Optional[Any]: The value if successful, None otherwise
        """
        try:
            data = self.connection_manager.execute(
                "hget",
                self._get_key(key),
                field
            )
            if data:
                # Handle bytes response from Redis
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data)
            return None
        except Exception as e:
            logger.error(f"Error getting hash field: {e}")
            return None

    def delete(self, key: str, field: str) -> bool:
        """Delete a field from the hash map.

        Args:
            key (str): The Redis key for this hash map
            field (str): The field name

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return bool(
                self.connection_manager.execute(
                    "hdel",
                    self._get_key(key),
                    field
                )
            )
        except Exception as e:
            logger.error(f"Error deleting hash field: {e}")
            return False

    def exists(self, key: str, field: str) -> bool:
        """Check if a field exists in the hash map.

        Args:
            key (str): The Redis key for this hash map
            field (str): The field name

        Returns:
            bool: True if the field exists, False otherwise
        """
        try:
            return bool(
                self.connection_manager.execute(
                    "hexists",
                    self._get_key(key),
                    field
                )
            )
        except Exception as e:
            logger.error(f"Error checking hash field existence: {e}")
            return False

    def get_all(self, key: str) -> Dict[str, Any]:
        """Get all fields and values from the hash map.

        Args:
            key (str): The Redis key for this hash map

        Returns:
            Dict[str, Any]: Dictionary of field-value pairs
        """
        try:
            data = self.connection_manager.execute(
                "hgetall",
                self._get_key(key)
            )
            if not data:
                return {}

            # Redis returns a flat list of [key1, val1, key2, val2, ...]
            # Convert to dict and deserialize values
            result = {}
            if isinstance(data, list):
                it = iter(data)
                for field in it:
                    value = next(it)
                    if isinstance(field, bytes):
                        field = field.decode("utf-8")
                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    try:
                        logger.debug(f"Raw value for field {field}: {value}")
                        deserialized = self._deserialize(value)
                        logger.debug(f"Deserialized value for field {field}: {deserialized}")
                        result[field] = deserialized
                    except Exception as e:
                        logger.error(f"Error deserializing value for field {field}: {e}")
                        logger.error(f"Raw value was: {value}")
                        result[field] = None
            else:
                # If data is already a dict (some Redis clients return dict)
                for field, value in data.items():
                    try:
                        if isinstance(value, bytes):
                            value = value.decode("utf-8")
                        deserialized = self._deserialize(value)
                        result[field] = deserialized
                    except Exception as e:
                        logger.error(f"Error deserializing value for field {field}: {e}")
                        logger.error(f"Raw value was: {value}")
                        result[field] = None
            return result
        except Exception as e:
            logger.error(f"Error getting all hash fields: {e}")
            return {}

    def get_fields(self, key: str) -> List[str]:
        """Get all fields from the hash map.

        Args:
            key (str): The Redis key for this hash map

        Returns:
            List[str]: List of field names
        """
        try:
            fields = self.connection_manager.execute(
                "hkeys",
                self._get_key(key)
            )
            return [
                field.decode("utf-8") if isinstance(field, bytes) else field
                for field in (fields or [])
            ]
        except Exception as e:
            logger.error(f"Error getting hash fields: {e}")
            return []

    def size(self, key: str) -> int:
        """Get the number of fields in the hash map.

        Args:
            key (str): The Redis key for this hash map

        Returns:
            int: Number of fields
        """
        try:
            return self.connection_manager.execute(
                "hlen",
                self._get_key(key)
            ) or 0
        except Exception as e:
            logger.error(f"Error getting hash size: {e}")
            return 0
