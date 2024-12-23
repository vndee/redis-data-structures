import json
import unittest
from unittest.mock import patch

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
        """Test basic add and remove operations."""
        # Test adding items
        self.assertTrue(self.set_ds.add(self.test_key, "item1"), "Failed to add item1")
        self.assertTrue(self.set_ds.add(self.test_key, "item2"), "Failed to add item2")

        # Test size after adding
        self.assertEqual(self.set_ds.size(self.test_key), 2, "Set should have 2 items")

        # Test removing item
        self.assertTrue(self.set_ds.remove(self.test_key, "item1"), "Failed to remove item1")
        self.assertEqual(self.set_ds.size(self.test_key), 1, "Set should have 1 item after removal")

    def test_add_duplicate(self):
        """Test adding duplicate items."""
        # First addition should succeed
        self.assertTrue(self.set_ds.add(self.test_key, "item1"), "Failed to add item1")
        # Second addition should fail (duplicate)
        self.assertFalse(
            self.set_ds.add(self.test_key, "item1"),
            "Adding duplicate should return False",
        )
        # Size should still be 1
        self.assertEqual(
            self.set_ds.size(self.test_key),
            1,
            "Set size should be 1 after adding duplicate",
        )

    def test_remove_nonexistent(self):
        """Test removing non-existent item."""
        self.assertFalse(
            self.set_ds.remove(self.test_key, "nonexistent"),
            "Removing non-existent item should return False",
        )

    def test_contains(self):
        """Test contains operation."""
        # Add an item
        self.set_ds.add(self.test_key, "item1")

        # Test membership
        self.assertTrue(
            self.set_ds.contains(self.test_key, "item1"),
            "Set should contain added item",
        )
        self.assertFalse(
            self.set_ds.contains(self.test_key, "nonexistent"),
            "Set should not contain non-existent item",
        )

    def test_members(self):
        """Test getting all members."""
        items = {"item1", "item2", "item3"}
        for item in items:
            self.assertTrue(self.set_ds.add(self.test_key, item), f"Failed to add {item}")

        # Test members retrieval
        members = self.set_ds.members(self.test_key)
        self.assertEqual(members, items, "Retrieved members should match added items")

    def test_size(self):
        """Test size operations."""
        # Test empty set
        self.assertEqual(self.set_ds.size(self.test_key), 0, "Empty set should have size 0")

        # Test after adding one item
        self.set_ds.add(self.test_key, "item1")
        self.assertEqual(
            self.set_ds.size(self.test_key),
            1,
            "Set should have size 1 after adding one item",
        )

        # Test after adding second item
        self.set_ds.add(self.test_key, "item2")
        self.assertEqual(
            self.set_ds.size(self.test_key),
            2,
            "Set should have size 2 after adding second item",
        )

        # Test after adding duplicate
        self.set_ds.add(self.test_key, "item1")
        self.assertEqual(
            self.set_ds.size(self.test_key),
            2,
            "Set size should not change after adding duplicate",
        )

    def test_clear(self):
        """Test clear operation."""
        # Add items
        self.set_ds.add(self.test_key, "item1")
        self.set_ds.add(self.test_key, "item2")

        # Clear and verify
        self.set_ds.clear(self.test_key)
        self.assertEqual(self.set_ds.size(self.test_key), 0, "Set should be empty after clear")
        self.assertEqual(
            self.set_ds.members(self.test_key),
            set(),
            "Set members should be empty after clear",
        )

    def test_pop(self):
        """Test pop operation."""
        # Test pop on empty set
        self.assertIsNone(self.set_ds.pop(self.test_key), "Pop on empty set should return None")

        # Add items and test pop
        items = {"item1", "item2", "item3"}
        for item in items:
            self.set_ds.add(self.test_key, item)

        # Pop and verify
        popped = self.set_ds.pop(self.test_key)
        self.assertIn(popped, items, "Popped item should be one of the added items")
        self.assertEqual(self.set_ds.size(self.test_key), 2, "Set size should decrease after pop")
        self.assertFalse(
            self.set_ds.contains(self.test_key, popped),
            "Set should not contain popped item",
        )

    def test_complex_data_types(self):
        """Test with complex data types."""
        # Test with JSON data
        test_json1 = json.dumps({"key": "value", "nested": {"data": True}})
        test_json2 = json.dumps([1, 2, [3, 4]])

        # Add complex items
        self.assertTrue(self.set_ds.add(self.test_key, test_json1), "Failed to add first JSON item")
        self.assertTrue(
            self.set_ds.add(self.test_key, test_json2),
            "Failed to add second JSON item",
        )

        # Test membership
        self.assertTrue(
            self.set_ds.contains(self.test_key, test_json1),
            "Set should contain first JSON item",
        )
        self.assertTrue(
            self.set_ds.contains(self.test_key, test_json2),
            "Set should contain second JSON item",
        )

        # Test members retrieval
        members = self.set_ds.members(self.test_key)
        self.assertEqual(len(members), 2, "Set should contain exactly 2 items")
        self.assertIn(test_json1, members, "Members should contain first JSON item")
        self.assertIn(test_json2, members, "Members should contain second JSON item")

    def test_serialization_edge_cases(self):
        """Test with various data types."""
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
            '{"nested": {"data": [1, 2, 3]}}',  # Complex JSON string
        ]

        for data in test_cases:
            with self.subTest(data=data):
                self.set_ds.clear(self.test_key)  # Clear before each test

                # Test add
                self.assertTrue(self.set_ds.add(self.test_key, data), f"Failed to add {data!r}")

                # Test contains
                self.assertTrue(
                    self.set_ds.contains(self.test_key, data),
                    f"Failed to find {data!r}",
                )

                # Test members
                members = self.set_ds.members(self.test_key)
                self.assertEqual(len(members), 1, f"Set should contain exactly 1 item for {data!r}")
                self.assertIn(data, members, f"Members should contain {data!r}")

                # Test remove
                self.assertTrue(
                    self.set_ds.remove(self.test_key, data),
                    f"Failed to remove {data!r}",
                )

    def test_add_error_handling(self):
        """Test error handling in add method."""
        with patch.object(self.set_ds.redis_client, "sadd", side_effect=RedisError):
            self.assertFalse(
                self.set_ds.add(self.test_key, "data"),
                "Should return False on Redis error",
            )

    def test_remove_error_handling(self):
        """Test error handling in remove method."""
        # Test error during smembers operation
        with patch.object(self.set_ds.redis_client, "smembers", side_effect=RedisError):
            self.assertFalse(
                self.set_ds.remove(self.test_key, "data"),
                "Should return False on Redis error during find",
            )

        # Test error during srem operation
        self.set_ds.add(self.test_key, "data")
        with patch.object(self.set_ds.redis_client, "srem", side_effect=RedisError):
            self.assertFalse(
                self.set_ds.remove(self.test_key, "data"),
                "Should return False on Redis error during remove",
            )

    def test_contains_error_handling(self):
        """Test error handling in contains method."""
        with patch.object(self.set_ds.redis_client, "smembers", side_effect=RedisError):
            self.assertFalse(
                self.set_ds.contains(self.test_key, "data"),
                "Should return False on Redis error",
            )

    def test_members_error_handling(self):
        """Test error handling in members method."""
        with patch.object(self.set_ds.redis_client, "smembers", side_effect=RedisError):
            self.assertEqual(
                self.set_ds.members(self.test_key),
                set(),
                "Should return empty set on Redis error",
            )

    def test_size_error_handling(self):
        """Test error handling in size method."""
        with patch.object(self.set_ds.redis_client, "scard", side_effect=RedisError):
            self.assertEqual(self.set_ds.size(self.test_key), 0, "Should return 0 on Redis error")

    def test_pop_error_handling(self):
        """Test error handling in pop method."""
        with patch.object(self.set_ds.redis_client, "spop", side_effect=RedisError):
            self.assertIsNone(self.set_ds.pop(self.test_key), "Should return None on Redis error")


if __name__ == "__main__":
    unittest.main()
