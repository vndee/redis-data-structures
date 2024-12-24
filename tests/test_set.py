from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures import Set
from tests.test_base import User


@pytest.fixture
def set_ds(connection_manager) -> Set:
    """Create a Set instance for testing."""
    s = Set()
    test_key = "test_set"
    s.clear(test_key)
    yield s
    s.clear(test_key)


def test_add_and_remove(set_ds):
    """Test basic add and remove operations."""
    assert set_ds.add("test_set", "item1")
    assert set_ds.add("test_set", "item2")

    assert set_ds.size("test_set") == 2
    assert set_ds.remove("test_set", "item1")
    assert set_ds.size("test_set") == 1


def test_add_duplicate(set_ds):
    """Test adding duplicate items."""
    assert set_ds.add("test_set", "item1")
    assert not set_ds.add("test_set", "item1")  # Adding duplicate should fail
    assert set_ds.size("test_set") == 1


def test_remove_nonexistent(set_ds):
    """Test removing non-existent item."""
    assert not set_ds.remove("test_set", "nonexistent")


def test_contains(set_ds):
    """Test contains operation."""
    set_ds.add("test_set", "item1")
    assert set_ds.contains("test_set", "item1")
    assert not set_ds.contains("test_set", "nonexistent")


def test_members(set_ds):
    """Test getting all members."""
    items = {"item1", "item2", "item3"}
    for item in items:
        assert set_ds.add("test_set", item)

    members = set_ds.members("test_set")
    assert set(members) == items


def test_size(set_ds):
    """Test size operations."""
    assert set_ds.size("test_set") == 0

    set_ds.add("test_set", "item1")
    assert set_ds.size("test_set") == 1

    set_ds.add("test_set", "item2")
    assert set_ds.size("test_set") == 2

    set_ds.add("test_set", "item1")  # Adding duplicate
    assert set_ds.size("test_set") == 2  # Size should not change


def test_clear(set_ds):
    """Test clear operation."""
    set_ds.add("test_set", "item1")
    set_ds.add("test_set", "item2")

    assert set_ds.clear("test_set")
    assert set_ds.size("test_set") == 0
    assert set_ds.members("test_set") == set()


def test_pop(set_ds):
    """Test pop operation."""
    assert set_ds.pop("test_set") is None  # Pop on empty set

    set_ds.add("test_set", "item1")
    set_ds.add("test_set", "item2")

    popped = set_ds.pop("test_set")
    assert popped in {"item1", "item2"}
    assert set_ds.size("test_set") == 1


def test_complex_data_types(set_ds):
    """Test with complex data types."""
    test_json1 = {"key": "value", "nested": {"data": True}}
    test_json2 = [1, 2, [3, 4]]

    assert set_ds.add("test_set", test_json1)
    assert set_ds.add("test_set", test_json2)

    assert set_ds.contains("test_set", test_json1)
    assert set_ds.contains("test_set", test_json2)

    members = set_ds.members("test_set")
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
        set_ds.clear("test_set")  # Clear before each test
        assert set_ds.add("test_set", data)
        assert set_ds.contains("test_set", data)
        assert set_ds.size("test_set") == 1
        assert data in set_ds.members("test_set")


def test_add_error_handling(set_ds):
    """Test error handling in add method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert not set_ds.add("test_set", "data")


def test_remove_error_handling(set_ds):
    """Test error handling in remove method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert not set_ds.remove("test_set", "data")


def test_contains_error_handling(set_ds):
    """Test error handling in contains method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert not set_ds.contains("test_set", "data")


def test_members_error_handling(set_ds):
    """Test error handling in members method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert set_ds.members("test_set") == set()


def test_size_error_handling(set_ds):
    """Test error handling in size method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert set_ds.size("test_set") == 0


def test_pop_error_handling(set_ds):
    """Test error handling in pop method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert set_ds.pop("test_set") is None


# Additional tests for increased coverage
def test_add_and_remove_multiple_items(set_ds):
    """Test adding and removing multiple items."""
    items = ["item1", "item2", "item3"]
    for item in items:
        assert set_ds.add("test_set", item)

    assert set_ds.size("test_set") == 3

    for item in items:
        assert set_ds.remove("test_set", item)

    assert set_ds.size("test_set") == 0


