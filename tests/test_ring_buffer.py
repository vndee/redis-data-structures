import unittest
from unittest.mock import patch

from redis.exceptions import RedisError

from redis_data_structures import RingBuffer


class TestRingBuffer(unittest.TestCase):
    """Test cases for RingBuffer implementation."""

    def setUp(self):
        """Set up test cases."""
        self.buffer = RingBuffer(capacity=3)
        self.test_key = "test_ring_buffer"
        self.buffer.clear(self.test_key)

    def tearDown(self):
        """Clean up after tests."""
        self.buffer.clear(self.test_key)

    def test_push_within_capacity(self):
        """Test pushing items within buffer capacity."""
        self.assertTrue(self.buffer.push(self.test_key, "item1"))
        self.assertTrue(self.buffer.push(self.test_key, "item2"))
        self.assertEqual(self.buffer.size(self.test_key), 2)

        items = self.buffer.get_all(self.test_key)
        self.assertEqual(items, ["item1", "item2"])

    def test_push_beyond_capacity(self):
        """Test pushing items beyond buffer capacity."""
        self.assertTrue(self.buffer.push(self.test_key, "item1"))
        self.assertTrue(self.buffer.push(self.test_key, "item2"))
        self.assertTrue(self.buffer.push(self.test_key, "item3"))
        self.assertTrue(self.buffer.push(self.test_key, "item4"))  # Should overwrite item1

        self.assertEqual(self.buffer.size(self.test_key), 3)
        items = self.buffer.get_all(self.test_key)
        self.assertEqual(items, ["item2", "item3", "item4"])

    def test_get_latest(self):
        """Test getting latest items."""
        # Setup test data
        self.assertTrue(self.buffer.push(self.test_key, "item1"))
        self.assertTrue(self.buffer.push(self.test_key, "item2"))
        self.assertTrue(self.buffer.push(self.test_key, "item3"))

        # Test getting latest item
        latest = self.buffer.get_latest(self.test_key)
        self.assertEqual(latest, ["item3"])

        # Test getting latest 2 items
        latest = self.buffer.get_latest(self.test_key, 2)
        self.assertEqual(latest, ["item3", "item2"])

        # Test getting more items than available
        latest = self.buffer.get_latest(self.test_key, 5)
        self.assertEqual(latest, ["item3", "item2", "item1"])

    def test_clear(self):
        """Test clearing buffer."""
        # Setup test data
        self.assertTrue(self.buffer.push(self.test_key, "item1"))
        self.assertTrue(self.buffer.push(self.test_key, "item2"))

        # Test clearing buffer
        self.assertTrue(self.buffer.clear(self.test_key))
        self.assertEqual(self.buffer.size(self.test_key), 0)
        self.assertEqual(self.buffer.get_all(self.test_key), [])

    def test_complex_data_types(self):
        """Test with different data types."""
        test_data = [
            42,  # integer
            3.14,  # float
            {"key": "value"},  # dict
            ["list", "of", "items"],  # list
            ("tuple", "items"),  # tuple
            {1, 2, 3},  # set
        ]

        for data in test_data:
            self.buffer.clear(self.test_key)
            self.assertTrue(self.buffer.push(self.test_key, data))
            items = self.buffer.get_all(self.test_key)
            self.assertEqual(items, [data])

    def test_concurrent_wrapping(self):
        """Test that buffer correctly wraps around multiple times."""
        for i in range(10):  # Push more items than capacity
            self.assertTrue(self.buffer.push(self.test_key, f"item{i}"))

        # Should only contain the last 3 items
        items = self.buffer.get_all(self.test_key)
        self.assertEqual(len(items), 3)
        self.assertEqual(items, ["item7", "item8", "item9"])

    def test_empty_buffer(self):
        """Test operations on empty buffer."""
        self.assertEqual(self.buffer.size(self.test_key), 0)
        self.assertEqual(self.buffer.get_all(self.test_key), [])
        self.assertEqual(self.buffer.get_latest(self.test_key), [])
        self.assertEqual(self.buffer.get_latest(self.test_key, 5), [])

    # Error handling tests
    def test_push_error_handling(self):
        """Test error handling during push operation."""
        with patch.object(self.buffer.connection_manager, "pipeline", side_effect=RedisError):
            self.assertFalse(self.buffer.push(self.test_key, "data"))

    def test_get_all_error_handling(self):
        """Test error handling during get_all operation."""
        with patch.object(self.buffer.connection_manager, "execute", side_effect=RedisError):
            self.assertEqual(self.buffer.get_all(self.test_key), [])

    def test_get_latest_error_handling(self):
        """Test error handling during get_latest operation."""
        with patch.object(self.buffer.connection_manager, "execute", side_effect=RedisError):
            self.assertEqual(self.buffer.get_latest(self.test_key), [])

    def test_size_error_handling(self):
        """Test error handling during size operation."""
        with patch.object(self.buffer.connection_manager, "execute", side_effect=RedisError):
            self.assertEqual(self.buffer.size(self.test_key), 0)

    def test_clear_error_handling(self):
        """Test error handling during clear operation."""
        with patch.object(self.buffer.connection_manager, "pipeline", side_effect=RedisError):
            self.assertFalse(self.buffer.clear(self.test_key))


if __name__ == "__main__":
    unittest.main()
