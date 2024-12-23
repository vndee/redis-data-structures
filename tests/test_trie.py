import unittest
from unittest.mock import patch

from redis.exceptions import RedisError

from redis_data_structures import Trie


class TestTrie(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.trie_ds = Trie()
        self.test_key = "test_trie"
        self.trie_ds.clear(self.test_key)

    def tearDown(self):
        """Clean up after tests."""
        self.trie_ds.clear(self.test_key)

    def test_insert_and_search(self):
        """Test basic insert and search operations."""
        # Test basic insert and search operations
        self.assertTrue(self.trie_ds.insert(self.test_key, "hello"), "Failed to insert 'hello'")
        self.assertTrue(self.trie_ds.insert(self.test_key, "help"), "Failed to insert 'help'")
        self.assertTrue(self.trie_ds.insert(self.test_key, "world"), "Failed to insert 'world'")

        self.assertTrue(self.trie_ds.search(self.test_key, "hello"), "'hello' should be found")
        self.assertTrue(self.trie_ds.search(self.test_key, "help"), "'help' should be found")
        self.assertTrue(self.trie_ds.search(self.test_key, "world"), "'world' should be found")
        self.assertFalse(self.trie_ds.search(self.test_key, "hell"), "'hell' should not be found")
        self.assertFalse(self.trie_ds.search(self.test_key, "helping"), "'helping' should not be found")

    def test_starts_with(self):
        """Test prefix search operations."""
        # Add test words
        words = ["hello", "help", "world", "helper", "helping"]
        for word in words:
            self.assertTrue(self.trie_ds.insert(self.test_key, word), f"Failed to insert '{word}'")

        # Test various prefixes
        self.assertEqual(
            set(self.trie_ds.starts_with(self.test_key, "hel")),
            {"hello", "help", "helper", "helping"},
            "Wrong results for prefix 'hel'",
        )
        self.assertEqual(
            set(self.trie_ds.starts_with(self.test_key, "help")),
            {"help", "helper", "helping"},
            "Wrong results for prefix 'help'",
        )
        self.assertEqual(
            set(self.trie_ds.starts_with(self.test_key, "world")),
            {"world"},
            "Wrong results for prefix 'world'",
        )
        self.assertEqual(
            set(self.trie_ds.starts_with(self.test_key, "wor")),
            {"world"},
            "Wrong results for prefix 'wor'",
        )
        self.assertEqual(
            self.trie_ds.starts_with(self.test_key, "xyz"),
            [],
            "Should return empty list for non-existent prefix",
        )

    def test_delete(self):
        """Test delete operations."""
        # Add test words
        words = ["hello", "help", "world", "helper"]
        for word in words:
            self.assertTrue(self.trie_ds.insert(self.test_key, word), f"Failed to insert '{word}'")

        # Delete existing word
        self.assertTrue(self.trie_ds.delete(self.test_key, "hello"), "Failed to delete 'hello'")
        self.assertFalse(self.trie_ds.search(self.test_key, "hello"), "'hello' should be deleted")
        self.assertTrue(self.trie_ds.search(self.test_key, "help"), "'help' should still exist")

        # Try to delete non-existent word
        self.assertFalse(self.trie_ds.delete(self.test_key, "xyz"), "Should not delete non-existent word")

        # Delete word and verify prefix still works
        self.assertTrue(self.trie_ds.delete(self.test_key, "help"), "Failed to delete 'help'")
        self.assertTrue(self.trie_ds.search(self.test_key, "helper"), "'helper' should still exist")
        self.assertEqual(
            set(self.trie_ds.starts_with(self.test_key, "help")),
            {"helper"},
            "Wrong results after deleting 'help'",
        )

    def test_size(self):
        """Test size operations."""
        # Test empty trie
        self.assertEqual(self.trie_ds.size(self.test_key), 0, "Empty trie should have size 0")

        # Add words and test size
        words = ["hello", "help", "world", "helper"]
        for word in words:
            self.assertTrue(self.trie_ds.insert(self.test_key, word), f"Failed to insert '{word}'")
        self.assertEqual(self.trie_ds.size(self.test_key), 4, "Trie should have 4 words")

        # Delete word and test size
        self.assertTrue(self.trie_ds.delete(self.test_key, "hello"), "Failed to delete 'hello'")
        self.assertEqual(self.trie_ds.size(self.test_key), 3, "Trie should have 3 words after deletion")

    def test_clear(self):
        """Test clear operation."""
        # Add test words
        words = ["hello", "help", "world", "helper"]
        for word in words:
            self.assertTrue(self.trie_ds.insert(self.test_key, word), f"Failed to insert '{word}'")

        # Test clear operation
        self.assertGreater(self.trie_ds.size(self.test_key), 0, "Trie should not be empty")
        self.assertTrue(self.trie_ds.clear(self.test_key), "Failed to clear trie")
        self.assertEqual(self.trie_ds.size(self.test_key), 0, "Trie should be empty after clear")
        self.assertFalse(self.trie_ds.search(self.test_key, "hello"), "No words should exist after clear")

    def test_empty_string(self):
        """Test edge case with empty string."""
        # Test empty string operations
        self.assertTrue(self.trie_ds.insert(self.test_key, ""), "Failed to insert empty string")
        self.assertTrue(self.trie_ds.search(self.test_key, ""), "Empty string should be found")
        self.assertEqual(self.trie_ds.size(self.test_key), 1, "Trie should have size 1 with empty string")
        self.assertTrue(self.trie_ds.delete(self.test_key, ""), "Failed to delete empty string")
        self.assertFalse(self.trie_ds.search(self.test_key, ""), "Empty string should be deleted")

    def test_error_handling(self):
        """Test error handling."""
        with patch.object(self.trie_ds.connection_manager, "execute", side_effect=RedisError):
            self.assertFalse(
                self.trie_ds.insert(self.test_key, "test"),
                "Insert should return False on Redis error",
            )
            self.assertFalse(
                self.trie_ds.search(self.test_key, "test"),
                "Search should return False on Redis error",
            )
            self.assertEqual(
                self.trie_ds.starts_with(self.test_key, "test"),
                [],
                "Starts with should return empty list on Redis error",
            )
            self.assertFalse(
                self.trie_ds.delete(self.test_key, "test"),
                "Delete should return False on Redis error",
            )
            self.assertEqual(
                self.trie_ds.size(self.test_key),
                0,
                "Size should return 0 on Redis error",
            )
            self.assertFalse(
                self.trie_ds.clear(self.test_key),
                "Clear should return False on Redis error",
            )


if __name__ == "__main__":
    unittest.main()
