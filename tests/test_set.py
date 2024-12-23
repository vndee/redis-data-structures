import unittest
from unittest.mock import patch
import json

from redis.exceptions import RedisError

from redis_data_structures import Set


class TestSet(unittest.TestCase):
    def setUp(self):
        self.set_ds = Set(host="localhost", port=6379, db=0)
        self.test_key = "test_set"
        self.set_ds.clear(self.test_key)

    def tearDown(self):
        self.set_ds.clear(self.test_key)

    def test_add_and_remove(self):
        # Test basic add and remove operations
        assert self.set_ds.add(self.test_key, "item1")
        assert self.set_ds.add(self.test_key, "item2")

        assert self.set_ds.size(self.test_key) == 2
        assert self.set_ds.remove(self.test_key, "item1")
        assert self.set_ds.size(self.test_key) == 1

    def test_add_duplicate(self):
        # Test adding duplicate items
        assert self.set_ds.add(self.test_key, "item1")
        assert not self.set_ds.add(self.test_key, "item1")
        assert self.set_ds.size(self.test_key) == 1

    def test_remove_nonexistent(self):
        # Test removing non-existent item
        assert not self.set_ds.remove(self.test_key, "nonexistent")

    def test_contains(self):
        # Test contains operation
        self.set_ds.add(self.test_key, "item1")

        assert self.set_ds.contains(self.test_key, "item1")
        assert not self.set_ds.contains(self.test_key, "nonexistent")

    def test_members(self):
        # Test getting all members
        items = {"item1", "item2", "item3"}
        for item in items:
            self.set_ds.add(self.test_key, item)

        # For simple types, we should get a regular set back
        assert self.set_ds.members(self.test_key) == items

    def test_size(self):
        # Test size operations
        assert self.set_ds.size(self.test_key) == 0

        self.set_ds.add(self.test_key, "item1")
        assert self.set_ds.size(self.test_key) == 1

        self.set_ds.add(self.test_key, "item2")
        assert self.set_ds.size(self.test_key) == 2

        # Adding duplicate should not increase size
        self.set_ds.add(self.test_key, "item1")
        assert self.set_ds.size(self.test_key) == 2

    def test_clear(self):
        # Test clear operation
        self.set_ds.add(self.test_key, "item1")
        self.set_ds.add(self.test_key, "item2")

        self.set_ds.clear(self.test_key)
        assert self.set_ds.size(self.test_key) == 0
        assert self.set_ds.members(self.test_key) == set()  # Empty set for empty data

    def test_pop(self):
        # Test pop operation on empty set
        assert self.set_ds.pop(self.test_key) is None

        # Test pop with items
        items = {"item1", "item2", "item3"}
        for item in items:
            self.set_ds.add(self.test_key, item)

        # Pop should remove and return a random item
        popped = self.set_ds.pop(self.test_key)
        assert popped in items
        assert self.set_ds.size(self.test_key) == 2
        assert not self.set_ds.contains(self.test_key, popped)

    def test_complex_data_types(self):
        # Test with string representation of complex data
        test_json1 = json.dumps({"key": "value", "nested": {"data": True}})
        test_json2 = json.dumps([1, 2, [3, 4]])

        assert self.set_ds.add(self.test_key, test_json1)
        assert self.set_ds.add(self.test_key, test_json2)

        assert self.set_ds.contains(self.test_key, test_json1)
        assert self.set_ds.contains(self.test_key, test_json2)
        
        members = self.set_ds.members(self.test_key)
        assert len(members) == 2
        assert test_json1 in members
        assert test_json2 in members

    def test_serialization_edge_cases(self):
        # Test with various hashable data types
        test_cases = [
            None,
            True,
            False,
            42,
            3.14,
            "",
            "Hello",
            "[]",  # JSON string representing a list
            "{}",  # JSON string representing a dict
            '{"nested": {"data": [1, 2, 3]}}'  # Complex JSON string
        ]

        for data in test_cases:
            self.set_ds.clear(self.test_key)  # Clear before each test
            assert self.set_ds.add(self.test_key, data)
            assert self.set_ds.contains(self.test_key, data)
            
            # Get all members and verify our data is in there
            members = self.set_ds.members(self.test_key)
            assert len(members) == 1
            assert data in members
            
            assert self.set_ds.remove(self.test_key, data)

    # Error handling tests
    def test_find_item_error_handling(self):
        with patch.object(self.set_ds.redis_client, "smembers", side_effect=RedisError):
            assert self.set_ds._find_item(self.test_key, "data") is None

    def test_add_error_handling(self):
        with patch.object(self.set_ds.redis_client, "sadd", side_effect=RedisError):
            assert not self.set_ds.add(self.test_key, "data")

    def test_remove_error_handling(self):
        with patch.object(self.set_ds.redis_client, "smembers", side_effect=RedisError):
            assert not self.set_ds.remove(self.test_key, "data")

        # Test error during srem operation
        self.set_ds.add(self.test_key, "data")
        with patch.object(self.set_ds.redis_client, "srem", side_effect=RedisError):
            assert not self.set_ds.remove(self.test_key, "data")

    def test_contains_error_handling(self):
        with patch.object(self.set_ds.redis_client, "smembers", side_effect=RedisError):
            assert not self.set_ds.contains(self.test_key, "data")

    def test_members_error_handling(self):
        with patch.object(self.set_ds.redis_client, "smembers", side_effect=RedisError):
            assert self.set_ds.members(self.test_key) == set()  # Empty set for errors

    def test_size_error_handling(self):
        with patch.object(self.set_ds.redis_client, "scard", side_effect=RedisError):
            assert self.set_ds.size(self.test_key) == 0

    def test_pop_error_handling(self):
        with patch.object(self.set_ds.redis_client, "spop", side_effect=RedisError):
            assert self.set_ds.pop(self.test_key) is None


if __name__ == "__main__":
    unittest.main()
