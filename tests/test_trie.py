import unittest

from redis_data_structures import Trie


class TestTrie(unittest.TestCase):
    def setUp(self):
        self.trie = Trie(host="localhost", port=6379, db=0)
        self.test_key = "test_trie"
        self.trie.clear(self.test_key)

    def tearDown(self):
        self.trie.clear(self.test_key)

    def test_insert_and_search(self):
        # Test basic insert and search operations
        self.assertTrue(self.trie.insert(self.test_key, "hello"))
        self.assertTrue(self.trie.insert(self.test_key, "help"))
        self.assertTrue(self.trie.insert(self.test_key, "world"))

        self.assertTrue(self.trie.search(self.test_key, "hello"))
        self.assertTrue(self.trie.search(self.test_key, "help"))
        self.assertTrue(self.trie.search(self.test_key, "world"))
        self.assertFalse(self.trie.search(self.test_key, "hell"))
        self.assertFalse(self.trie.search(self.test_key, "helping"))

    def test_starts_with(self):
        # Test prefix search operations
        words = ["hello", "help", "world", "helper", "helping"]
        for word in words:
            self.trie.insert(self.test_key, word)

        # Test various prefixes
        self.assertEqual(
            set(self.trie.starts_with(self.test_key, "hel")),
            {"hello", "help", "helper", "helping"},
        )
        self.assertEqual(
            set(self.trie.starts_with(self.test_key, "help")),
            {"help", "helper", "helping"},
        )
        self.assertEqual(
            set(self.trie.starts_with(self.test_key, "world")),
            {"world"},
        )
        self.assertEqual(
            set(self.trie.starts_with(self.test_key, "wor")),
            {"world"},
        )
        self.assertFalse(self.trie.starts_with(self.test_key, "xyz"))

    def test_delete(self):
        # Test delete operations
        words = ["hello", "help", "world", "helper"]
        for word in words:
            self.trie.insert(self.test_key, word)

        # Delete existing word
        self.assertTrue(self.trie.delete(self.test_key, "hello"))
        self.assertFalse(self.trie.search(self.test_key, "hello"))
        self.assertTrue(self.trie.search(self.test_key, "help"))

        # Try to delete non-existent word
        self.assertFalse(self.trie.delete(self.test_key, "xyz"))

        # Delete word and verify prefix still works
        self.assertTrue(self.trie.delete(self.test_key, "help"))
        self.assertTrue(self.trie.search(self.test_key, "helper"))
        self.assertEqual(
            set(self.trie.starts_with(self.test_key, "help")),
            {"helper"},
        )

    def test_size(self):
        # Test size operations
        self.assertEqual(self.trie.size(self.test_key), 0)

        words = ["hello", "help", "world", "helper"]
        for word in words:
            self.trie.insert(self.test_key, word)
        self.assertEqual(self.trie.size(self.test_key), 4)

        self.trie.delete(self.test_key, "hello")
        self.assertEqual(self.trie.size(self.test_key), 3)

    def test_clear(self):
        # Test clear operation
        words = ["hello", "help", "world", "helper"]
        for word in words:
            self.trie.insert(self.test_key, word)

        self.assertGreater(self.trie.size(self.test_key), 0)
        self.assertTrue(self.trie.clear(self.test_key))
        self.assertEqual(self.trie.size(self.test_key), 0)
        self.assertFalse(self.trie.search(self.test_key, "hello"))

    def test_empty_string(self):
        # Test edge case with empty string
        self.assertTrue(self.trie.insert(self.test_key, ""))
        self.assertTrue(self.trie.search(self.test_key, ""))
        self.assertEqual(self.trie.size(self.test_key), 1)
        self.assertTrue(self.trie.delete(self.test_key, ""))
        self.assertFalse(self.trie.search(self.test_key, ""))
