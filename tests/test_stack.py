import unittest
from unittest.mock import patch

from redis.exceptions import RedisError

from redis_data_structures import Stack


class TestStack(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.stack_ds = Stack()
        self.test_key = "test_stack"
        self.stack_ds.clear(self.test_key)

    def tearDown(self):
        """Clean up after tests."""
        self.stack_ds.clear(self.test_key)

    def test_push_and_pop(self):
        """Test basic push and pop operations."""
        # Test pushing items
        self.assertTrue(self.stack_ds.push(self.test_key, "item1"), "Failed to push item1")
        self.assertTrue(self.stack_ds.push(self.test_key, "item2"), "Failed to push item2")

        # Test size after pushing
        self.assertEqual(self.stack_ds.size(self.test_key), 2, "Stack should have 2 items")

        # Test popping items
        self.assertEqual(self.stack_ds.pop(self.test_key), "item2", "Wrong item popped")
        self.assertEqual(self.stack_ds.pop(self.test_key), "item1", "Wrong item popped")
        self.assertIsNone(self.stack_ds.pop(self.test_key), "Empty stack should return None")

    def test_peek(self):
        """Test peek operation."""
        # Test peek on empty stack
        self.assertIsNone(self.stack_ds.peek(self.test_key), "Peek on empty stack should return None")

        # Add items and test peek
        self.stack_ds.push(self.test_key, "item1")
        self.stack_ds.push(self.test_key, "item2")

        # Peek should return top item without removing it
        self.assertEqual(self.stack_ds.peek(self.test_key), "item2", "Peek should return top item")
        self.assertEqual(self.stack_ds.size(self.test_key), 2, "Size should not change after peek")

        # Peek again should return same item
        self.assertEqual(self.stack_ds.peek(self.test_key), "item2", "Second peek should return same item")

    def test_size(self):
        """Test size operations."""
        # Test empty stack
        self.assertEqual(self.stack_ds.size(self.test_key), 0, "Empty stack should have size 0")

        # Test after pushing one item
        self.stack_ds.push(self.test_key, "item1")
        self.assertEqual(
            self.stack_ds.size(self.test_key),
            1,
            "Stack should have size 1 after pushing one item",
        )

        # Test after pushing second item
        self.stack_ds.push(self.test_key, "item2")
        self.assertEqual(
            self.stack_ds.size(self.test_key),
            2,
            "Stack should have size 2 after pushing second item",
        )

        # Test after popping
        self.stack_ds.pop(self.test_key)
        self.assertEqual(
            self.stack_ds.size(self.test_key),
            1,
            "Stack should have size 1 after popping",
        )

    def test_clear(self):
        """Test clear operation."""
        # Add items
        self.stack_ds.push(self.test_key, "item1")
        self.stack_ds.push(self.test_key, "item2")

        # Clear and verify
        self.assertTrue(self.stack_ds.clear(self.test_key), "Clear should return True")
        self.assertEqual(self.stack_ds.size(self.test_key), 0, "Stack should be empty after clear")
        self.assertIsNone(self.stack_ds.peek(self.test_key), "Peek should return None after clear")

    def test_complex_data_types(self):
        """Test with complex data types."""
        # Test with JSON data
        test_dict = {"key": "value", "nested": {"data": True}}
        test_list = [1, 2, [3, 4]]

        # Push complex items
        self.assertTrue(self.stack_ds.push(self.test_key, test_dict), "Failed to push dictionary")
        self.assertTrue(self.stack_ds.push(self.test_key, test_list), "Failed to push list")

        # Test peek and pop with complex items
        self.assertEqual(self.stack_ds.peek(self.test_key), test_list, "Peek should return list")
        self.assertEqual(self.stack_ds.pop(self.test_key), test_list, "Pop should return list")
        self.assertEqual(self.stack_ds.pop(self.test_key), test_dict, "Pop should return dictionary")

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
            [],
            [1, 2, 3],
            {},
            {"a": 1, "b": 2},
            {"nested": {"data": [1, 2, 3]}},
        ]

        for data in test_cases:
            with self.subTest(data=data):
                self.stack_ds.clear(self.test_key)  # Clear before each test

                # Test push
                self.assertTrue(
                    self.stack_ds.push(self.test_key, data),
                    f"Failed to push {data!r}",
                )

                # Test peek
                self.assertEqual(
                    self.stack_ds.peek(self.test_key),
                    data,
                    f"Peek should return {data!r}",
                )

                # Test pop
                self.assertEqual(
                    self.stack_ds.pop(self.test_key),
                    data,
                    f"Pop should return {data!r}",
                )

    def test_push_error_handling(self):
        """Test error handling in push method."""
        with patch.object(self.stack_ds.connection_manager, "execute", side_effect=RedisError):
            self.assertFalse(
                self.stack_ds.push(self.test_key, "data"),
                "Should return False on Redis error",
            )

    def test_pop_error_handling(self):
        """Test error handling in pop method."""
        with patch.object(self.stack_ds.connection_manager, "execute", side_effect=RedisError):
            self.assertIsNone(
                self.stack_ds.pop(self.test_key),
                "Should return None on Redis error",
            )

    def test_peek_error_handling(self):
        """Test error handling in peek method."""
        with patch.object(self.stack_ds.connection_manager, "execute", side_effect=RedisError):
            self.assertIsNone(
                self.stack_ds.peek(self.test_key),
                "Should return None on Redis error",
            )

    def test_size_error_handling(self):
        """Test error handling in size method."""
        with patch.object(self.stack_ds.connection_manager, "execute", side_effect=RedisError):
            self.assertEqual(
                self.stack_ds.size(self.test_key),
                0,
                "Should return 0 on Redis error",
            )


if __name__ == "__main__":
    unittest.main()
