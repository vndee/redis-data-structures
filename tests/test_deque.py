from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures import Deque


@pytest.fixture
def deque(connection_manager) -> Deque:
    """Create a Deque instance for testing."""
    dq = Deque()
    test_key = "test_deque"
    dq.clear(test_key)
    yield dq
    dq.clear(test_key)
    dq.close()


@pytest.mark.unit
def test_push_front_and_pop_front(deque):
    # Test push_front and pop_front operations
    deque.push_front("test_deque", "item1")
    deque.push_front("test_deque", "item2")

    assert deque.size("test_deque") == 2
    assert deque.pop_front("test_deque") == "item2"
    assert deque.pop_front("test_deque") == "item1"


def test_push_back_and_pop_back(deque):
    # Test push_back and pop_back operations
    deque.push_back("test_deque", "item1")
    deque.push_back("test_deque", "item2")

    assert deque.size("test_deque") == 2
    assert deque.pop_back("test_deque") == "item2"
    assert deque.pop_back("test_deque") == "item1"


def test_mixed_operations(deque):
    # Test mixing front and back operations
    deque.push_front("test_deque", "front1")
    deque.push_back("test_deque", "back1")
    deque.push_front("test_deque", "front2")
    deque.push_back("test_deque", "back2")

    assert deque.size("test_deque") == 4
    assert deque.pop_front("test_deque") == "front2"
    assert deque.pop_back("test_deque") == "back2"
    assert deque.pop_front("test_deque") == "front1"
    assert deque.pop_back("test_deque") == "back1"


def test_pop_empty(deque):
    # Test popping from empty deque
    assert deque.pop_front("test_deque") is None
    assert deque.pop_back("test_deque") is None


def test_size(deque):
    # Test size operations
    assert deque.size("test_deque") == 0

    deque.push_front("test_deque", "item1")
    assert deque.size("test_deque") == 1

    deque.push_back("test_deque", "item2")
    assert deque.size("test_deque") == 2

    deque.pop_front("test_deque")
    assert deque.size("test_deque") == 1


def test_clear(deque):
    # Test clear operation
    deque.push_front("test_deque", "item1")
    deque.push_back("test_deque", "item2")

    deque.clear("test_deque")
    assert deque.size("test_deque") == 0


def test_alternating_operations(deque):
    # Test alternating push and pop operations
    deque.push_front("test_deque", "item1")
    assert deque.pop_back("test_deque") == "item1"

    deque.push_back("test_deque", "item2")
    assert deque.pop_front("test_deque") == "item2"


def test_peek_operations(deque):
    # Test peek operations
    assert deque.peek_front("test_deque") is None
    assert deque.peek_back("test_deque") is None

    deque.push_front("test_deque", "item1")
    deque.push_front("test_deque", "item2")

    assert deque.peek_front("test_deque") == "item2"
    assert deque.peek_back("test_deque") == "item1"
    assert deque.size("test_deque") == 2  # Verify peeks don't remove items


def test_complex_data_types(deque):
    # Test with complex data types
    test_dict = {"key": "value", "nested": {"data": True}}
    test_list = [1, 2, [3, 4]]

    deque.push_front("test_deque", test_dict)
    deque.push_back("test_deque", test_list)

    assert deque.pop_front("test_deque") == test_dict
    assert deque.pop_back("test_deque") == test_list


def test_push_front_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.push_front("test_deque", "data") is False


def test_push_back_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.push_back("test_deque", "data") is False


def test_pop_front_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.pop_front("test_deque") is None


def test_pop_back_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.pop_back("test_deque") is None


def test_peek_front_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.peek_front("test_deque") is None


def test_peek_back_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.peek_back("test_deque") is None


def test_size_error_handling(deque):
    with patch.object(deque.connection_manager, "execute", side_effect=RedisError):
        assert deque.size("test_deque") == 0
