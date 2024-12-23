import unittest

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


if __name__ == "__main__":
    unittest.main()
