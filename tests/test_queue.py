import unittest
from unittest.mock import patch

from redis.exceptions import RedisError

from redis_data_structures import Queue


class TestQueue(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()
        self.test_key = "test_queue"
        self.queue.clear(self.test_key)

    def tearDown(self):
        self.queue.clear(self.test_key)

    def test_push_and_pop(self):
        """Test basic push and pop operations."""
        self.assertTrue(self.queue.push(self.test_key, "item1"))
        self.assertTrue(self.queue.push(self.test_key, "item2"))

        self.assertEqual(self.queue.size(self.test_key), 2)
        self.assertEqual(self.queue.pop(self.test_key), "item1")
        self.assertEqual(self.queue.pop(self.test_key), "item2")

    def test_pop_empty_queue(self):
        """Test popping from empty queue."""
        self.assertIsNone(self.queue.pop(self.test_key))

    def test_size(self):
        """Test size operations."""
        self.assertEqual(self.queue.size(self.test_key), 0)

        self.assertTrue(self.queue.push(self.test_key, "item1"))
        self.assertEqual(self.queue.size(self.test_key), 1)

        self.assertTrue(self.queue.push(self.test_key, "item2"))
        self.assertEqual(self.queue.size(self.test_key), 2)

        self.queue.pop(self.test_key)
        self.assertEqual(self.queue.size(self.test_key), 1)

    def test_clear(self):
        """Test clear operation."""
        self.assertTrue(self.queue.push(self.test_key, "item1"))
        self.assertTrue(self.queue.push(self.test_key, "item2"))

        self.assertTrue(self.queue.clear(self.test_key))
        self.assertEqual(self.queue.size(self.test_key), 0)

    def test_fifo_order(self):
        """Test FIFO ordering."""
        items = ["first", "second", "third"]
        for item in items:
            self.assertTrue(self.queue.push(self.test_key, item))

        for expected_item in items:
            self.assertEqual(self.queue.pop(self.test_key), expected_item)

    def test_peek_operations(self):
        """Test peek operations."""
        # Test peek on empty queue
        self.assertIsNone(self.queue.peek(self.test_key))

        # Test peek with items
        self.assertTrue(self.queue.push(self.test_key, "item1"))
        self.assertTrue(self.queue.push(self.test_key, "item2"))

        # Peek should return front item without removing it
        self.assertEqual(self.queue.peek(self.test_key), "item1")
        self.assertEqual(self.queue.size(self.test_key), 2)  # Size should remain unchanged

        # Peek again should return the same item
        self.assertEqual(self.queue.peek(self.test_key), "item1")
        self.assertEqual(self.queue.size(self.test_key), 2)

        # Pop should remove the item we were peeking at
        self.assertEqual(self.queue.pop(self.test_key), "item1")
        self.assertEqual(self.queue.peek(self.test_key), "item2")

    def test_complex_data_types(self):
        """Test with complex data types."""
        test_dict = {"key": "value", "nested": {"data": True}}
        test_list = [1, 2, [3, 4]]

        self.assertTrue(self.queue.push(self.test_key, test_dict))
        self.assertTrue(self.queue.push(self.test_key, test_list))

        self.assertEqual(self.queue.peek(self.test_key), test_dict)
        self.assertEqual(self.queue.pop(self.test_key), test_dict)
        self.assertEqual(self.queue.pop(self.test_key), test_list)

    def test_serialization_edge_cases(self):
        """Test with various data types."""
        test_cases = [
            None,
            True,
            False,
            42,
            3.14,
            "",
            "Hello",
            [],
            [1, 2, 3],
            {},
            {"a": 1, "b": 2},
            {"nested": {"data": [1, 2, 3]}},
        ]

        for data in test_cases:
            self.assertTrue(self.queue.push(self.test_key, data))
            self.assertEqual(self.queue.peek(self.test_key), data)
            self.assertEqual(self.queue.pop(self.test_key), data)

    # Error handling tests
    def test_push_error_handling(self):
        """Test error handling during push operation."""
        with patch.object(self.queue.connection_manager, "execute", side_effect=RedisError):
            self.assertFalse(self.queue.push(self.test_key, "data"))

    def test_pop_error_handling(self):
        """Test error handling during pop operation."""
        with patch.object(self.queue.connection_manager, "execute", side_effect=RedisError):
            self.assertIsNone(self.queue.pop(self.test_key))

    def test_peek_error_handling(self):
        """Test error handling during peek operation."""
        with patch.object(self.queue.connection_manager, "execute", side_effect=RedisError):
            self.assertIsNone(self.queue.peek(self.test_key))

    def test_size_error_handling(self):
        """Test error handling during size operation."""
        with patch.object(self.queue.connection_manager, "execute", side_effect=RedisError):
            self.assertEqual(self.queue.size(self.test_key), 0)

    def test_clear_error_handling(self):
        """Test error handling during clear operation."""
        with patch.object(self.queue.connection_manager, "execute", side_effect=RedisError):
            self.assertFalse(self.queue.clear(self.test_key))


if __name__ == "__main__":
    unittest.main()
