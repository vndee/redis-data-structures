from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures import HashMap


@pytest.fixture
def hash_map(connection_manager) -> HashMap:
    """Create a HashMap instance for testing."""
    hm = HashMap()
    test_key = "test_hash_map"
    hm.clear(test_key)
    yield hm
    hm.clear(test_key)
    hm.close()


def test_set_and_get(hash_map):
    # Test basic set and get operations
    hash_map.set("test_hash_map", "field1", "value1")
    hash_map.set("test_hash_map", "field2", "value2")

    assert hash_map.get("test_hash_map", "field1") == "value1"
    assert hash_map.get("test_hash_map", "field2") == "value2"


def test_get_nonexistent(hash_map):
    # Test getting non-existent field
    assert hash_map.get("test_hash_map", "nonexistent") is None


def test_set_update(hash_map):
    # Test updating existing field
    hash_map.set("test_hash_map", "field1", "value1")
    hash_map.set("test_hash_map", "field1", "new_value")

    assert hash_map.get("test_hash_map", "field1") == "new_value"


def test_delete(hash_map):
    # Test delete operation
    hash_map.set("test_hash_map", "field1", "value1")
    assert hash_map.delete("test_hash_map", "field1")
    assert hash_map.get("test_hash_map", "field1") is None


def test_delete_nonexistent(hash_map):
    # Test deleting non-existent field
    assert not hash_map.delete("test_hash_map", "nonexistent")


def test_get_all(hash_map):
    # Test getting all fields and values
    test_data = {"field1": "value1", "field2": "value2", "field3": "value3"}

    # Set each field with proper serialization
    for field, value in test_data.items():
        hash_map.set("test_hash_map", field, value)

    # Get all fields and compare with original data
    result = hash_map.get_all("test_hash_map")
    assert result == test_data


def test_size(hash_map):
    # Test size operations
    assert hash_map.size("test_hash_map") == 0

    hash_map.set("test_hash_map", "field1", "value1")
    assert hash_map.size("test_hash_map") == 1

    hash_map.set("test_hash_map", "field2", "value2")
    assert hash_map.size("test_hash_map") == 2

    # Updating existing field should not increase size
    hash_map.set("test_hash_map", "field1", "new_value")
    assert hash_map.size("test_hash_map") == 2


def test_clear(hash_map):
    # Test clear operation
    hash_map.set("test_hash_map", "field1", "value1")
    hash_map.set("test_hash_map", "field2", "value2")

    hash_map.clear("test_hash_map")
    assert hash_map.size("test_hash_map") == 0
    assert hash_map.get_all("test_hash_map") == {}


def test_complex_data_types(hash_map):
    # Test with complex data types
    test_dict = {"key": "value", "nested": {"data": True}}
    test_list = [1, 2, [3, 4]]
    test_datetime = datetime.now(tz=timezone.utc)
    test_set = {1, 2, 3}
    test_tuple = (1, "two", 3.0)

    test_data = {
        "dict_field": test_dict,
        "list_field": test_list,
        "datetime_field": test_datetime,
        "set_field": test_set,
        "tuple_field": test_tuple,
    }

    # Test setting complex types
    for field, value in test_data.items():
        assert hash_map.set("test_hash_map", field, value)

    # Test getting complex types
    for field, value in test_data.items():
        retrieved = hash_map.get("test_hash_map", field)
        if field == "datetime_field":
            # Compare datetime string representations due to microsecond precision
            assert retrieved.strftime("%Y-%m-%d %H:%M:%S") == value.strftime("%Y-%m-%d %H:%M:%S")
        elif field == "set_field":
            assert set(retrieved) == value
        elif field == "tuple_field":
            assert tuple(retrieved) == value
        else:
            assert retrieved == value


def test_exists(hash_map):
    # Test exists operation
    assert not hash_map.exists("test_hash_map", "field1")

    hash_map.set("test_hash_map", "field1", "value1")
    assert hash_map.exists("test_hash_map", "field1")

    hash_map.delete("test_hash_map", "field1")
    assert not hash_map.exists("test_hash_map", "field1")


def test_get_fields(hash_map):
    # Test get_fields operation
    test_data = {
        "field1": "value1",
        "field2": "value2",
        "field3": "value3",
    }

    for field, value in test_data.items():
        hash_map.set("test_hash_map", field, value)

    fields = hash_map.get_fields("test_hash_map")
    assert set(fields) == set(test_data.keys())


def test_empty_operations(hash_map):
    # Test operations on empty hash map
    assert hash_map.get_all("test_hash_map") == {}
    assert hash_map.get_fields("test_hash_map") == []
    assert hash_map.size("test_hash_map") == 0


def test_none_value(hash_map):
    # Test handling of None values
    assert hash_map.set("test_hash_map", "null_field", None)
    assert hash_map.get("test_hash_map", "null_field") is None


def test_empty_string(hash_map):
    # Test handling of empty strings
    assert hash_map.set("test_hash_map", "empty_field", "")
    assert hash_map.get("test_hash_map", "empty_field") == ""


