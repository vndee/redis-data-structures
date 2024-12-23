from typing import Any, Optional
from typing import Set as PySet
import json

from .base import RedisDataStructure


class Set(RedisDataStructure):
    """A Redis-backed set implementation.

    This class implements a set data structure using Redis sets, ensuring uniqueness
    of elements and providing O(1) add/remove operations. It's perfect for tracking
    unique items like user sessions, maintaining lists of unique identifiers, and
    implementing features that require set operations like unions and intersections.
    """

    def _compare_data(self, data1: Any, data2: Any) -> bool:
        """Compare two data items by their JSON representation.

        Args:
            data1: First data item
            data2: Second data item

        Returns:
            bool: True if the items are equal, False otherwise
        """
        try:
            return json.dumps(data1, sort_keys=True) == json.dumps(data2, sort_keys=True)
        except (TypeError, ValueError):
            # If JSON serialization fails, fall back to direct comparison
            return data1 == data2

    def _find_item(self, key: str, data: Any) -> Optional[str]:
        """Find the serialized item in the set that matches the given data.

        Args:
            key (str): The Redis key for this set
            data (Any): Data to find

        Returns:
            Optional[str]: Serialized item if found, None otherwise
        """
        try:
            items = self.redis_client.smembers(key)
            if not items:
                return None

            for item in items:
                try:
                    # Handle bytes to string conversion if needed
                    if isinstance(item, bytes):
                        item = item.decode('utf-8')
                    # Deserialize the item and extract the data
                    deserialized = self._deserialize(item)["data"]
                    if self._compare_data(deserialized, data):
                        return item
                except (json.JSONDecodeError, TypeError, KeyError) as e:
                    print(f"Error deserializing item: {e}")
                    continue
            return None
        except Exception as e:
            print(f"Error finding item: {e}")
            return None

    def add(self, key: str, data: Any) -> bool:
        """Add an item to the set.

        Args:
            key (str): The Redis key for this set
            data (Any): Data to be stored

        Returns:
            bool: True if the item was added, False if it already existed
        """
        try:
            # First check if the item already exists
            if self.contains(key, data):
                return False

            # If not, add it
            try:
                serialized = self._serialize(data)
                result = self.redis_client.sadd(key, serialized)
                return bool(result)
            except (TypeError, ValueError) as e:
                print(f"Error serializing data: {e}")
                return False
        except Exception as e:
            print(f"Error adding to set: {e}")
            return False

    def remove(self, key: str, data: Any) -> bool:
        """Remove an item from the set.

        Args:
            key (str): The Redis key for this set
            data (Any): Data to be removed

        Returns:
            bool: True if the item was removed, False if it didn't exist
        """
        try:
            # Find the actual serialized item
            found_item = self._find_item(key, data)
            if found_item is None:
                return False

            result = self.redis_client.srem(key, found_item)
            return bool(result)
        except Exception as e:
            print(f"Error removing from set: {e}")
            return False

    def contains(self, key: str, data: Any) -> bool:
        """Check if an item exists in the set.

        Args:
            key (str): The Redis key for this set
            data (Any): Data to check

        Returns:
            bool: True if the item exists, False otherwise
        """
        try:
            items = self.redis_client.smembers(key)
            if not items:
                return False

            for item in items:
                try:
                    # Handle bytes to string conversion if needed
                    if isinstance(item, bytes):
                        item = item.decode('utf-8')
                    # Deserialize the item and extract the data
                    deserialized = self._deserialize(item)["data"]
                    if self._compare_data(deserialized, data):
                        return True
                except (json.JSONDecodeError, TypeError, KeyError) as e:
                    print(f"Error deserializing item: {e}")
                    continue
            return False
        except Exception as e:
            print(f"Error checking set membership: {e}")
            return False

    def members(self, key: str) -> PySet[Any]:
        """Get all members of the set.

        Args:
            key (str): The Redis key for this set

        Returns:
            Set[Any]: Set of all members. Only hashable types are supported.
        """
        try:
            items = self.redis_client.smembers(key)
            if not items:
                return set()

            # Create a set to store deserialized items
            result_set = set()
            for item in items:
                try:
                    # Handle bytes to string conversion if needed
                    if isinstance(item, bytes):
                        item = item.decode('utf-8')
                    # Deserialize the item and extract the data
                    deserialized = self._deserialize(item)["data"]
                    result_set.add(deserialized)
                except (json.JSONDecodeError, TypeError, KeyError) as e:
                    print(f"Error deserializing item: {e}")
                    continue

            return result_set
        except Exception as e:
            print(f"Error getting set members: {e}")
            return set()

    def size(self, key: str) -> int:
        """Get the size of the set.

        Args:
            key (str): The Redis key for this set

        Returns:
            int: Number of elements in the set
        """
        try:
            result = self.redis_client.scard(key)
            return int(result if result is not None else 0)
        except Exception as e:
            print(f"Error getting set size: {e}")
            return 0

    def pop(self, key: str) -> Optional[Any]:
        """Remove and return a random element from the set.

        Args:
            key (str): The Redis key for this set

        Returns:
            Optional[Any]: Random element if successful, None if set is empty
        """
        try:
            data = self.redis_client.spop(key)
            if data is not None:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                return self._deserialize(data)["data"]
            return None
        except Exception as e:
            print(f"Error popping from set: {e}")
            return None
