from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures import Queue


@pytest.fixture
def queue() -> Queue:
    """Create a Queue instance for testing."""
    q = Queue(key="test_queue")
    q.clear()
    yield q
    q.clear()


def test_push_and_pop(queue):
    """Test basic push and pop operations."""
    assert queue.push("item1")
    assert queue.push("item2")

    assert queue.size() == 2
    assert queue.pop() == "item1"
    assert queue.pop() == "item2"


def test_pop_empty_queue(queue):
    """Test popping from empty queue."""
    assert queue.pop() is None


def test_size(queue):
    """Test size operations."""
    assert queue.size() == 0

    assert queue.push("item1")
    assert queue.size() == 1

    assert queue.push("item2")
    assert queue.size() == 2

    queue.pop()
    assert queue.size() == 1


def test_clear(queue):
    """Test clear operation."""
    assert queue.push("item1")
    assert queue.push("item2")

    assert queue.clear()
    assert queue.size() == 0


def test_fifo_order(queue):
    """Test FIFO ordering."""
    items = ["first", "second", "third"]
    for item in items:
        assert queue.push(item)

    for expected_item in items:
        assert queue.pop() == expected_item


def test_peek_operations(queue):
    """Test peek operations."""
    # Test peek on empty queue
    assert queue.peek() is None

    # Test peek with items
    assert queue.push("item1")
    assert queue.push("item2")

    # Peek should return front item without removing it
    assert queue.peek() == "item1"
    assert queue.size() == 2  # Size should remain unchanged

    # Peek again should return the same item
    assert queue.peek() == "item1"
    assert queue.size() == 2

    # Pop should remove the item we were peeking at
    assert queue.pop() == "item1"
    assert queue.peek() == "item2"


def test_complex_data_types(queue):
    """Test with complex data types."""
    test_dict = {"key": "value", "nested": {"data": True}}
    test_list = [1, 2, [3, 4]]

    assert queue.push(test_dict)
    assert queue.push(test_list)

    assert queue.peek() == test_dict
    assert queue.pop() == test_dict
    assert queue.pop() == test_list


def test_serialization_edge_cases(queue):
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
        assert queue.push(data)
        assert queue.peek() == data
        assert queue.pop() == data


# Error handling tests
def test_push_error_handling(queue):
    """Test error handling during push operation."""
    with patch.object(queue.connection_manager, "execute", side_effect=RedisError):
        assert not queue.push("data")


def test_pop_error_handling(queue):
    """Test error handling during pop operation."""
    with patch.object(queue.connection_manager, "execute", side_effect=RedisError):
        assert queue.pop() is None


def test_peek_error_handling(queue):
    """Test error handling during peek operation."""
    with patch.object(queue.connection_manager, "execute", side_effect=RedisError):
        assert queue.peek() is None


def test_size_error_handling(queue):
    """Test error handling during size operation."""
    with patch.object(queue.connection_manager, "execute", side_effect=RedisError):
        assert queue.size() == 0


def test_clear_error_handling(queue):
    """Test error handling during clear operation."""
    with patch.object(queue.connection_manager, "execute", side_effect=RedisError):
        assert not queue.clear()
