import unittest
from unittest.mock import patch

from redis.exceptions import RedisError

from redis_data_structures import Queue


class TestQueue(unittest.TestCase):
    def setUp(self):
        self.queue = Queue(host="localhost", port=6379, db=0)
        self.test_key = "test_queue"
        self.queue.clear(self.test_key)

    def tearDown(self):
        self.queue.clear(self.test_key)

    def test_push_and_pop(self):
        # Test basic push and pop operations
        self.queue.push(self.test_key, "item1")
        self.queue.push(self.test_key, "item2")

        assert self.queue.size(self.test_key) == 2
        assert self.queue.pop(self.test_key) == "item1"
        assert self.queue.pop(self.test_key) == "item2"

    def test_pop_empty_queue(self):
        # Test popping from empty queue
        assert self.queue.pop(self.test_key) is None

    def test_size(self):
        # Test size operations
        assert self.queue.size(self.test_key) == 0

        self.queue.push(self.test_key, "item1")
        assert self.queue.size(self.test_key) == 1

        self.queue.push(self.test_key, "item2")
        assert self.queue.size(self.test_key) == 2

        self.queue.pop(self.test_key)
        assert self.queue.size(self.test_key) == 1

    def test_clear(self):
        # Test clear operation
        self.queue.push(self.test_key, "item1")
        self.queue.push(self.test_key, "item2")

        self.queue.clear(self.test_key)
        assert self.queue.size(self.test_key) == 0

    def test_fifo_order(self):
        # Test FIFO ordering
        items = ["first", "second", "third"]
        for item in items:
            self.queue.push(self.test_key, item)

        for expected_item in items:
            assert self.queue.pop(self.test_key) == expected_item

    def test_peek_operations(self):
        # Test peek operations on empty queue
        assert self.queue.peek(self.test_key) is None

        # Test peek with items
        self.queue.push(self.test_key, "item1")
        self.queue.push(self.test_key, "item2")

        # Peek should return front item without removing it
        assert self.queue.peek(self.test_key) == "item1"
        assert self.queue.size(self.test_key) == 2  # Size should remain unchanged

        # Peek again should return the same item
        assert self.queue.peek(self.test_key) == "item1"
        assert self.queue.size(self.test_key) == 2

        # Pop should remove the item we were peeking at
        assert self.queue.pop(self.test_key) == "item1"
        assert self.queue.peek(self.test_key) == "item2"

    def test_complex_data_types(self):
        # Test with complex data types
        test_dict = {"key": "value", "nested": {"data": True}}
        test_list = [1, 2, [3, 4]]

        self.queue.push(self.test_key, test_dict)
        self.queue.push(self.test_key, test_list)

        assert self.queue.peek(self.test_key) == test_dict
        assert self.queue.pop(self.test_key) == test_dict
        assert self.queue.pop(self.test_key) == test_list

    # Error handling tests
    def test_push_error_handling(self):
        with patch.object(self.queue.redis_client, "rpush", side_effect=RedisError):
            assert not self.queue.push(self.test_key, "data")

    def test_pop_error_handling(self):
        with patch.object(self.queue.redis_client, "lpop", side_effect=RedisError):
            assert self.queue.pop(self.test_key) is None

    def test_peek_error_handling(self):
        with patch.object(self.queue.redis_client, "lindex", side_effect=RedisError):
            assert self.queue.peek(self.test_key) is None

    def test_size_error_handling(self):
        with patch.object(self.queue.redis_client, "llen", side_effect=RedisError):
            assert self.queue.size(self.test_key) == 0

    def test_serialization_edge_cases(self):
        # Test with various data types
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
            self.queue.push(self.test_key, data)
            assert self.queue.peek(self.test_key) == data
            assert self.queue.pop(self.test_key) == data


if __name__ == "__main__":
    unittest.main()
