import unittest
from unittest.mock import patch

from redis.exceptions import RedisError

from redis_data_structures import PriorityQueue


class TestPriorityQueue(unittest.TestCase):
    def setUp(self):
        self.pq = PriorityQueue(host="localhost", port=6379, db=0)
        self.test_key = "test_priority_queue"
        self.pq.clear(self.test_key)

    def tearDown(self):
        self.pq.clear(self.test_key)

    def test_push_and_pop(self):
        # Test basic push and pop operations
        self.pq.push(self.test_key, "low_priority", 3)
        self.pq.push(self.test_key, "high_priority", 1)

        assert self.pq.size(self.test_key) == 2
        item, priority = self.pq.pop(self.test_key)
        assert item == "high_priority"
        assert priority == 1

    def test_pop_empty_queue(self):
        # Test popping from empty queue
        assert self.pq.pop(self.test_key) is None

    def test_size(self):
        # Test size operations
        assert self.pq.size(self.test_key) == 0

        self.pq.push(self.test_key, "item1", 1)
        assert self.pq.size(self.test_key) == 1

        self.pq.push(self.test_key, "item2", 2)
        assert self.pq.size(self.test_key) == 2

        self.pq.pop(self.test_key)
        assert self.pq.size(self.test_key) == 1

    def test_clear(self):
        # Test clear operation
        self.pq.push(self.test_key, "item1", 1)
        self.pq.push(self.test_key, "item2", 2)

        self.pq.clear(self.test_key)
        assert self.pq.size(self.test_key) == 0

    def test_priority_order(self):
        # Test priority ordering (lower number = higher priority)
        items = [("lowest", 3), ("highest", 1), ("medium", 2)]

        for item, priority in items:
            self.pq.push(self.test_key, item, priority)

        # Should pop in order: highest (1), medium (2), lowest (3)
        expected_order = ["highest", "medium", "lowest"]
        for expected_item in expected_order:
            item, _ = self.pq.pop(self.test_key)
            assert item == expected_item

    def test_same_priority(self):
        # Test items with same priority
        self.pq.push(self.test_key, "first", 1)
        self.pq.push(self.test_key, "second", 1)

        # Should maintain order for same priority
        item1, _ = self.pq.pop(self.test_key)
        item2, _ = self.pq.pop(self.test_key)
        assert item1 == "first"
        assert item2 == "second"

    def test_peek_operations(self):
        # Test peek operations
        assert self.pq.peek(self.test_key) is None

        self.pq.push(self.test_key, "item1", 2)
        self.pq.push(self.test_key, "item2", 1)

        # Peek should return highest priority item without removing it
        item, priority = self.pq.peek(self.test_key)
        assert item == "item2"
        assert priority == 1
        assert self.pq.size(self.test_key) == 2  # Size should remain unchanged

        # Peek again should return the same item
        item, priority = self.pq.peek(self.test_key)
        assert item == "item2"
        assert priority == 1

    def test_complex_data_types(self):
        # Test with complex data types
        test_dict = {"key": "value", "nested": {"data": True}}
        test_list = [1, 2, [3, 4]]

        self.pq.push(self.test_key, test_dict, 1)
        self.pq.push(self.test_key, test_list, 2)

        item1, priority1 = self.pq.pop(self.test_key)
        item2, priority2 = self.pq.pop(self.test_key)

        assert item1 == test_dict
        assert priority1 == 1
        assert item2 == test_list
        assert priority2 == 2

    def test_negative_priority(self):
        # Test with negative priority values
        self.pq.push(self.test_key, "negative", -1)
        self.pq.push(self.test_key, "positive", 1)
        self.pq.push(self.test_key, "zero", 0)

        # Should pop in order: negative (-1), zero (0), positive (1)
        item1, priority1 = self.pq.pop(self.test_key)
        item2, priority2 = self.pq.pop(self.test_key)
        item3, priority3 = self.pq.pop(self.test_key)

        assert item1 == "negative" and priority1 == -1
        assert item2 == "zero" and priority2 == 0
        assert item3 == "positive" and priority3 == 1

    # Error handling tests
    def test_push_error_handling(self):
        with patch.object(self.pq.redis_client, "zadd", side_effect=RedisError):
            assert not self.pq.push(self.test_key, "data", 1)

    def test_pop_error_handling(self):
        with patch.object(self.pq.redis_client, "zrange", side_effect=RedisError):
            assert self.pq.pop(self.test_key) is None

        # Test error during zrem operation
        self.pq.push(self.test_key, "data", 1)
        with patch.object(self.pq.redis_client, "zrem", side_effect=RedisError):
            assert self.pq.pop(self.test_key) is None

    def test_peek_error_handling(self):
        with patch.object(self.pq.redis_client, "zrange", side_effect=RedisError):
            assert self.pq.peek(self.test_key) is None

    def test_size_error_handling(self):
        with patch.object(self.pq.redis_client, "zcard", side_effect=RedisError):
            assert self.pq.size(self.test_key) == 0


if __name__ == "__main__":
    unittest.main()
