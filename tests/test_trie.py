from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures import Trie


@pytest.fixture
def trie_ds() -> Trie:
    """Create a Trie instance for testing."""
    trie = Trie(key="test_trie")
    trie.clear()
    yield trie
    trie.clear()


def test_insert_and_search(trie_ds):
    """Test basic insert and search operations."""
    assert trie_ds.insert("hello")
    assert trie_ds.insert("help")
    assert trie_ds.insert("world")

    assert trie_ds.search("hello")
    assert trie_ds.search("help")
    assert trie_ds.search("world")
    assert not trie_ds.search("hell")
    assert not trie_ds.search("helping")


def test_starts_with(trie_ds):
    """Test prefix search operations."""
    words = ["hello", "help", "world", "helper", "helping"]
    for word in words:
        assert trie_ds.insert(word)

    assert set(trie_ds.starts_with("hel")) == {"hello", "help", "helper", "helping"}
    assert set(trie_ds.starts_with("help")) == {"help", "helper", "helping"}
    assert set(trie_ds.starts_with("world")) == {"world"}
    assert set(trie_ds.starts_with("wor")) == {"world"}
    assert trie_ds.starts_with("xyz") == []


def test_delete(trie_ds):
    """Test delete operations."""
    words = ["hello", "help", "world", "helper"]
    for word in words:
        assert trie_ds.insert(word)

    assert trie_ds.delete("hello")
    assert not trie_ds.search("hello")
    assert trie_ds.search("help")

    assert not trie_ds.delete("xyz")

    assert trie_ds.delete("help")
    assert trie_ds.search("helper")
    assert set(trie_ds.starts_with("help")) == {"helper"}


def test_size(trie_ds):
    """Test size operations."""
    assert trie_ds.size() == 0

    words = ["hello", "help", "world", "helper"]
    for word in words:
        assert trie_ds.insert(word)
    assert trie_ds.size() == 4

    assert trie_ds.delete("hello")
    assert trie_ds.size() == 3


def test_clear(trie_ds):
    """Test clear operation."""
    words = ["hello", "help", "world", "helper"]
    for word in words:
        assert trie_ds.insert(word)

    assert trie_ds.size() > 0
    assert trie_ds.clear()
    assert trie_ds.size() == 0
    assert not trie_ds.search("hello")


def test_empty_string(trie_ds):
    """Test edge case with empty string."""
    assert trie_ds.insert("")
    assert trie_ds.search("")
    assert trie_ds.size() == 1
    assert trie_ds.delete("")
    assert not trie_ds.search("")


def test_error_handling(trie_ds):
    """Test error handling."""
    with patch.object(trie_ds.connection_manager, "execute", side_effect=RedisError):
        assert not trie_ds.insert("test")
        assert not trie_ds.search("test")
        assert trie_ds.starts_with("test") == []
        assert not trie_ds.delete("test")
        assert trie_ds.size() == 0
        assert not trie_ds.clear()


def test_get_all_words(trie_ds):
    """Test get all words operation."""
    words = ["hello", "help", "world", "helper"]
    for word in words:
        assert trie_ds.insert(word)

    assert set(trie_ds.get_all_words()) == set(words)

    assert set(trie_ds.starts_with("")) == set(words)
