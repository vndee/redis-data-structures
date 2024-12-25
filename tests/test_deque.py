from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures import Deque


@pytest.fixture
def deque() -> "Deque":
    """Create a Deque instance for testing."""
    dq = Deque("test_deque")
    dq.clear()
    yield dq
    dq.clear()
    dq.close()


@pytest.mark.unit
def test_push_front_and_pop_front(deque):
    # Test push_front and pop_front operations
    deque.push_front("item1")
    deque.push_front("item2")

    assert deque.size() == 2
    assert deque.pop_front() == "item2"
    assert deque.pop_front() == "item1"


def test_push_back_and_pop_back(deque):
    # Test push_back and pop_back operations
    deque.push_back("item1")
    deque.push_back("item2")

    assert deque.size() == 2
    assert deque.pop_back() == "item2"
    assert deque.pop_back() == "item1"


def test_mixed_operations(deque):
    # Test mixing front and back operations
    deque.push_front("front1")
    deque.push_back("back1")
    deque.push_front("front2")
    deque.push_back("back2")

    assert deque.size() == 4
    assert deque.pop_front() == "front2"
    assert deque.pop_back() == "back2"
    assert deque.pop_front() == "front1"
    assert deque.pop_back() == "back1"


def test_pop_empty(deque):
    # Test popping from empty deque
    assert deque.pop_front() is None
    assert deque.pop_back() is None


def test_size(deque):
    # Test size operations
    assert deque.size() == 0

    deque.push_front("item1")
    assert deque.size() == 1

    deque.push_back("item2")
    assert deque.size() == 2

    deque.pop_front()
    assert deque.size() == 1


def test_clear(deque):
    # Test clear operation
    deque.push_front("item1")
    deque.push_back("item2")

    deque.clear()
    assert deque.size() == 0


def test_alternating_operations(deque):
    # Test alternating push and pop operations
    deque.push_front("item1")
    assert deque.pop_back() == "item1"

    deque.push_back("item2")
    assert deque.pop_front() == "item2"


def test_peek_operations(deque):
    # Test peek operations
    assert deque.peek_front() is None
    assert deque.peek_back() is None

    deque.push_front("item1")
    deque.push_front("item2")

    assert deque.peek_front() == "item2"
    assert deque.peek_back() == "item1"
    assert deque.size() == 2  # Verify peeks don't remove items


def test_complex_data_types(deque):
    # Test with complex data types
    test_dict = {"key": "value", "nested": {"data": True}}
    test_list = [1, 2, [3, 4]]

    deque.push_front(test_dict)
    deque.push_back(test_list)

    assert deque.pop_front() == test_dict
    assert deque.pop_back() == test_list


def test_push_front_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.push_front("data") is False


def test_push_back_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.push_back("data") is False


def test_pop_front_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.pop_front() is None


def test_pop_back_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.pop_back() is None


def test_peek_front_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.peek_front() is None


def test_peek_back_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.peek_back() is None


def test_size_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.size() == 0
