import time
from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures import LRUCache


@pytest.fixture
def lru_cache() -> LRUCache:
    """Create an LRUCache instance for testing."""
    cache = LRUCache(capacity=3, key="test_lru_cache")
    cache.clear()
    yield cache
    cache.clear()


def test_put_and_get(lru_cache):
    # Test basic put and get operations
    assert lru_cache.put("key1", "value1")
    assert lru_cache.get("key1") == "value1"

    # Test getting non-existent item
    assert lru_cache.get("nonexistent") is None


def test_capacity_limit(lru_cache):
    # Test that cache respects capacity limit
    lru_cache.put("key1", "value1")
    lru_cache.put("key2", "value2")
    lru_cache.put("key3", "value3")

    # Verify size
    assert lru_cache.size() == 3

    # Add one more item, should evict least recently used
    lru_cache.put("key4", "value4")
    assert lru_cache.size() == 3
    assert lru_cache.get("key1") is None  # Should be evicted
    assert lru_cache.get("key4") == "value4"


def test_lru_eviction_order(lru_cache):
    # Test that items are evicted in LRU order
    lru_cache.put("key1", "value1")
    lru_cache.put("key2", "value2")
    lru_cache.put("key3", "value3")

    # Access key1, making key2 the least recently used
    lru_cache.get("key1")
    time.sleep(0.1)  # Ensure different timestamps
    lru_cache.get("key3")

    # Add new item, should evict key2
    lru_cache.put("key4", "value4")
    assert lru_cache.get("key2") is None  # Should be evicted
    assert lru_cache.get("key1") == "value1"
    assert lru_cache.get("key3") == "value3"
    assert lru_cache.get("key4") == "value4"


def test_peek(lru_cache):
    # Test peeking at values without updating access time
    lru_cache.put("key1", "value1")
    lru_cache.put("key2", "value2")

    # Peek at key1 (shouldn't update access time)
    assert lru_cache.peek("key1") == "value1"

    # Add item to full cache
    lru_cache.put("key3", "value3")
    lru_cache.put("key4", "value4")

    # key1 should be evicted since peek didn't update its access time
    assert lru_cache.get("key1") is None


def test_remove(lru_cache):
    # Test removing items from cache
    lru_cache.put("key1", "value1")
    lru_cache.put("key2", "value2")

    # Remove item
    assert lru_cache.remove("key1")
    assert lru_cache.get("key1") is None
    assert lru_cache.size() == 1

    # Try removing non-existent item
    assert not lru_cache.remove("nonexistent")


def test_clear(lru_cache):
    # Test clearing the cache
    lru_cache.put("key1", "value1")
    lru_cache.put("key2", "value2")

    # Clear cache
    assert lru_cache.clear()
    assert lru_cache.size() == 0
    assert lru_cache.get("key1") is None
    assert lru_cache.get("key2") is None


def test_get_all(lru_cache):
    # Test getting all items from cache
    items = {"key1": "value1", "key2": "value2", "key3": "value3"}
    for key, value in items.items():
        lru_cache.put(key, value)

    # Get all items
    cached_items = lru_cache.get_all()
    assert cached_items == items


def test_get_lru_order(lru_cache):
    # Test getting items in LRU order
    lru_cache.put("key1", "value1")
    time.sleep(0.1)  # Ensure different timestamps
    lru_cache.put("key2", "value2")
    time.sleep(0.1)
    lru_cache.put("key3", "value3")

    # Access items in specific order
    time.sleep(0.1)
    lru_cache.get("key1")  # Make key1 most recently used
    time.sleep(0.1)
    lru_cache.get("key2")  # Make key2 most recently used

    # Get LRU order
    order = lru_cache.get_lru_order()
    assert order[0] == "key3"  # Least recently used
    assert order[-1] == "key2"  # Most recently used


def test_complex_data_types(lru_cache):
    # Test cache with complex data types
    dict_value = {"name": "John", "age": 30}
    lru_cache.put("dict", dict_value)
    assert lru_cache.get("dict") == dict_value

    list_value = [1, 2, [3, 4]]
    lru_cache.put("list", list_value)
    assert lru_cache.get("list") == list_value

    tuple_value = (1, "two", [3])
    lru_cache.put("tuple", tuple_value)
    assert lru_cache.get("tuple") == tuple_value


def test_error_handling(lru_cache):
    # Test error handling
    with patch.object(lru_cache.connection_manager, "pipeline", side_effect=RedisError):
        assert not lru_cache.put("key", "value")

    with patch.object(lru_cache.connection_manager, "execute", side_effect=RedisError):
        assert lru_cache.get("key") is None

    with patch.object(lru_cache.connection_manager, "pipeline", side_effect=RedisError):
        assert not lru_cache.remove("key")

    with patch.object(lru_cache.connection_manager, "pipeline", side_effect=RedisError):
        assert not lru_cache.clear()


def test_update_existing(lru_cache):
    # Test updating existing cache entries
    lru_cache.put("key1", "value1")

    # Update with new value
    lru_cache.put("key1", "new_value")
    assert lru_cache.get("key1") == "new_value"
    assert lru_cache.size() == 1  # Size should remain same


