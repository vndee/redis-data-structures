import pytest
from redis.exceptions import RedisError
from redis_data_structures import Dict

from unittest.mock import patch


@pytest.fixture
def dict_instance(connection_manager) -> Dict:
    """Create a Dict instance for testing."""
    d = Dict("test_dict")
    d.clear()
    yield d
    d.clear()

def test_set_and_get(dict_instance):
    dict_instance.set("key1", "value1")
    dict_instance.set("key2", "value2")

    assert dict_instance.get("key1") == "value1"
    assert dict_instance.get("key2") == "value2"

def test_get_nonexistent(dict_instance):
    assert dict_instance.get("nonexistent") is None

def test_set_update(dict_instance):
    dict_instance.set("key1", "value1")
    dict_instance.set("key1", "new_value")

    assert dict_instance.get("key1") == "new_value"

def test_delete(dict_instance):
    dict_instance.set("key1", "value1")
    assert dict_instance.delete("key1")
    assert dict_instance.get("key1") is None

def test_delete_nonexistent(dict_instance):
    assert not dict_instance.delete("nonexistent")

def test_keys(dict_instance):
    dict_instance.set("key1", "value1")
    dict_instance.set("key2", "value2")
    assert set(dict_instance.keys()) == {"key1", "key2"}

def test_values(dict_instance):
    dict_instance.set("key1", "value1")
    dict_instance.set("key2", "value2")
    assert set(dict_instance.values()) == {"value1", "value2"}

def test_items(dict_instance):
    dict_instance.set("key1", "value1")
    dict_instance.set("key2", "value2")
    assert set(dict_instance.items()) == {("key1", "value1"), ("key2", "value2")}

def test_clear(dict_instance):
    dict_instance.set("key1", "value1")
    dict_instance.set("key2", "value2")
    dict_instance.clear()
    assert dict_instance.size() == 0
    assert dict_instance.items() == []

def test_exists(dict_instance):
    assert not dict_instance.exists("key1")
    dict_instance.set("key1", "value1")
    assert dict_instance.exists("key1")
    dict_instance.delete("key1")
    assert not dict_instance.exists("key1")

def test_complex_data_types(dict_instance):
    test_data = {
        "dict_field": {"key": "value"},
        "list_field": [1, 2, 3],
        "set_field": {1, 2, 3},
        "tuple_field": (1, 2, 3),
    }

    for field, value in test_data.items():
        dict_instance.set(field, value)

    for field, value in test_data.items():
        assert dict_instance.get(field) == value

def test_none_value(dict_instance):
    assert dict_instance.set("null_field", None)
    assert dict_instance.get("null_field") is None

def test_empty_string(dict_instance):
    assert dict_instance.set("empty_field", "")
    assert dict_instance.get("empty_field") == ""

def test_unicode_strings(dict_instance):
    test_data = {
        "unicode_field1": "你好",  # Chinese
        "unicode_field2": "안녕하세요",  # Korean
        "unicode_field3": "Привет",  # Russian
        "unicode_field4": "🌟🎉🎈",  # Emojis
    }

    for field, value in test_data.items():
        assert dict_instance.set(field, value)
        assert dict_instance.get(field) == value

def test_special_characters(dict_instance):
    special_key = "spécial_key_!@#$%^&*()"
    special_value = "value_with_special_chars_!@#$%^&*()"
    dict_instance.set(special_key, special_value)
    assert dict_instance.get(special_key) == special_value

def test_concurrent_access(dict_instance):
    import threading

    def add_items():
        for i in range(5):
            dict_instance.set(f"key_{i}", f"value_{i}")

    threads = [threading.Thread(target=add_items) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    for i in range(5):
        assert dict_instance.get(f"key_{i}") == f"value_{i}" 