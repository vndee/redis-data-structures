from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures import PriorityQueue


@pytest.fixture
def priority_queue() -> PriorityQueue:
    """Create a PriorityQueue instance for testing."""
    pq = PriorityQueue("test_priority_queue", host="localhost", port=6379, db=0)
    pq.clear()
    yield pq
    pq.clear()


def test_push_and_pop(priority_queue):
    """Test basic push and pop operations."""
    assert priority_queue.push("low_priority", 3)
    assert priority_queue.push("high_priority", 1)

    assert priority_queue.size() == 2
    item, priority = priority_queue.pop()
    assert item == "high_priority"
    assert priority == 1


def test_pop_empty_queue(priority_queue):
    """Test popping from empty queue."""
    assert priority_queue.pop() is None


def test_size(priority_queue):
    """Test size operations."""
    assert priority_queue.size() == 0

    priority_queue.push("item1", 1)
    assert priority_queue.size() == 1

    priority_queue.push("item2", 2)
    assert priority_queue.size() == 2

    priority_queue.pop()
    assert priority_queue.size() == 1


def test_clear(priority_queue):
    """Test clear operation."""
    priority_queue.push("item1", 1)
    priority_queue.push("item2", 2)

    assert priority_queue.clear()
    assert priority_queue.size() == 0


def test_priority_order(priority_queue):
    """Test priority ordering (lower number = higher priority)."""
    items = [("lowest", 3), ("highest", 1), ("medium", 2)]

    for item, priority in items:
        priority_queue.push(item, priority)

    # Should pop in order: highest (1), medium (2), lowest (3)
    expected_order = ["highest", "medium", "lowest"]
    for expected_item in expected_order:
        item, _ = priority_queue.pop()
        assert item == expected_item


def test_same_priority(priority_queue):
    """Test items with same priority."""
    priority_queue.push("first", 1)
    priority_queue.push("second", 1)

    # Should maintain order for same priority
    item1, _ = priority_queue.pop()
    item2, _ = priority_queue.pop()
    assert item1 == "first"
    assert item2 == "second"


def test_peek_operations(priority_queue):
    """Test peek operations."""
    assert priority_queue.peek() is None

    priority_queue.push("item1", 2)
    priority_queue.push("item2", 1)

    # Peek should return highest priority item without removing it
    item, priority = priority_queue.peek()
    assert item == "item2"
    assert priority == 1
    assert priority_queue.size() == 2  # Size should remain unchanged

    # Peek again should return the same item
    item, priority = priority_queue.peek()
    assert item == "item2"
    assert priority == 1


def test_get_all(priority_queue):
    """Test getting all items in priority order."""
    items = [("lowest", 3), ("highest", 1), ("medium", 2), ("also_high", 1)]

    for item, priority in items:
        priority_queue.push(item, priority)

    all_items = priority_queue.get_all()
    assert len(all_items) == 4

    # Check items are in priority order
    priorities = [p for _, p in all_items]
    assert priorities == sorted(priorities)


def test_complex_data_types(priority_queue):
    """Test with complex data types."""
    test_dict = {"key": "value", "nested": {"data": True}}
    test_list = [1, 2, [3, 4]]

    priority_queue.push(test_dict, 1)
    priority_queue.push(test_list, 2)

    item1, priority1 = priority_queue.pop()
    item2, priority2 = priority_queue.pop()

    assert item1 == test_dict
    assert priority1 == 1
    assert item2 == test_list
    assert priority2 == 2


def test_negative_priority(priority_queue):
    """Test with negative priority values."""
    priority_queue.push("negative", -1)
    priority_queue.push("positive", 1)
    priority_queue.push("zero", 0)

    # Should pop in order: negative (-1), zero (0), positive (1)
    item1, priority1 = priority_queue.pop()
    item2, priority2 = priority_queue.pop()
    item3, priority3 = priority_queue.pop()

    assert item1 == "negative"
    assert priority1 == -1
    assert item2 == "zero"
    assert priority2 == 0
    assert item3 == "positive"
    assert priority3 == 1


def test_error_handling(priority_queue):
    """Test error handling."""
    # Test Redis error during push
    with patch.object(priority_queue.connection_manager, "execute", side_effect=RedisError):
        assert not priority_queue.push("data", 1)

    # Test Redis error during pop
    with patch.object(priority_queue.connection_manager, "execute", side_effect=RedisError):
        assert priority_queue.pop() is None

    # Test Redis error during peek
    with patch.object(priority_queue.connection_manager, "execute", side_effect=RedisError):
        assert priority_queue.peek() is None

    # Test Redis error during size
    with patch.object(priority_queue.connection_manager, "execute", side_effect=RedisError):
        assert priority_queue.size() == 0

    # Test Redis error during clear
    with patch.object(priority_queue.connection_manager, "execute", side_effect=RedisError):
        assert not priority_queue.clear()

    # Test Redis error during get_all
    with patch.object(priority_queue.connection_manager, "execute", side_effect=RedisError):
        assert priority_queue.get_all() == []
