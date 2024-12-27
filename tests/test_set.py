from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures import Set


@pytest.fixture
def set_ds() -> Set:
    """Create a Set instance for testing."""
    s = Set("test_set")
    s.clear()
    yield s
    s.clear()


def test_add_and_remove(set_ds):
    """Test basic add and remove operations."""
    assert set_ds.add("item1")
    assert set_ds.add("item2")

    assert set_ds.size() == 2
    assert set_ds.remove("item1")
    assert set_ds.size() == 1


def test_add_duplicate(set_ds):
    """Test adding duplicate items."""
    assert set_ds.add("item1")
    assert not set_ds.add("item1")  # Adding duplicate should fail
    assert set_ds.size() == 1


def test_remove_nonexistent(set_ds):
    """Test removing non-existent item."""
    assert not set_ds.remove("nonexistent")


def test_contains(set_ds):
    """Test contains operation."""
    set_ds.add("item1")
    assert set_ds.contains("item1")
    assert not set_ds.contains("nonexistent")


def test_members(set_ds):
    """Test getting all members."""
    items = {"item1", "item2", "item3"}
    for item in items:
        assert set_ds.add(item)

    members = set_ds.members()
    assert set(members) == items


def test_size(set_ds):
    """Test size operations."""
    assert set_ds.size() == 0

    set_ds.add("item1")
    assert set_ds.size() == 1

    set_ds.add("item2")
    assert set_ds.size() == 2

    set_ds.add("item1")  # Adding duplicate
    assert set_ds.size() == 2  # Size should not change


def test_clear(set_ds):
    """Test clear operation."""
    set_ds.add("item1")
    set_ds.add("item2")

    assert set_ds.clear()
    assert set_ds.size() == 0
    assert set_ds.members() == []


def test_pop(set_ds):
    """Test pop operation."""
    assert set_ds.pop() is None  # Pop on empty set

    set_ds.add("item1")
    set_ds.add("item2")

    popped = set_ds.pop()
    assert popped in {"item1", "item2"}
    assert set_ds.size() == 1


def test_complex_data_types(set_ds):
    """Test with complex data types."""
    test_json1 = {"key": "value", "nested": {"data": True}}
    test_json2 = [1, 2, [3, 4]]

    assert set_ds.add(test_json1)
    assert set_ds.add(test_json2)

    assert set_ds.contains(test_json1)
    assert set_ds.contains(test_json2)

    members = set_ds.members()
    assert len(members) == 2
    assert test_json1 in members
    assert test_json2 in members


def test_serialization_edge_cases(set_ds):
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
        set_ds.clear()  # Clear before each test
        assert set_ds.add(data)
        assert set_ds.contains(data)
        assert set_ds.size() == 1
        assert data in set_ds.members()


def test_add_error_handling(set_ds):
    """Test error handling in add method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert not set_ds.add("data")


def test_remove_error_handling(set_ds):
    """Test error handling in remove method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert not set_ds.remove("data")


def test_contains_error_handling(set_ds):
    """Test error handling in contains method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert not set_ds.contains("data")


def test_size_error_handling(set_ds):
    """Test error handling in size method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert set_ds.size() == 0


def test_pop_error_handling(set_ds):
    """Test error handling in pop method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert set_ds.pop() is None


# Additional tests for increased coverage
def test_add_and_remove_multiple_items(set_ds):
    """Test adding and removing multiple items."""
    items = ["item1", "item2", "item3"]
    for item in items:
        assert set_ds.add(item)

    assert set_ds.size() == 3

    for item in items:
        assert set_ds.remove(item)

    assert set_ds.size() == 0


def test_clear_empty_set(set_ds):
    """Test clearing an already empty set."""
    assert set_ds.clear()  # Should not raise an error


def test_contains_various_data_types(set_ds):
    """Test checking membership for various data types."""
    assert set_ds.add(42)
    assert set_ds.add("string")
    assert set_ds.add((1, 2))
    assert set_ds.add({"key": "value"})

    assert set_ds.contains(42)
    assert set_ds.contains("string")
    assert set_ds.contains((1, 2))
    assert set_ds.contains({"key": "value"})


def test_size_after_multiple_operations(set_ds):
    """Test size after multiple add and remove operations."""
    assert set_ds.size() == 0
    set_ds.add("item1")
    set_ds.add("item2")
    assert set_ds.size() == 2
    set_ds.remove("item1")
    assert set_ds.size() == 1
    set_ds.remove("item2")
    assert set_ds.size() == 0


def test_pop_from_single_item_set(set_ds):
    """Test popping from a set with one item."""
    set_ds.add("item1")
    popped = set_ds.pop()
    assert popped == "item1"
    assert set_ds.size() == 0


def test_error_clear_set(set_ds):
    """Test error handling in clear method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert not set_ds.clear()
