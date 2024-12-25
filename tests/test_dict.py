import ast

import pytest

from redis_data_structures import Dict


@pytest.fixture
def dict_instance() -> Dict:
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


# Tests for Python special methods
def test_getitem(dict_instance):
    """Test dictionary-style access using []."""
    dict_instance.set("key1", "value1")
    assert dict_instance["key1"] == "value1"

    # Test accessing non-existent key
    with pytest.raises(KeyError):
        _ = dict_instance["nonexistent"]


def test_setitem(dict_instance):
    """Test dictionary-style assignment using []."""
    dict_instance["key1"] = "value1"
    assert dict_instance.get("key1") == "value1"

    # Test updating existing key
    dict_instance["key1"] = "new_value"
    assert dict_instance.get("key1") == "new_value"


def test_delitem(dict_instance):
    """Test dictionary-style deletion using del."""
    dict_instance["key1"] = "value1"
    del dict_instance["key1"]
    assert dict_instance.get("key1") is None

    # Test deleting non-existent key
    with pytest.raises(KeyError):
        del dict_instance["nonexistent"]


def test_iter(dict_instance):
    """Test dictionary iteration."""
    test_data = {"key1": "value1", "key2": "value2", "key3": "value3"}
    for key, value in test_data.items():
        dict_instance[key] = value

    # Test that iteration yields all keys
    assert set(iter(dict_instance)) == set(test_data.keys())

    # Test that iteration order matches keys()
    assert list(iter(dict_instance)) == dict_instance.keys()


def test_len(dict_instance):
    """Test len() function on dictionary."""
    assert len(dict_instance) == 0

    dict_instance["key1"] = "value1"
    assert len(dict_instance) == 1

    dict_instance["key2"] = "value2"
    assert len(dict_instance) == 2

    del dict_instance["key1"]
    assert len(dict_instance) == 1

    dict_instance.clear()
    assert len(dict_instance) == 0


def test_repr(dict_instance):
    """Test string representation of dictionary."""
    # Test empty dict
    assert repr(dict_instance) == "Dict(key=test_dict, items=[])"

    # Test with items
    dict_instance["key1"] = "value1"
    dict_instance["key2"] = "value2"

    # Since items() might return items in any order, we need to check both possibilities
    expected_items = {("key1", "value1"), ("key2", "value2")}
    actual_repr = repr(dict_instance)
    assert actual_repr.startswith("Dict(key=test_dict, items=")
    assert all(str(item) in actual_repr for item in expected_items)


def test_str(dict_instance):
    """Test string conversion of dictionary."""
    # Test empty dict
    assert str(dict_instance) == "{}"

    # Test with items
    dict_instance["key1"] = "value1"
    dict_instance["key2"] = "value2"

    # Convert string representation to dict and compare
    result = ast.literal_eval(str(dict_instance))
    assert isinstance(result, dict)
    assert result == {"key1": "value1", "key2": "value2"}


def test_contains(dict_instance):
    """Test 'in' operator."""
    dict_instance["key1"] = "value1"

    assert "key1" in dict_instance
    assert "nonexistent" not in dict_instance

    del dict_instance["key1"]
    assert "key1" not in dict_instance


def test_bool(dict_instance):
    """Test boolean evaluation."""
    # Empty dict should be False
    assert not bool(dict_instance)

    # Dict with items should be True
    dict_instance["key1"] = "value1"
    assert bool(dict_instance)

    # Dict should be False again after clearing
    dict_instance.clear()
    assert not bool(dict_instance)


def test_eq(dict_instance):
    """Test equality comparison."""
    # Create another Dict instance
    other_dict = Dict("test_dict_2")
    other_dict.clear()

    # Empty dicts should be equal
    assert dict_instance == other_dict

    # Dicts with same items should be equal
    dict_instance["key1"] = "value1"
    other_dict["key1"] = "value1"
    assert dict_instance == other_dict

    # Dicts with different items should not be equal
    other_dict["key2"] = "value2"
    assert dict_instance != other_dict

    # Clean up
    other_dict.clear()
