import time
import unittest
from unittest.mock import patch

from redis import RedisError

from redis_data_structures import LRUCache


class TestLRUCache(unittest.TestCase):
    """Test cases for LRUCache implementation."""

    def setUp(self):
        """Set up test cases."""
        self.cache = LRUCache(capacity=3, host="localhost", port=6379, db=0)
        self.test_key = "test_lru_cache"
        self.cache.clear(self.test_key)

    def tearDown(self):
        """Clean up after tests."""
        self.cache.clear(self.test_key)

    def test_put_and_get(self):
        """Test basic put and get operations."""
        # Test putting and getting single item
        self.assertTrue(self.cache.put(self.test_key, "key1", "value1"))
        self.assertEqual(self.cache.get(self.test_key, "key1"), "value1")

        # Test getting non-existent item
        self.assertIsNone(self.cache.get(self.test_key, "nonexistent"))

    def test_capacity_limit(self):
        """Test that cache respects capacity limit."""
        # Fill cache to capacity
        self.cache.put(self.test_key, "key1", "value1")
        self.cache.put(self.test_key, "key2", "value2")
        self.cache.put(self.test_key, "key3", "value3")

        # Verify size
        self.assertEqual(self.cache.size(self.test_key), 3)

        # Add one more item, should evict least recently used
        self.cache.put(self.test_key, "key4", "value4")
        self.assertEqual(self.cache.size(self.test_key), 3)
        self.assertIsNone(self.cache.get(self.test_key, "key1"))  # Should be evicted
        self.assertEqual(self.cache.get(self.test_key, "key4"), "value4")

    def test_lru_eviction_order(self):
        """Test that items are evicted in LRU order."""
        # Add items
        self.cache.put(self.test_key, "key1", "value1")
        self.cache.put(self.test_key, "key2", "value2")
        self.cache.put(self.test_key, "key3", "value3")

        # Access key1, making key2 the least recently used
        self.cache.get(self.test_key, "key1")
        time.sleep(0.1)  # Ensure different timestamps
        self.cache.get(self.test_key, "key3")

        # Add new item, should evict key2
        self.cache.put(self.test_key, "key4", "value4")
        self.assertIsNone(self.cache.get(self.test_key, "key2"))  # Should be evicted
        self.assertEqual(self.cache.get(self.test_key, "key1"), "value1")
        self.assertEqual(self.cache.get(self.test_key, "key3"), "value3")
        self.assertEqual(self.cache.get(self.test_key, "key4"), "value4")

    def test_peek(self):
        """Test peeking at values without updating access time."""
        # Add items
        self.cache.put(self.test_key, "key1", "value1")
        self.cache.put(self.test_key, "key2", "value2")

        # Peek at key1 (shouldn't update access time)
        self.assertEqual(self.cache.peek(self.test_key, "key1"), "value1")

        # Add item to full cache
        self.cache.put(self.test_key, "key3", "value3")
        self.cache.put(self.test_key, "key4", "value4")

        # key1 should be evicted since peek didn't update its access time
        self.assertIsNone(self.cache.get(self.test_key, "key1"))

    def test_remove(self):
        """Test removing items from cache."""
        # Add items
        self.cache.put(self.test_key, "key1", "value1")
        self.cache.put(self.test_key, "key2", "value2")

        # Remove item
        self.assertTrue(self.cache.remove(self.test_key, "key1"))
        self.assertIsNone(self.cache.get(self.test_key, "key1"))
        self.assertEqual(self.cache.size(self.test_key), 1)

        # Try removing non-existent item
        self.assertFalse(self.cache.remove(self.test_key, "nonexistent"))

    def test_clear(self):
        """Test clearing the cache."""
        # Add items
        self.cache.put(self.test_key, "key1", "value1")
        self.cache.put(self.test_key, "key2", "value2")

        # Clear cache
        self.assertTrue(self.cache.clear(self.test_key))
        self.assertEqual(self.cache.size(self.test_key), 0)
        self.assertIsNone(self.cache.get(self.test_key, "key1"))
        self.assertIsNone(self.cache.get(self.test_key, "key2"))

    def test_get_all(self):
        """Test getting all items from cache."""
        # Add items
        items = {"key1": "value1", "key2": "value2", "key3": "value3"}
        for key, value in items.items():
            self.cache.put(self.test_key, key, value)

        # Get all items
        cached_items = self.cache.get_all(self.test_key)
        self.assertEqual(cached_items, items)

    def test_get_lru_order(self):
        """Test getting items in LRU order."""
        # Add items
        self.cache.put(self.test_key, "key1", "value1")
        time.sleep(0.1)  # Ensure different timestamps
        self.cache.put(self.test_key, "key2", "value2")
        time.sleep(0.1)
        self.cache.put(self.test_key, "key3", "value3")

        # Access items in specific order
        time.sleep(0.1)
        self.cache.get(self.test_key, "key1")  # Make key1 most recently used
        time.sleep(0.1)
        self.cache.get(self.test_key, "key2")  # Make key2 most recently used

        # Get LRU order
        order = self.cache.get_lru_order(self.test_key)
        self.assertEqual(order[0], "key3")  # Least recently used
        self.assertEqual(order[-1], "key2")  # Most recently used

    def test_complex_data_types(self):
        """Test cache with complex data types."""
        # Test with dictionary
        dict_value = {"name": "John", "age": 30}
        self.cache.put(self.test_key, "dict", dict_value)
        self.assertEqual(self.cache.get(self.test_key, "dict"), dict_value)

        # Test with list
        list_value = [1, 2, [3, 4]]
        self.cache.put(self.test_key, "list", list_value)
        self.assertEqual(self.cache.get(self.test_key, "list"), list_value)

        # Test with tuple
        tuple_value = (1, "two", [3])
        self.cache.put(self.test_key, "tuple", tuple_value)
        self.assertEqual(self.cache.get(self.test_key, "tuple"), tuple_value)

    def test_error_handling(self):
        """Test error handling."""
        # Test Redis error during put
        with patch.object(self.cache.redis_client, "pipeline", side_effect=RedisError):
            self.assertFalse(self.cache.put(self.test_key, "key", "value"))

        # Test Redis error during get
        with patch.object(self.cache.redis_client, "hget", side_effect=RedisError):
            self.assertIsNone(self.cache.get(self.test_key, "key"))

        # Test Redis error during remove
        with patch.object(self.cache.redis_client, "pipeline", side_effect=RedisError):
            self.assertFalse(self.cache.remove(self.test_key, "key"))

        # Test Redis error during clear
        with patch.object(self.cache.redis_client, "pipeline", side_effect=RedisError):
            self.assertFalse(self.cache.clear(self.test_key))

    def test_update_existing(self):
        """Test updating existing cache entries."""
        # Add initial value
        self.cache.put(self.test_key, "key1", "value1")

        # Update with new value
        self.cache.put(self.test_key, "key1", "new_value")
        self.assertEqual(self.cache.get(self.test_key, "key1"), "new_value")
        self.assertEqual(self.cache.size(self.test_key), 1)  # Size should remain same

    def test_minimum_capacity(self):
        """Test that cache capacity cannot be less than 1."""
        cache = LRUCache(capacity=0)  # Should be set to 1
        self.assertEqual(cache.capacity, 1)

        cache = LRUCache(capacity=-5)  # Should be set to 1
        self.assertEqual(cache.capacity, 1)


if __name__ == "__main__":
    unittest.main()
