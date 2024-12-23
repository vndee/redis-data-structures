import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from redis.exceptions import RedisError

from redis_data_structures import HashMap


class TestHashMap(unittest.TestCase):
    def setUp(self):
        self.hash_map = HashMap()
        self.test_key = "test_hash_map"
        self.hash_map.clear(self.test_key)

    def tearDown(self):
        self.hash_map.clear(self.test_key)
        self.hash_map.close()

    def test_set_and_get(self):
        # Test basic set and get operations
        self.hash_map.set(self.test_key, "field1", "value1")
        self.hash_map.set(self.test_key, "field2", "value2")

        self.assertEqual(self.hash_map.get(self.test_key, "field1"), "value1")
        self.assertEqual(self.hash_map.get(self.test_key, "field2"), "value2")

    def test_get_nonexistent(self):
        # Test getting non-existent field
        self.assertIsNone(self.hash_map.get(self.test_key, "nonexistent"))

    def test_set_update(self):
        # Test updating existing field
        self.hash_map.set(self.test_key, "field1", "value1")
        self.hash_map.set(self.test_key, "field1", "new_value")

        self.assertEqual(self.hash_map.get(self.test_key, "field1"), "new_value")

    def test_delete(self):
        # Test delete operation
        self.hash_map.set(self.test_key, "field1", "value1")
        self.assertTrue(self.hash_map.delete(self.test_key, "field1"))
        self.assertIsNone(self.hash_map.get(self.test_key, "field1"))

    def test_delete_nonexistent(self):
        # Test deleting non-existent field
        self.assertFalse(self.hash_map.delete(self.test_key, "nonexistent"))

    def test_get_all(self):
        # Test getting all fields and values
        test_data = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }

        # Set each field with proper serialization
        for field, value in test_data.items():
            self.hash_map.set(self.test_key, field, value)

        # Get all fields and compare with original data
        result = self.hash_map.get_all(self.test_key)
        self.assertEqual(result, test_data)

    def test_size(self):
        # Test size operations
        self.assertEqual(self.hash_map.size(self.test_key), 0)

        self.hash_map.set(self.test_key, "field1", "value1")
        self.assertEqual(self.hash_map.size(self.test_key), 1)

        self.hash_map.set(self.test_key, "field2", "value2")
        self.assertEqual(self.hash_map.size(self.test_key), 2)

        # Updating existing field should not increase size
        self.hash_map.set(self.test_key, "field1", "new_value")
        self.assertEqual(self.hash_map.size(self.test_key), 2)

    def test_clear(self):
        # Test clear operation
        self.hash_map.set(self.test_key, "field1", "value1")
        self.hash_map.set(self.test_key, "field2", "value2")

        self.hash_map.clear(self.test_key)
        self.assertEqual(self.hash_map.size(self.test_key), 0)
        self.assertEqual(self.hash_map.get_all(self.test_key), {})

    def test_complex_data_types(self):
        # Test with complex data types
        test_dict = {"key": "value", "nested": {"data": True}}
        test_list = [1, 2, [3, 4]]
        test_datetime = datetime.now()
        test_set = {1, 2, 3}
        test_tuple = (1, "two", 3.0)

        test_data = {
            "dict_field": test_dict,
            "list_field": test_list,
            "datetime_field": test_datetime,
            "set_field": test_set,
            "tuple_field": test_tuple
        }

        # Test setting complex types
        for field, value in test_data.items():
            self.assertTrue(self.hash_map.set(self.test_key, field, value))

        # Test getting complex types
        for field, value in test_data.items():
            retrieved = self.hash_map.get(self.test_key, field)
            if field == "datetime_field":
                # Compare datetime string representations due to microsecond precision
                self.assertEqual(retrieved.strftime("%Y-%m-%d %H:%M:%S"), value.strftime("%Y-%m-%d %H:%M:%S"))
            elif field == "set_field":
                self.assertEqual(set(retrieved), value)
            elif field == "tuple_field":
                self.assertEqual(tuple(retrieved), value)
            else:
                self.assertEqual(retrieved, value)

    def test_exists(self):
        # Test exists operation
        self.assertFalse(self.hash_map.exists(self.test_key, "field1"))

        self.hash_map.set(self.test_key, "field1", "value1")
        self.assertTrue(self.hash_map.exists(self.test_key, "field1"))

        self.hash_map.delete(self.test_key, "field1")
        self.assertFalse(self.hash_map.exists(self.test_key, "field1"))

    def test_get_fields(self):
        # Test get_fields operation
        test_data = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3",
        }

        for field, value in test_data.items():
            self.hash_map.set(self.test_key, field, value)

        fields = self.hash_map.get_fields(self.test_key)
        self.assertEqual(set(fields), set(test_data.keys()))

    def test_empty_operations(self):
        # Test operations on empty hash map
        self.assertEqual(self.hash_map.get_all(self.test_key), {})
        self.assertEqual(self.hash_map.get_fields(self.test_key), [])
        self.assertEqual(self.hash_map.size(self.test_key), 0)

    def test_none_value(self):
        # Test handling of None values
        self.assertTrue(self.hash_map.set(self.test_key, "null_field", None))
        self.assertIsNone(self.hash_map.get(self.test_key, "null_field"))

    def test_empty_string(self):
        # Test handling of empty strings
        self.assertTrue(self.hash_map.set(self.test_key, "empty_field", ""))
        self.assertEqual(self.hash_map.get(self.test_key, "empty_field"), "")

    def test_unicode_strings(self):
        # Test handling of unicode strings
        test_data = {
            "unicode_field1": "你好",  # Chinese
            "unicode_field2": "안녕하세요",  # Korean
            "unicode_field3": "Привет",  # Russian
            "unicode_field4": "🌟🎉🎈",  # Emojis
        }

        for field, value in test_data.items():
            self.assertTrue(self.hash_map.set(self.test_key, field, value))
            self.assertEqual(self.hash_map.get(self.test_key, field), value)

    # Error handling tests
    def test_set_error_handling(self):
        with patch.object(self.hash_map.connection_manager, "execute", side_effect=RedisError):
            self.assertFalse(self.hash_map.set(self.test_key, "field", "value"))

    def test_get_error_handling(self):
        with patch.object(self.hash_map.connection_manager, "execute", side_effect=RedisError):
            self.assertIsNone(self.hash_map.get(self.test_key, "field"))

    def test_delete_error_handling(self):
        with patch.object(self.hash_map.connection_manager, "execute", side_effect=RedisError):
            self.assertFalse(self.hash_map.delete(self.test_key, "field"))

    def test_exists_error_handling(self):
        with patch.object(self.hash_map.connection_manager, "execute", side_effect=RedisError):
            self.assertFalse(self.hash_map.exists(self.test_key, "field"))

    def test_get_all_error_handling(self):
        with patch.object(self.hash_map.connection_manager, "execute", side_effect=RedisError):
            self.assertEqual(self.hash_map.get_all(self.test_key), {})

    def test_get_fields_error_handling(self):
        with patch.object(self.hash_map.connection_manager, "execute", side_effect=RedisError):
            self.assertEqual(self.hash_map.get_fields(self.test_key), [])

    def test_size_error_handling(self):
        with patch.object(self.hash_map.connection_manager, "execute", side_effect=RedisError):
            self.assertEqual(self.hash_map.size(self.test_key), 0)

    def test_clear_error_handling(self):
        with patch.object(self.hash_map.connection_manager, "execute", side_effect=RedisError):
            self.assertFalse(self.hash_map.clear(self.test_key))


if __name__ == "__main__":
    unittest.main()
