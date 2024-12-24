from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures import Trie


@pytest.fixture
def trie_ds(connection_manager) -> Trie:
    """Create a Trie instance for testing."""
    trie = Trie()
    test_key = "test_trie"
    trie.clear(test_key)
    yield trie
    trie.clear(test_key)


def test_insert_and_search(trie_ds):
    """Test basic insert and search operations."""
    assert trie_ds.insert("test_trie", "hello")
    assert trie_ds.insert("test_trie", "help")
    assert trie_ds.insert("test_trie", "world")

    assert trie_ds.search("test_trie", "hello")
    assert trie_ds.search("test_trie", "help")
    assert trie_ds.search("test_trie", "world")
    assert not trie_ds.search("test_trie", "hell")
    assert not trie_ds.search("test_trie", "helping")


def test_starts_with(trie_ds):
    """Test prefix search operations."""
    words = ["hello", "help", "world", "helper", "helping"]
    for word in words:
        assert trie_ds.insert("test_trie", word)

    assert set(trie_ds.starts_with("test_trie", "hel")) == {"hello", "help", "helper", "helping"}
    assert set(trie_ds.starts_with("test_trie", "help")) == {"help", "helper", "helping"}
    assert set(trie_ds.starts_with("test_trie", "world")) == {"world"}
    assert set(trie_ds.starts_with("test_trie", "wor")) == {"world"}
    assert trie_ds.starts_with("test_trie", "xyz") == []


def test_delete(trie_ds):
    """Test delete operations."""
    words = ["hello", "help", "world", "helper"]
    for word in words:
        assert trie_ds.insert("test_trie", word)

    assert trie_ds.delete("test_trie", "hello")
    assert not trie_ds.search("test_trie", "hello")
    assert trie_ds.search("test_trie", "help")

    assert not trie_ds.delete("test_trie", "xyz")

    assert trie_ds.delete("test_trie", "help")
    assert trie_ds.search("test_trie", "helper")
    assert set(trie_ds.starts_with("test_trie", "help")) == {"helper"}


def test_size(trie_ds):
    """Test size operations."""
    assert trie_ds.size("test_trie") == 0

    words = ["hello", "help", "world", "helper"]
    for word in words:
        assert trie_ds.insert("test_trie", word)
    assert trie_ds.size("test_trie") == 4

    assert trie_ds.delete("test_trie", "hello")
    assert trie_ds.size("test_trie") == 3


def test_clear(trie_ds):
    """Test clear operation."""
    words = ["hello", "help", "world", "helper"]
    for word in words:
        assert trie_ds.insert("test_trie", word)

    assert trie_ds.size("test_trie") > 0
    assert trie_ds.clear("test_trie")
    assert trie_ds.size("test_trie") == 0
    assert not trie_ds.search("test_trie", "hello")


def test_empty_string(trie_ds):
    """Test edge case with empty string."""
    assert trie_ds.insert("test_trie", "")
    assert trie_ds.search("test_trie", "")
    assert trie_ds.size("test_trie") == 1
    assert trie_ds.delete("test_trie", "")
    assert not trie_ds.search("test_trie", "")


def test_error_handling(trie_ds):
    """Test error handling."""
    with patch.object(trie_ds.connection_manager, "execute", side_effect=RedisError):
        assert not trie_ds.insert("test_trie", "test")
        assert not trie_ds.search("test_trie", "test")
        assert trie_ds.starts_with("test_trie", "test") == []
        assert not trie_ds.delete("test_trie", "test")
        assert trie_ds.size("test_trie") == 0
        assert not trie_ds.clear("test_trie")


def test_type_validation(trie_ds):
    """Test type validation."""
    assert trie_ds.insert("test_trie", "hello")
    assert trie_ds.insert("test_trie", 123) is False
    assert trie_ds.search("test_trie", "hello")
    assert trie_ds.search("test_trie", 123) is False
    assert trie_ds.starts_with("test_trie", "hel") == ["hello"]
    assert trie_ds.starts_with("test_trie", 123) == []
    assert trie_ds.delete("test_trie", "hello")
    assert trie_ds.delete("test_trie", 123) is False


def test_get_all_words(trie_ds):
    """Test get all words operation."""
    words = ["hello", "help", "world", "helper"]
    for word in words:
        assert trie_ds.insert("test_trie", word)
    assert set(trie_ds.get_all_words("test_trie")) == set(words)

    assert set(trie_ds.starts_with("test_trie", "")) == set(words)

