from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures import Stack


@pytest.fixture
def stack_ds() -> Stack:
    """Create a Stack instance for testing."""
    stack = Stack(key="test_stack")
    stack.clear()
    yield stack
    stack.clear()


def test_push_and_pop(stack_ds):
    """Test basic push and pop operations."""
    assert stack_ds.push("item1")
    assert stack_ds.push("item2")

    assert stack_ds.size() == 2
    assert stack_ds.pop() == "item2"
    assert stack_ds.pop() == "item1"


def test_pop_empty_stack(stack_ds):
    """Test popping from an empty stack."""
    assert stack_ds.pop() is None


def test_size(stack_ds):
    """Test size operations."""
    assert stack_ds.size() == 0

    stack_ds.push("item1")
    assert stack_ds.size() == 1

    stack_ds.push("item2")
    assert stack_ds.size() == 2

    stack_ds.pop()
    assert stack_ds.size() == 1


def test_clear(stack_ds):
    """Test clear operation."""
    stack_ds.push("item1")
    stack_ds.push("item2")

    assert stack_ds.clear()
    assert stack_ds.size() == 0


def test_peek(stack_ds):
    """Test peek operation."""
    assert stack_ds.peek() is None

    stack_ds.push("item1")
    stack_ds.push("item2")

    assert stack_ds.peek() == "item2"
    assert stack_ds.size() == 2  # Size should remain unchanged


def test_complex_data_types(stack_ds):
    """Test with complex data types."""
    test_dict = {"key": "value", "nested": {"data": True}}
    test_list = [1, 2, [3, 4]]

    assert stack_ds.push(test_dict)
    assert stack_ds.push(test_list)

    assert stack_ds.pop() == test_list
    assert stack_ds.pop() == test_dict


def test_serialization_edge_cases(stack_ds):
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
        stack_ds.clear()  # Clear before each test
        assert stack_ds.push(data)
        assert stack_ds.peek() == data
        assert stack_ds.pop() == data


# Error handling tests
def test_push_error_handling(stack_ds):
    """Test error handling in push method."""
    with patch.object(stack_ds.connection_manager, "execute", side_effect=RedisError):
        assert not stack_ds.push("data")


def test_pop_error_handling(stack_ds):
    """Test error handling in pop method."""
    with patch.object(stack_ds.connection_manager, "execute", side_effect=RedisError):
        assert stack_ds.pop() is None


def test_peek_error_handling(stack_ds):
    """Test error handling in peek method."""
    with patch.object(stack_ds.connection_manager, "execute", side_effect=RedisError):
        assert stack_ds.peek() is None


def test_size_error_handling(stack_ds):
    """Test error handling in size method."""
    with patch.object(stack_ds.connection_manager, "execute", side_effect=RedisError):
        assert stack_ds.size() == 0


def test_clear_error_handling(stack_ds):
    """Test error handling in clear method."""
    with patch.object(stack_ds.connection_manager, "execute", side_effect=RedisError):
        assert not stack_ds.clear()
