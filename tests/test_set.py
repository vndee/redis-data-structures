import unittest

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
        assert self.set_ds.members(self.test_key) == set()


if __name__ == "__main__":
    unittest.main()
