import unittest
from unittest.mock import patch

from redis.exceptions import RedisError

from redis_data_structures import RingBuffer


class TestRingBuffer(unittest.TestCase):
    def setUp(self):
        self.buffer = RingBuffer(capacity=3, host="localhost", port=6379, db=0)
        self.test_key = "test_ring_buffer"
        self.buffer.clear(self.test_key)

    def tearDown(self):
        self.buffer.clear(self.test_key)

    def test_push_within_capacity(self):
        # Test pushing items within buffer capacity
        assert self.buffer.push(self.test_key, "item1")
        assert self.buffer.push(self.test_key, "item2")
        assert self.buffer.size(self.test_key) == 2
        
        items = self.buffer.get_all(self.test_key)
        assert items == ["item1", "item2"]

    def test_push_beyond_capacity(self):
        # Test pushing items beyond buffer capacity
        self.buffer.push(self.test_key, "item1")
        self.buffer.push(self.test_key, "item2")
        self.buffer.push(self.test_key, "item3")
        self.buffer.push(self.test_key, "item4")  # Should overwrite item1

        assert self.buffer.size(self.test_key) == 3
        items = self.buffer.get_all(self.test_key)
        assert items == ["item2", "item3", "item4"]

    def test_get_latest(self):
        # Setup test data
        self.buffer.push(self.test_key, "item1")
        self.buffer.push(self.test_key, "item2")
        self.buffer.push(self.test_key, "item3")

        # Test getting latest item
        latest = self.buffer.get_latest(self.test_key)
        assert latest == ["item3"]

        # Test getting latest 2 items
        latest = self.buffer.get_latest(self.test_key, 2)
        assert latest == ["item3", "item2"]

        # Test getting more items than available
        latest = self.buffer.get_latest(self.test_key, 5)
        assert latest == ["item3", "item2", "item1"]

    def test_clear(self):
        # Setup test data
        self.buffer.push(self.test_key, "item1")
        self.buffer.push(self.test_key, "item2")
        
        # Test clearing buffer
        assert self.buffer.clear(self.test_key)
        assert self.buffer.size(self.test_key) == 0
        assert self.buffer.get_all(self.test_key) == []

    def test_complex_data_types(self):
        # Test with different data types
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
            assert self.buffer.push(self.test_key, data)
            items = self.buffer.get_all(self.test_key)
            assert items == [data]

    def test_error_handling(self):
        # Test push error handling
        with patch.object(self.buffer.redis_client, "pipeline", side_effect=RedisError):
            assert not self.buffer.push(self.test_key, "item")

        # Test get_all error handling
        with patch.object(self.buffer.redis_client, "lrange", side_effect=RedisError):
            assert self.buffer.get_all(self.test_key) == []

        # Test get_latest error handling
        with patch.object(self.buffer.redis_client, "lrange", side_effect=RedisError):
            assert self.buffer.get_latest(self.test_key) == []

        # Test clear error handling
        with patch.object(self.buffer.redis_client, "pipeline", side_effect=RedisError):
            assert not self.buffer.clear(self.test_key)

        # Test size error handling
        with patch.object(self.buffer.redis_client, "llen", side_effect=RedisError):
            assert self.buffer.size(self.test_key) == 0

    def test_concurrent_wrapping(self):
        # Test that buffer correctly wraps around multiple times
        for i in range(10):  # Push more items than capacity
            self.buffer.push(self.test_key, f"item{i}")

        # Should only contain the last 3 items
        items = self.buffer.get_all(self.test_key)
        assert len(items) == 3
        assert items == ["item7", "item8", "item9"]

    def test_empty_buffer(self):
        # Test operations on empty buffer
        assert self.buffer.size(self.test_key) == 0
        assert self.buffer.get_all(self.test_key) == []
        assert self.buffer.get_latest(self.test_key) == []
        assert self.buffer.get_latest(self.test_key, 5) == []


if __name__ == "__main__":
    unittest.main() 