def test_unicode_strings(hash_map):
    # Test handling of unicode strings
    test_data = {
        "unicode_field1": "你好",  # Chinese
        "unicode_field2": "안녕하세요",  # Korean
        "unicode_field3": "Привет",  # Russian
        "unicode_field4": "🌟🎉🎈",  # Emojis
    }

    for field, value in test_data.items():
        assert hash_map.set("test_hash_map", field, value)
        assert hash_map.get("test_hash_map", field) == value


# Error handling tests
def test_set_error_handling(hash_map):
    with patch.object(hash_map.connection_manager, "execute", side_effect=RedisError):
        assert not hash_map.set("test_hash_map", "field", "value")


def test_get_error_handling(hash_map):
    with patch.object(hash_map.connection_manager, "execute", side_effect=RedisError):
        assert hash_map.get("test_hash_map", "field") is None


def test_delete_error_handling(hash_map):
    with patch.object(hash_map.connection_manager, "execute", side_effect=RedisError):
        assert not hash_map.delete("test_hash_map", "field")


def test_exists_error_handling(hash_map):
    with patch.object(hash_map.connection_manager, "execute", side_effect=RedisError):
        assert not hash_map.exists("test_hash_map", "field")


def test_get_all_error_handling(hash_map):
    with patch.object(hash_map.connection_manager, "execute", side_effect=RedisError):
        assert hash_map.get_all("test_hash_map") == {}


def test_get_fields_error_handling(hash_map):
    with patch.object(hash_map.connection_manager, "execute", side_effect=RedisError):
        assert hash_map.get_fields("test_hash_map") == []


def test_size_error_handling(hash_map):
    with patch.object(hash_map.connection_manager, "execute", side_effect=RedisError):
        assert hash_map.size("test_hash_map") == 0


def test_clear_error_handling(hash_map):
    with patch.object(hash_map.connection_manager, "execute", side_effect=RedisError):
        assert not hash_map.clear("test_hash_map")


def test_set_and_get_large_data(hash_map):
    """Test setting and getting large data."""
    large_data = "x" * (10**6)  # 1 MB of data
    hash_map.set("test_hash_map", "large_field", large_data)
    assert hash_map.get("test_hash_map", "large_field") == large_data


def test_special_characters(hash_map):
    """Test handling of special characters in keys and values."""
    special_key = "spécial_key_!@#$%^&*()"
    special_value = "value_with_special_chars_!@#$%^&*()"
    hash_map.set("test_hash_map", special_key, special_value)
    assert hash_map.get("test_hash_map", special_key) == special_value


def test_nested_data_structures(hash_map):
    """Test handling of nested data structures."""
    nested_data = {"level1": {"level2": {"level3": "value"}}}
    hash_map.set("test_hash_map", "nested_field", nested_data)
    assert hash_map.get("test_hash_map", "nested_field") == nested_data


def test_clear_non_existent_key(hash_map):
    """Test clearing a non-existent key."""
    assert hash_map.clear("test_hash_map")  # Should not raise an error


def test_size_after_clearing(hash_map):
    """Test size after clearing the hash map."""
    hash_map.set("test_hash_map", "field1", "value1")
    assert hash_map.size("test_hash_map") == 1
    hash_map.clear("test_hash_map")
    assert hash_map.size("test_hash_map") == 0


def test_exists_with_special_characters(hash_map):
    """Test existence check with special characters in keys."""
    special_key = "spécial_key_!@#$%^&*()"
    hash_map.set("test_hash_map", special_key, "value")
    assert hash_map.exists("test_hash_map", special_key)
    hash_map.delete("test_hash_map", special_key)
    assert not hash_map.exists("test_hash_map", special_key)


def test_concurrent_access(hash_map):
    """Test hash map behavior under concurrent access (if applicable)."""
    import threading

    def add_items():
        for i in range(5):
            hash_map.set("test_hash_map", f"key_{i}", f"value_{i}")

    threads = [threading.Thread(target=add_items) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Check if all items were added
    for i in range(5):
        assert hash_map.get("test_hash_map", f"key_{i}") == f"value_{i}"


def test_get_all_items(hash_map):
    """Test getting all items from the hash map."""
    hash_map.set("test_hash_map", "key1", "value1")
    hash_map.set("test_hash_map", "key2", "value2")
    assert hash_map.get_all("test_hash_map") == {"key1": "value1", "key2": "value2"}


def test_get_all_deserialization_error_handling(hash_map):
    """Test error handling during deserialization in get_all operation."""
    # Mock the execute method to return a list of fields and values
    mock_data = [b"field1", b"value1", b"field2", b"value2"]

    with patch.object(hash_map.connection_manager, "execute", return_value=mock_data):
        with patch.object(hash_map, "deserialize", side_effect=Exception("Deserialization error")):
            result = hash_map.get_all("test_hash_map")
            assert result == {
                "field1": None,
                "field2": None,
            }  # Expect None for deserialization errors
