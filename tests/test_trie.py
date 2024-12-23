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
        assert self.trie.insert(self.test_key, "hello")
        assert self.trie.insert(self.test_key, "help")
        assert self.trie.insert(self.test_key, "world")

        assert self.trie.search(self.test_key, "hello")
        assert self.trie.search(self.test_key, "help")
        assert self.trie.search(self.test_key, "world")
        assert not self.trie.search(self.test_key, "hell")
        assert not self.trie.search(self.test_key, "helping")

    def test_starts_with(self):
        # Test prefix search operations
        words = ["hello", "help", "world", "helper", "helping"]
        for word in words:
            self.trie.insert(self.test_key, word)

        # Test various prefixes
        assert set(self.trie.starts_with(self.test_key, "hel")) == {
            "hello",
            "help",
            "helper",
            "helping",
        }
        assert set(self.trie.starts_with(self.test_key, "help")) == {"help", "helper", "helping"}
        assert set(self.trie.starts_with(self.test_key, "world")) == {"world"}
        assert set(self.trie.starts_with(self.test_key, "wor")) == {"world"}
        assert not self.trie.starts_with(self.test_key, "xyz")

    def test_delete(self):
        # Test delete operations
        words = ["hello", "help", "world", "helper"]
        for word in words:
            self.trie.insert(self.test_key, word)

        # Delete existing word
        assert self.trie.delete(self.test_key, "hello")
        assert not self.trie.search(self.test_key, "hello")
        assert self.trie.search(self.test_key, "help")

        # Try to delete non-existent word
        assert not self.trie.delete(self.test_key, "xyz")

        # Delete word and verify prefix still works
        assert self.trie.delete(self.test_key, "help")
        assert self.trie.search(self.test_key, "helper")
        assert set(self.trie.starts_with(self.test_key, "help")) == {"helper"}

    def test_size(self):
        # Test size operations
        assert self.trie.size(self.test_key) == 0

        words = ["hello", "help", "world", "helper"]
        for word in words:
            self.trie.insert(self.test_key, word)
        assert self.trie.size(self.test_key) == 4

        self.trie.delete(self.test_key, "hello")
        assert self.trie.size(self.test_key) == 3

    def test_clear(self):
        # Test clear operation
        words = ["hello", "help", "world", "helper"]
        for word in words:
            self.trie.insert(self.test_key, word)

        assert self.trie.size(self.test_key) > 0
        assert self.trie.clear(self.test_key)
        assert self.trie.size(self.test_key) == 0
        assert not self.trie.search(self.test_key, "hello")

    def test_empty_string(self):
        # Test edge case with empty string
        assert self.trie.insert(self.test_key, "")
        assert self.trie.search(self.test_key, "")
        assert self.trie.size(self.test_key) == 1
        assert self.trie.delete(self.test_key, "")
        assert not self.trie.search(self.test_key, "")
