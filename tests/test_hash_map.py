import unittest
from unittest.mock import patch

from redis.exceptions import RedisError

from redis_data_structures import HashMap


class TestHashMap(unittest.TestCase):
    def setUp(self):
        self.hash_map = HashMap(host="localhost", port=6379, db=0)
        self.test_key = "test_hash_map"
        self.hash_map.clear(self.test_key)

    def tearDown(self):
        self.hash_map.clear(self.test_key)

    def test_set_and_get(self):
        # Test basic set and get operations
        self.hash_map.set(self.test_key, "field1", "value1")
        self.hash_map.set(self.test_key, "field2", "value2")

        assert self.hash_map.get(self.test_key, "field1") == "value1"
        assert self.hash_map.get(self.test_key, "field2") == "value2"

    def test_get_nonexistent(self):
        # Test getting non-existent field
        assert self.hash_map.get(self.test_key, "nonexistent") is None

    def test_set_update(self):
        # Test updating existing field
        self.hash_map.set(self.test_key, "field1", "value1")
        self.hash_map.set(self.test_key, "field1", "new_value")

        assert self.hash_map.get(self.test_key, "field1") == "new_value"

    def test_delete(self):
        # Test delete operation
        self.hash_map.set(self.test_key, "field1", "value1")
        assert self.hash_map.delete(self.test_key, "field1")
        assert self.hash_map.get(self.test_key, "field1") is None

    def test_delete_nonexistent(self):
        # Test deleting non-existent field
        assert not self.hash_map.delete(self.test_key, "nonexistent")

    def test_get_all(self):
        # Test getting all fields and values
        test_data = {"field1": "value1", "field2": "value2", "field3": "value3"}

        for field, value in test_data.items():
            self.hash_map.set(self.test_key, field, value)

        assert self.hash_map.get_all(self.test_key) == test_data

    def test_size(self):
        # Test size operations
        assert self.hash_map.size(self.test_key) == 0

        self.hash_map.set(self.test_key, "field1", "value1")
        assert self.hash_map.size(self.test_key) == 1

        self.hash_map.set(self.test_key, "field2", "value2")
        assert self.hash_map.size(self.test_key) == 2

        # Updating existing field should not increase size
        self.hash_map.set(self.test_key, "field1", "new_value")
        assert self.hash_map.size(self.test_key) == 2

    def test_clear(self):
        # Test clear operation
        self.hash_map.set(self.test_key, "field1", "value1")
        self.hash_map.set(self.test_key, "field2", "value2")

        self.hash_map.clear(self.test_key)
        assert self.hash_map.size(self.test_key) == 0
        assert self.hash_map.get_all(self.test_key) == {}

    def test_complex_data_types(self):
        # Test with complex data types
        test_dict = {"key": "value", "nested": {"data": True}}
        test_list = [1, 2, [3, 4]]

        self.hash_map.set(self.test_key, "dict_field", test_dict)
        self.hash_map.set(self.test_key, "list_field", test_list)

        assert self.hash_map.get(self.test_key, "dict_field") == test_dict
        assert self.hash_map.get(self.test_key, "list_field") == test_list

    def test_contains(self):
        # Test contains operation
        assert not self.hash_map.contains(self.test_key, "field1")

        self.hash_map.set(self.test_key, "field1", "value1")
        assert self.hash_map.contains(self.test_key, "field1")

        self.hash_map.delete(self.test_key, "field1")
        assert not self.hash_map.contains(self.test_key, "field1")

    def test_fields_and_values(self):
        # Test fields and values operations
        test_data = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3",
        }

        for field, value in test_data.items():
            self.hash_map.set(self.test_key, field, value)

        fields = self.hash_map.fields(self.test_key)
        values = self.hash_map.values(self.test_key)

        assert set(fields) == set(test_data.keys())
        assert set(values) == set(test_data.values())

    def test_empty_operations(self):
        # Test operations on empty hash map
        assert self.hash_map.get_all(self.test_key) == {}
        assert self.hash_map.fields(self.test_key) == []
        assert self.hash_map.values(self.test_key) == []
        assert self.hash_map.size(self.test_key) == 0

    # Error handling tests
    def test_set_error_handling(self):
        with patch.object(self.hash_map.redis_client, "hset", side_effect=RedisError):
            assert not self.hash_map.set(self.test_key, "field", "value")

    def test_get_error_handling(self):
        with patch.object(self.hash_map.redis_client, "hget", side_effect=RedisError):
            assert self.hash_map.get(self.test_key, "field") is None

    def test_delete_error_handling(self):
        with patch.object(self.hash_map.redis_client, "hdel", side_effect=RedisError):
            assert not self.hash_map.delete(self.test_key, "field")

    def test_contains_error_handling(self):
        with patch.object(self.hash_map.redis_client, "hexists", side_effect=RedisError):
            assert not self.hash_map.contains(self.test_key, "field")

    def test_get_all_error_handling(self):
        with patch.object(self.hash_map.redis_client, "hgetall", side_effect=RedisError):
            assert self.hash_map.get_all(self.test_key) == {}

    def test_fields_error_handling(self):
        with patch.object(self.hash_map.redis_client, "hkeys", side_effect=RedisError):
            assert self.hash_map.fields(self.test_key) == []

    def test_values_error_handling(self):
        with patch.object(self.hash_map.redis_client, "hvals", side_effect=RedisError):
            assert self.hash_map.values(self.test_key) == []

    def test_size_error_handling(self):
        with patch.object(self.hash_map.redis_client, "hlen", side_effect=RedisError):
            assert self.hash_map.size(self.test_key) == 0


if __name__ == "__main__":
    unittest.main()
