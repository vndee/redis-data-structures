from typing import Any, Dict, List, Optional

from .base import RedisDataStructure


class HashMap(RedisDataStructure):
    """A Redis-backed hash map implementation.

    This class implements a hash map using Redis hashes, providing field-based
    key-value storage with O(1) access time. It's ideal for storing structured data
    like user profiles, configuration settings, and any scenario requiring fast
    field-based access to data with support for complex data types through JSON
    serialization.
    """

    def set(self, key: str, field: str, value: Any) -> bool:
        """Set a field-value pair in the hash map.

        Args:
            key (str): The Redis key for this hash map
            field (str): Field name
            value (Any): Value to be stored

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized = self._serialize(value)
            result = self.redis_client.hset(key, field, serialized)
            return bool(result)
        except Exception as e:
            print(f"Error setting hash field: {e}")
            return False

    def get(self, key: str, field: str) -> Optional[Any]:
        """Get the value of a field from the hash map.

        Args:
            key (str): The Redis key for this hash map
            field (str): Field name

        Returns:
            Optional[Any]: Value if field exists, None otherwise
        """
        try:
            data = self.redis_client.hget(key, field)
            if data is not None:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data)
            return None
        except Exception as e:
            print(f"Error getting hash field: {e}")
            return None

    def delete(self, key: str, field: str) -> bool:
        """Delete a field from the hash map.

        Args:
            key (str): The Redis key for this hash map
            field (str): Field to delete

        Returns:
            bool: True if field was deleted, False if it didn't exist
        """
        try:
            result = self.redis_client.hdel(key, field)
            return bool(result)
        except Exception as e:
            print(f"Error deleting hash field: {e}")
            return False

    def contains(self, key: str, field: str) -> bool:
        """Check if a field exists in the hash map.

        Args:
            key (str): The Redis key for this hash map
            field (str): Field to check

        Returns:
            bool: True if field exists, False otherwise
        """
        try:
            result = self.redis_client.hexists(key, field)
            return bool(result)
        except Exception as e:
            print(f"Error checking hash field existence: {e}")
            return False

    def get_all(self, key: str) -> Dict[str, Any]:
        """Get all field-value pairs from the hash map.

        Args:
            key (str): The Redis key for this hash map

        Returns:
            Dict[str, Any]: Dictionary of all field-value pairs
        """
        try:
            items = self.redis_client.hgetall(key)
            if not items:
                return {}

            result = {}
            for field, value in items.items():
                field_str = field.decode("utf-8") if isinstance(field, bytes) else field
                value_str = value.decode("utf-8") if isinstance(value, bytes) else value
                result[field_str] = self._deserialize(value_str)
            return result
        except Exception as e:
            print(f"Error getting all hash fields: {e}")
            return {}

    def fields(self, key: str) -> List[str]:
        """Get all fields from the hash map.

        Args:
            key (str): The Redis key for this hash map

        Returns:
            List[str]: List of all fields
        """
        try:
            fields = self.redis_client.hkeys(key)
            if isinstance(fields, list):
                return [
                    field.decode("utf-8") if isinstance(field, bytes) else field for field in fields
                ]
            return []
        except Exception as e:
            print(f"Error getting hash fields: {e}")
            return []

    def values(self, key: str) -> List[Any]:
        """Get all values from the hash map.

        Args:
            key (str): The Redis key for this hash map

        Returns:
            List[Any]: List of all values
        """
        try:
            values = self.redis_client.hvals(key)
            if isinstance(values, list):
                return [
                    self._deserialize(value.decode("utf-8") if isinstance(value, bytes) else value)
                    for value in values
                ]
            return []
        except Exception as e:
            print(f"Error getting hash values: {e}")
            return []

    def size(self, key: str) -> int:
        """Get the number of fields in the hash map.

        Args:
            key (str): The Redis key for this hash map

        Returns:
            int: Number of fields
        """
        try:
            result = self.redis_client.hlen(key)
            return int(result)
        except Exception as e:
            print(f"Error getting hash size: {e}")
            return 0
