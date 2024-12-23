import unittest
from unittest.mock import patch

from redis.exceptions import RedisError

from redis_data_structures import Stack


class TestStack(unittest.TestCase):
    EXPECTED_SIZE_TWO = 2  # Constant for size comparisons

    def setUp(self):
        self.stack = Stack(host="localhost", port=6379, db=0)
        self.test_key = "test_stack"
        self.stack.clear(self.test_key)

    def tearDown(self):
        self.stack.clear(self.test_key)

    def test_push_and_pop(self):
        # Test basic push and pop operations
        self.stack.push(self.test_key, "item1")
        self.stack.push(self.test_key, "item2")

        assert self.stack.size(self.test_key) == self.EXPECTED_SIZE_TWO
        assert self.stack.pop(self.test_key) == "item2"
        assert self.stack.pop(self.test_key) == "item1"

    def test_pop_empty_stack(self):
        # Test popping from empty stack
        assert self.stack.pop(self.test_key) is None

    def test_size(self):
        # Test size operations
        assert self.stack.size(self.test_key) == 0

        self.stack.push(self.test_key, "item1")
        assert self.stack.size(self.test_key) == 1

        self.stack.push(self.test_key, "item2")
        assert self.stack.size(self.test_key) == self.EXPECTED_SIZE_TWO

        self.stack.pop(self.test_key)
        assert self.stack.size(self.test_key) == 1

    def test_clear(self):
        # Test clear operation
        self.stack.push(self.test_key, "item1")
        self.stack.push(self.test_key, "item2")

        self.stack.clear(self.test_key)
        assert self.stack.size(self.test_key) == 0

    def test_lifo_order(self):
        # Test LIFO ordering
        items = ["first", "second", "third"]
        for item in items:
            self.stack.push(self.test_key, item)

        for expected_item in reversed(items):
            assert self.stack.pop(self.test_key) == expected_item

    def test_peek_operations(self):
        # Test peek operations on empty stack
        assert self.stack.peek(self.test_key) is None

        # Test peek with items
        self.stack.push(self.test_key, "item1")
        self.stack.push(self.test_key, "item2")

        # Peek should return top item without removing it
        assert self.stack.peek(self.test_key) == "item2"
        assert (
            self.stack.size(self.test_key) == self.EXPECTED_SIZE_TWO
        )  # Size should remain unchanged

        # Peek again should return the same item
        assert self.stack.peek(self.test_key) == "item2"
        assert self.stack.size(self.test_key) == self.EXPECTED_SIZE_TWO

        # Pop should remove the item we were peeking at
        assert self.stack.pop(self.test_key) == "item2"
        assert self.stack.peek(self.test_key) == "item1"

    def test_complex_data_types(self):
        # Test with complex data types
        test_dict = {"key": "value", "nested": {"data": True}}
        test_list = [1, 2, [3, 4]]

        assert self.stack.push(self.test_key, test_dict)
        assert self.stack.push(self.test_key, test_list)

        assert self.stack.peek(self.test_key) == test_list
        assert self.stack.pop(self.test_key) == test_list
        assert self.stack.pop(self.test_key) == test_dict

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
            assert self.stack.push(self.test_key, data)
            assert self.stack.peek(self.test_key) == data
            assert self.stack.pop(self.test_key) == data

    # Error handling tests
    def test_push_error_handling(self):
        with patch.object(self.stack.redis_client, "lpush", side_effect=RedisError):
            assert not self.stack.push(self.test_key, "data")

    def test_pop_error_handling(self):
        with patch.object(self.stack.redis_client, "lpop", side_effect=RedisError):
            assert self.stack.pop(self.test_key) is None

    def test_peek_error_handling(self):
        with patch.object(self.stack.redis_client, "lindex", side_effect=RedisError):
            assert self.stack.peek(self.test_key) is None

    def test_size_error_handling(self):
        with patch.object(self.stack.redis_client, "llen", side_effect=RedisError):
            assert self.stack.size(self.test_key) == 0


if __name__ == "__main__":
    unittest.main()