def test_clear_empty_set(set_ds):
    """Test clearing an already empty set."""
    assert set_ds.clear("test_set")  # Should not raise an error


def test_contains_various_data_types(set_ds):
    """Test checking membership for various data types."""
    assert set_ds.add("test_set", 42)
    assert set_ds.add("test_set", "string")
    assert set_ds.add("test_set", (1, 2))
    assert set_ds.add("test_set", {"key": "value"})

    assert set_ds.contains("test_set", 42)
    assert set_ds.contains("test_set", "string")
    assert set_ds.contains("test_set", (1, 2))
    assert set_ds.contains("test_set", {"key": "value"})


def test_size_after_multiple_operations(set_ds):
    """Test size after multiple add and remove operations."""
    assert set_ds.size("test_set") == 0
    set_ds.add("test_set", "item1")
    set_ds.add("test_set", "item2")
    assert set_ds.size("test_set") == 2
    set_ds.remove("test_set", "item1")
    assert set_ds.size("test_set") == 1
    set_ds.remove("test_set", "item2")
    assert set_ds.size("test_set") == 0


def test_pop_from_single_item_set(set_ds):
    """Test popping from a set with one item."""
    set_ds.add("test_set", "item1")
    popped = set_ds.pop("test_set")
    assert popped == "item1"
    assert set_ds.size("test_set") == 0


def test_restore_type(set_ds):
    """Test restore_type method."""
    assert set_ds.restore_type({"_type": "int", "value": 42}) == 42
    assert set_ds.restore_type({"_type": "float", "value": 3.14}) == 3.14
    assert set_ds.restore_type({"_type": "str", "value": "hello"}) == "hello"
    assert set_ds.restore_type({"_type": "bool", "value": True}) is True
    assert set_ds.restore_type({"_type": "NoneType", "value": None}) is None

    assert set_ds.restore_type({"_type": "list", "value": [1, 2, 3]}) == [1, 2, 3]
    assert set_ds.restore_type({"_type": "dict", "value": {"a": 1, "b": 2}}) == {"a": 1, "b": 2}
    assert set_ds.restore_type({"_type": "tuple", "value": (1, 2, 3)}) == (1, 2, 3)

    assert User.from_dict(
        set_ds.restore_type({"_type": "User", "value": {"name": "Alice", "age": 30}}),
    ) == User(name="Alice", age=30)
    assert set_ds.restore_type(
        {
            "_type": "tuple",
            "value": [{"_type": "int", "value": 1}, {"_type": "str", "value": "two"}],
        },
    ) == (1, "two")
    assert set_ds.restore_type(
        {
            "_type": "set",
            "value": [{"_type": "str", "value": "item1"}, {"_type": "str", "value": "item2"}],
        },
    ) == {"item1", "item2"}


def test_make_hashable(set_ds):
    """Test make_hashable method."""
    assert set_ds.make_hashable({"a": 1, "b": 2}) == (("a", 1), ("b", 2))
    assert set_ds.make_hashable([1, 2, 3]) == (1, 2, 3)
    assert set_ds.make_hashable((1, 2, 3)) == (1, 2, 3)
    assert set_ds.make_hashable(42) == 42
    assert set_ds.make_hashable(3.14) == 3.14
    assert set_ds.make_hashable("hello") == "hello"
    assert set_ds.make_hashable(True) is True
    assert set_ds.make_hashable(None) is None
    assert set_ds.make_hashable({1, 2, 3}) == (1, 2, 3)
    assert set_ds.make_hashable(User(name="Alice", age=30)) == "User(name=Alice, age=30)"


def test_error_clear_set(set_ds):
    """Test error handling in clear method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert not set_ds.clear("test_set")


def test_error_members_get(set_ds):
    """Test error handling in members method."""
    with patch.object(set_ds.connection_manager, "execute", side_effect=RedisError):
        assert set_ds.members("test_set") == []


def test_members_error_handling(set_ds):
    """Test error handling in members method."""
    mock_data = [b'item1', b'item2', b'item3']

    with patch.object(set_ds.connection_manager, "execute", return_value=mock_data):
        with patch.object(set_ds, "deserialize", side_effect=[Exception("Deserialization error"), "item2", "item3"]):
            result = set_ds.members("test_set")
            assert result == ["item2", "item3"]  # Expect only the successfully deserialized items
