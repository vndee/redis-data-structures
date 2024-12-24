import pytest
from unittest.mock import patch
from redis.exceptions import RedisError
from redis_data_structures import RingBuffer


@pytest.fixture
def ring_buffer(connection_manager) -> RingBuffer:
    """Create a RingBuffer instance for testing."""
    buffer = RingBuffer(capacity=3)
    test_key = "test_ring_buffer"
    buffer.clear(test_key)
    yield buffer
    buffer.clear(test_key)


def test_push_within_capacity(ring_buffer):
    """Test pushing items within buffer capacity."""
    assert ring_buffer.push("test_ring_buffer", "item1")
    assert ring_buffer.push("test_ring_buffer", "item2")
    assert ring_buffer.size("test_ring_buffer") == 2

    items = ring_buffer.get_all("test_ring_buffer")
    assert items == ["item1", "item2"]


def test_push_beyond_capacity(ring_buffer):
    """Test pushing items beyond buffer capacity."""
    assert ring_buffer.push("test_ring_buffer", "item1")
    assert ring_buffer.push("test_ring_buffer", "item2")
    assert ring_buffer.push("test_ring_buffer", "item3")
    assert ring_buffer.push("test_ring_buffer", "item4")  # Should overwrite item1

    assert ring_buffer.size("test_ring_buffer") == 3
    items = ring_buffer.get_all("test_ring_buffer")
    assert items == ["item2", "item3", "item4"]


def test_get_latest(ring_buffer):
    """Test getting latest items."""
    assert ring_buffer.push("test_ring_buffer", "item1")
    assert ring_buffer.push("test_ring_buffer", "item2")
    assert ring_buffer.push("test_ring_buffer", "item3")

    # Test getting latest item
    latest = ring_buffer.get_latest("test_ring_buffer")
    assert latest == ["item3"]

    # Test getting latest 2 items
    latest = ring_buffer.get_latest("test_ring_buffer", 2)
    assert latest == ["item3", "item2"]

    # Test getting more items than available
    latest = ring_buffer.get_latest("test_ring_buffer", 5)
    assert latest == ["item3", "item2", "item1"]


def test_clear(ring_buffer):
    """Test clearing buffer."""
    assert ring_buffer.push("test_ring_buffer", "item1")
    assert ring_buffer.push("test_ring_buffer", "item2")

    # Test clearing buffer
    assert ring_buffer.clear("test_ring_buffer")
    assert ring_buffer.size("test_ring_buffer") == 0
    assert ring_buffer.get_all("test_ring_buffer") == []


def test_complex_data_types(ring_buffer):
    """Test with different data types."""
    test_data = [
        42,  # integer
        3.14,  # float
        {"key": "value"},  # dict
        ["list", "of", "items"],  # list
        ("tuple", "items"),  # tuple
        {1, 2, 3},  # set
    ]

    for data in test_data:
        ring_buffer.clear("test_ring_buffer")
        assert ring_buffer.push("test_ring_buffer", data)
        items = ring_buffer.get_all("test_ring_buffer")
        assert items == [data]


def test_concurrent_wrapping(ring_buffer):
    """Test that buffer correctly wraps around multiple times."""
    for i in range(10):  # Push more items than capacity
        assert ring_buffer.push("test_ring_buffer", f"item{i}")

    # Should only contain the last 3 items
    items = ring_buffer.get_all("test_ring_buffer")
    assert len(items) == 3
    assert items == ["item7", "item8", "item9"]


def test_empty_buffer(ring_buffer):
    """Test operations on empty buffer."""
    assert ring_buffer.size("test_ring_buffer") == 0
    assert ring_buffer.get_all("test_ring_buffer") == []
    assert ring_buffer.get_latest("test_ring_buffer") == []
    assert ring_buffer.get_latest("test_ring_buffer", 5) == []


# Error handling tests
def test_push_error_handling(ring_buffer):
    """Test error handling during push operation."""
    with patch.object(ring_buffer.connection_manager, "pipeline", side_effect=RedisError):
        assert not ring_buffer.push("test_ring_buffer", "data")


def test_get_all_error_handling(ring_buffer):
    """Test error handling during get_all operation."""
    with patch.object(ring_buffer.connection_manager, "execute", side_effect=RedisError):
        assert ring_buffer.get_all("test_ring_buffer") == []


def test_get_latest_error_handling(ring_buffer):
    """Test error handling during get_latest operation."""
    with patch.object(ring_buffer.connection_manager, "execute", side_effect=RedisError):
        assert ring_buffer.get_latest("test_ring_buffer") == []


def test_size_error_handling(ring_buffer):
    """Test error handling during size operation."""
    with patch.object(ring_buffer.connection_manager, "execute", side_effect=RedisError):
        assert ring_buffer.size("test_ring_buffer") == 0


def test_clear_error_handling(ring_buffer):
    """Test error handling during clear operation."""
    with patch.object(ring_buffer.connection_manager, "pipeline", side_effect=RedisError):
        assert not ring_buffer.clear("test_ring_buffer")


def test_get_current_position(ring_buffer):
    """Test getting the current position of the ring buffer."""
    # Push items into the ring buffer
    assert ring_buffer.push("test_ring_buffer", "item1")
    assert ring_buffer.push("test_ring_buffer", "item2")
    
    # Check the current position after pushing two items
    assert ring_buffer.get_current_position("test_ring_buffer") == 2

    # Push one more item
    assert ring_buffer.push("test_ring_buffer", "item3")
    
    # Check the current position after pushing three items
    assert ring_buffer.get_current_position("test_ring_buffer") == 3

    # Clear the ring buffer
    ring_buffer.clear("test_ring_buffer")
    
    # Check the current position after clearing
    assert ring_buffer.get_current_position("test_ring_buffer") == 0


def test_get_current_position_error_handling(ring_buffer):
    """Test error handling during get_current_position operation."""
    with patch.object(ring_buffer.connection_manager, "execute", side_effect=RedisError):
        assert ring_buffer.get_current_position("test_ring_buffer") == 0
