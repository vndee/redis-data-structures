import pytest

from redis_data_structures import RingBuffer


@pytest.fixture
def ring_buffer() -> RingBuffer:
    """Create a RingBuffer instance for testing."""
    buffer = RingBuffer("test_ring_buffer", capacity=3)
    buffer.clear()
    yield buffer
    buffer.clear()


def test_push_within_capacity(ring_buffer):
    """Test pushing items within buffer capacity."""
    assert ring_buffer.push("item1")
    assert ring_buffer.push("item2")
    assert ring_buffer.size() == 2

    items = ring_buffer.get_all()
    assert items == ["item1", "item2"]


def test_push_beyond_capacity(ring_buffer):
    """Test pushing items beyond buffer capacity."""
    assert ring_buffer.push("item1")
    assert ring_buffer.push("item2")
    assert ring_buffer.push("item3")
    assert ring_buffer.push("item4")  # Should overwrite item1

    assert ring_buffer.size() == 3
    items = ring_buffer.get_all()
    assert items == ["item2", "item3", "item4"]


def test_get_latest(ring_buffer):
    """Test getting latest items."""
    assert ring_buffer.push("item1")
    assert ring_buffer.push("item2")
    assert ring_buffer.push("item3")

    # Test getting latest item
    latest = ring_buffer.get_latest()
    assert latest == ["item3"]

    # Test getting latest 2 items
    latest = ring_buffer.get_latest(2)
    assert latest == ["item3", "item2"]

    # Test getting more items than available
    latest = ring_buffer.get_latest(5)
    assert latest == ["item3", "item2", "item1"]


def test_clear(ring_buffer):
    """Test clearing buffer."""
    assert ring_buffer.push("item1")
    assert ring_buffer.push("item2")

    # Test clearing buffer
    assert ring_buffer.clear()
    assert ring_buffer.size() == 0
    assert ring_buffer.get_all() == []


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
        ring_buffer.clear()
        assert ring_buffer.push(data)
        items = ring_buffer.get_all()
        assert items == [data]


def test_concurrent_wrapping(ring_buffer):
    """Test that buffer correctly wraps around multiple times."""
    for i in range(10):  # Push more items than capacity
        assert ring_buffer.push(f"item{i}")

    # Should only contain the last 3 items
    items = ring_buffer.get_all()
    assert len(items) == 3
    assert items == ["item7", "item8", "item9"]


def test_empty_buffer(ring_buffer):
    """Test operations on empty buffer."""
    assert ring_buffer.size() == 0
    assert ring_buffer.get_all() == []
    assert ring_buffer.get_latest() == []
    assert ring_buffer.get_latest(5) == []
