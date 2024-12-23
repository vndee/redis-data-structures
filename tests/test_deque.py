import unittest
from unittest.mock import patch

from redis.exceptions import RedisError

from redis_data_structures import Deque


class TestDeque(unittest.TestCase):
    def setUp(self):
        self.deque = Deque(host="localhost", port=6379, db=0)
        self.test_key = "test_deque"
        self.deque.clear(self.test_key)

    def tearDown(self):
        self.deque.clear(self.test_key)

    def test_push_front_and_pop_front(self):
        # Test push_front and pop_front operations
        self.deque.push_front(self.test_key, "item1")
        self.deque.push_front(self.test_key, "item2")

        assert self.deque.size(self.test_key) == 2
        assert self.deque.pop_front(self.test_key) == "item2"
        assert self.deque.pop_front(self.test_key) == "item1"

    def test_push_back_and_pop_back(self):
        # Test push_back and pop_back operations
        self.deque.push_back(self.test_key, "item1")
        self.deque.push_back(self.test_key, "item2")

        assert self.deque.size(self.test_key) == 2
        assert self.deque.pop_back(self.test_key) == "item2"
        assert self.deque.pop_back(self.test_key) == "item1"

    def test_mixed_operations(self):
        # Test mixing front and back operations
        self.deque.push_front(self.test_key, "front1")
        self.deque.push_back(self.test_key, "back1")
        self.deque.push_front(self.test_key, "front2")
        self.deque.push_back(self.test_key, "back2")

        assert self.deque.size(self.test_key) == 4
        assert self.deque.pop_front(self.test_key) == "front2"
        assert self.deque.pop_back(self.test_key) == "back2"
        assert self.deque.pop_front(self.test_key) == "front1"
        assert self.deque.pop_back(self.test_key) == "back1"

    def test_pop_empty(self):
        # Test popping from empty deque
        assert self.deque.pop_front(self.test_key) is None
        assert self.deque.pop_back(self.test_key) is None

    def test_size(self):
        # Test size operations
        assert self.deque.size(self.test_key) == 0

        self.deque.push_front(self.test_key, "item1")
        assert self.deque.size(self.test_key) == 1

        self.deque.push_back(self.test_key, "item2")
        assert self.deque.size(self.test_key) == 2

        self.deque.pop_front(self.test_key)
        assert self.deque.size(self.test_key) == 1

    def test_clear(self):
        # Test clear operation
        self.deque.push_front(self.test_key, "item1")
        self.deque.push_back(self.test_key, "item2")

        self.deque.clear(self.test_key)
        assert self.deque.size(self.test_key) == 0

    def test_alternating_operations(self):
        # Test alternating push and pop operations
        self.deque.push_front(self.test_key, "item1")
        assert self.deque.pop_back(self.test_key) == "item1"

        self.deque.push_back(self.test_key, "item2")
        assert self.deque.pop_front(self.test_key) == "item2"

    def test_peek_operations(self):
        # Test peek operations
        assert self.deque.peek_front(self.test_key) is None
        assert self.deque.peek_back(self.test_key) is None

        self.deque.push_front(self.test_key, "item1")
        self.deque.push_front(self.test_key, "item2")

        assert self.deque.peek_front(self.test_key) == "item2"
        assert self.deque.peek_back(self.test_key) == "item1"
        assert self.deque.size(self.test_key) == 2  # Verify peeks don't remove items

    def test_complex_data_types(self):
        # Test with complex data types
        test_dict = {"key": "value", "nested": {"data": True}}
        test_list = [1, 2, [3, 4]]

        self.deque.push_front(self.test_key, test_dict)
        self.deque.push_back(self.test_key, test_list)

        assert self.deque.pop_front(self.test_key) == test_dict
        assert self.deque.pop_back(self.test_key) == test_list

    def test_push_front_error_handling(self):
        with patch.object(self.deque.redis_client, "lpush", side_effect=RedisError):
            assert self.deque.push_front(self.test_key, "data") is False

    def test_push_back_error_handling(self):
        with patch.object(self.deque.redis_client, "rpush", side_effect=RedisError):
            assert self.deque.push_back(self.test_key, "data") is False

    def test_pop_front_error_handling(self):
        with patch.object(self.deque.redis_client, "lpop", side_effect=RedisError):
            assert self.deque.pop_front(self.test_key) is None

    def test_pop_back_error_handling(self):
        with patch.object(self.deque.redis_client, "rpop", side_effect=RedisError):
            assert self.deque.pop_back(self.test_key) is None

    def test_peek_front_error_handling(self):
        with patch.object(self.deque.redis_client, "lindex", side_effect=RedisError):
            assert self.deque.peek_front(self.test_key) is None

    def test_peek_back_error_handling(self):
        with patch.object(self.deque.redis_client, "lindex", side_effect=RedisError):
            assert self.deque.peek_back(self.test_key) is None

    def test_size_error_handling(self):
        with patch.object(self.deque.redis_client, "llen", side_effect=RedisError):
            assert self.deque.size(self.test_key) == 0


if __name__ == "__main__":
    unittest.main()
