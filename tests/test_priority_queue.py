import unittest
from unittest.mock import patch

from redis import RedisError

from redis_data_structures import PriorityQueue


class TestPriorityQueue(unittest.TestCase):
    """Test cases for PriorityQueue implementation."""

    def setUp(self):
        """Set up test cases."""
        self.pq = PriorityQueue(host="localhost", port=6379, db=0)
        self.test_key = "test_priority_queue"
        self.pq.clear(self.test_key)

    def tearDown(self):
        """Clean up after tests."""
        self.pq.clear(self.test_key)

    def test_push_and_pop(self):
        """Test basic push and pop operations."""
        # Test basic push and pop operations
        self.assertTrue(self.pq.push(self.test_key, "low_priority", 3))
        self.assertTrue(self.pq.push(self.test_key, "high_priority", 1))

        self.assertEqual(self.pq.size(self.test_key), 2)
        item, priority = self.pq.pop(self.test_key)
        self.assertEqual(item, "high_priority")
        self.assertEqual(priority, 1)

    def test_pop_empty_queue(self):
        """Test popping from empty queue."""
        self.assertIsNone(self.pq.pop(self.test_key))

    def test_size(self):
        """Test size operations."""
        self.assertEqual(self.pq.size(self.test_key), 0)

        self.pq.push(self.test_key, "item1", 1)
        self.assertEqual(self.pq.size(self.test_key), 1)

        self.pq.push(self.test_key, "item2", 2)
        self.assertEqual(self.pq.size(self.test_key), 2)

        self.pq.pop(self.test_key)
        self.assertEqual(self.pq.size(self.test_key), 1)

    def test_clear(self):
        """Test clear operation."""
        self.pq.push(self.test_key, "item1", 1)
        self.pq.push(self.test_key, "item2", 2)

        self.assertTrue(self.pq.clear(self.test_key))
        self.assertEqual(self.pq.size(self.test_key), 0)

    def test_priority_order(self):
        """Test priority ordering (lower number = higher priority)."""
        items = [("lowest", 3), ("highest", 1), ("medium", 2)]

        for item, priority in items:
            self.pq.push(self.test_key, item, priority)

        # Should pop in order: highest (1), medium (2), lowest (3)
        expected_order = ["highest", "medium", "lowest"]
        for expected_item in expected_order:
            item, _ = self.pq.pop(self.test_key)
            self.assertEqual(item, expected_item)

    def test_same_priority(self):
        """Test items with same priority."""
        self.pq.push(self.test_key, "first", 1)
        self.pq.push(self.test_key, "second", 1)

        # Should maintain order for same priority
        item1, _ = self.pq.pop(self.test_key)
        item2, _ = self.pq.pop(self.test_key)
        self.assertEqual(item1, "first")
        self.assertEqual(item2, "second")

    def test_peek_operations(self):
        """Test peek operations."""
        self.assertIsNone(self.pq.peek(self.test_key))

        self.pq.push(self.test_key, "item1", 2)
        self.pq.push(self.test_key, "item2", 1)

        # Peek should return highest priority item without removing it
        item, priority = self.pq.peek(self.test_key)
        self.assertEqual(item, "item2")
        self.assertEqual(priority, 1)
        self.assertEqual(self.pq.size(self.test_key), 2)  # Size should remain unchanged

        # Peek again should return the same item
        item, priority = self.pq.peek(self.test_key)
        self.assertEqual(item, "item2")
        self.assertEqual(priority, 1)

    def test_get_all(self):
        """Test getting all items in priority order."""
        items = [
            ("lowest", 3),
            ("highest", 1),
            ("medium", 2),
            ("also_high", 1)
        ]

        for item, priority in items:
            self.pq.push(self.test_key, item, priority)

        all_items = self.pq.get_all(self.test_key)
        self.assertEqual(len(all_items), 4)
        
        # Check items are in priority order
        priorities = [p for _, p in all_items]
        self.assertEqual(priorities, sorted(priorities))

    def test_complex_data_types(self):
        """Test with complex data types."""
        test_dict = {"key": "value", "nested": {"data": True}}
        test_list = [1, 2, [3, 4]]

        self.pq.push(self.test_key, test_dict, 1)
        self.pq.push(self.test_key, test_list, 2)

        item1, priority1 = self.pq.pop(self.test_key)
        item2, priority2 = self.pq.pop(self.test_key)

        self.assertEqual(item1, test_dict)
        self.assertEqual(priority1, 1)
        self.assertEqual(item2, test_list)
        self.assertEqual(priority2, 2)

    def test_negative_priority(self):
        """Test with negative priority values."""
        self.pq.push(self.test_key, "negative", -1)
        self.pq.push(self.test_key, "positive", 1)
        self.pq.push(self.test_key, "zero", 0)

        # Should pop in order: negative (-1), zero (0), positive (1)
        item1, priority1 = self.pq.pop(self.test_key)
        item2, priority2 = self.pq.pop(self.test_key)
        item3, priority3 = self.pq.pop(self.test_key)

        self.assertEqual(item1, "negative")
        self.assertEqual(priority1, -1)
        self.assertEqual(item2, "zero")
        self.assertEqual(priority2, 0)
        self.assertEqual(item3, "positive")
        self.assertEqual(priority3, 1)

    def test_error_handling(self):
        """Test error handling."""
        # Test Redis error during push
        with patch.object(self.pq.connection_manager, "execute", side_effect=RedisError):
            self.assertFalse(self.pq.push(self.test_key, "data", 1))

        # Test Redis error during pop
        with patch.object(self.pq.connection_manager, "execute", side_effect=RedisError):
            self.assertIsNone(self.pq.pop(self.test_key))

        # Test Redis error during peek
        with patch.object(self.pq.connection_manager, "execute", side_effect=RedisError):
            self.assertIsNone(self.pq.peek(self.test_key))

        # Test Redis error during size
        with patch.object(self.pq.connection_manager, "execute", side_effect=RedisError):
            self.assertEqual(self.pq.size(self.test_key), 0)

        # Test Redis error during clear
        with patch.object(self.pq.connection_manager, "execute", side_effect=RedisError):
            self.assertFalse(self.pq.clear(self.test_key))

        # Test Redis error during get_all
        with patch.object(self.pq.connection_manager, "execute", side_effect=RedisError):
            self.assertEqual(self.pq.get_all(self.test_key), [])


if __name__ == "__main__":
    unittest.main()