def test_minimum_capacity():
    # Test that cache capacity cannot be less than 1
    cache = LRUCache("test_lru_cache", capacity=0)  # Should be set to 1
    assert cache.capacity == 1

    cache = LRUCache("test_lru_cache", capacity=-5)  # Should be set to 1
    assert cache.capacity == 1


def test_add_duplicate_key(lru_cache):
    """Test adding a duplicate key updates the value."""
    lru_cache.put("key1", "value1")
    assert lru_cache.get("key1") == "value1"

    # Update with a new value
    lru_cache.put("key1", "new_value")
    assert lru_cache.get("key1") == "new_value"


def test_cache_size_after_eviction(lru_cache):
    """Test cache size after eviction."""
    lru_cache.put("key1", "value1")
    lru_cache.put("key2", "value2")
    lru_cache.put("key3", "value3")
    assert lru_cache.size() == 3

    # Add one more item, should evict the least recently used
    lru_cache.put("key4", "value4")
    assert lru_cache.size() == 3  # Size should remain 3


def test_clear_empty_cache(lru_cache):
    """Test clearing an already empty cache."""
    assert lru_cache.clear()  # Should not raise an error
    assert lru_cache.size() == 0


def test_peek_non_existent_key(lru_cache):
    """Test peeking at a non-existent key."""
    assert lru_cache.peek("nonexistent") is None


def test_complex_data_types_handling(lru_cache):
    """Test cache with various complex data types."""
    complex_data = {
        "name": "Alice",
        "age": 30,
        "hobbies": ["reading", "hiking"],
        "address": {"city": "Wonderland", "zip": "12345"},
    }
    lru_cache.put("complex_data", complex_data)
    assert lru_cache.get("complex_data") == complex_data


def test_large_data_handling(lru_cache):
    """Test cache behavior with large data."""
    large_data = "x" * (10**6)  # 1 MB of data
    lru_cache.put("large_data", large_data)
    assert lru_cache.get("large_data") == large_data


def test_concurrent_access(lru_cache):
    """Test cache behavior under concurrent access."""
    import threading
    from queue import Queue

    # Use a queue to track successful operations
    results = Queue()

    # Adjust number of threads and items to stay within cache capacity (3)
    num_threads = 2

    def add_items(thread_id):
        try:
            key = f"key_{thread_id}"
            value = f"value_{thread_id}"
            if lru_cache.put(key, value):
                results.put((key, value))
                # Verify immediately after putting
                result = lru_cache.get(key)
                if result != value:
                    results.put(
                        Exception(
                            f"Immediate verification failed for {key}: expected {value}, "
                            f"got {result}",
                        ),
                    )
        except Exception as e:
            results.put(e)

    # Create and start threads
    threads = [threading.Thread(target=add_items, args=(i,)) for i in range(num_threads)]
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check results
    successful_operations = []
    while not results.empty():
        result = results.get()
        if isinstance(result, Exception):
            pytest.fail(f"Thread operation failed: {result}")
        successful_operations.append(result)

    # Verify that operations were successful
    assert len(successful_operations) > 0, "No successful operations recorded"
    assert len(successful_operations) <= lru_cache.capacity, "Too many items in cache"

    # Verify that we can retrieve the values
    for key, expected_value in successful_operations:
        actual_value = lru_cache.get(key)
        assert (
            actual_value == expected_value
        ), f"Value mismatch for key {key}: expected {expected_value}, got {actual_value}"

    # Verify the cache size is within capacity
    assert lru_cache.size() <= lru_cache.capacity


def test_put_exception_handling(lru_cache):
    """Test exception handling during put operation."""
    with patch.object(lru_cache.connection_manager, "pipeline", side_effect=RedisError):
        assert not lru_cache.put("key", "value")


def test_get_exception_handling(lru_cache):
    """Test exception handling during get operation."""
    with patch.object(lru_cache.connection_manager, "execute", side_effect=RedisError):
        assert lru_cache.get("key") is None


def test_remove_exception_handling(lru_cache):
    """Test exception handling during remove operation."""
    with patch.object(lru_cache.connection_manager, "pipeline", side_effect=RedisError):
        assert not lru_cache.remove("key")


def test_clear_exception_handling(lru_cache):
    """Test exception handling during clear operation."""
    with patch.object(lru_cache.connection_manager, "pipeline", side_effect=RedisError):
        assert not lru_cache.clear()


def test_peek_exception_handling(lru_cache):
    """Test exception handling during peek operation."""
    with patch.object(lru_cache.connection_manager, "execute", side_effect=RedisError):
        assert lru_cache.peek("key") is None


def test_get_lru_order_exception_handling(lru_cache):
    """Test exception handling during get_lru_order operation."""
    with patch.object(lru_cache.connection_manager, "execute", side_effect=RedisError):
        assert lru_cache.get_lru_order() == []


def test_size_exception_handling(lru_cache):
    """Test exception handling during size operation."""
    with patch.object(lru_cache.connection_manager, "execute", side_effect=RedisError):
        assert lru_cache.size() == 0


def test_get_all_items(lru_cache):
    """Test getting all items from the cache."""
    lru_cache.put("key1", "value1")
    lru_cache.put("key2", "value2")
    assert lru_cache.get_all() == {"key1": "value1", "key2": "value2"}
