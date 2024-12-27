from typing import Tuple

import pytest

from redis_data_structures.base import RedisDataStructure


class TestSerialization:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup a RedisDataStructure instance for testing."""
        self.rds = RedisDataStructure(key="test_key")

    def test_basic_tuple_serialization(self):
        """Test basic tuple serialization."""
        tuple_data: Tuple[int, str, list] = (1, "two", [3, 4])
        serialized_tuple = self.rds.serializer.serialize(tuple_data)
        assert serialized_tuple is not None  # Ensure serialization is successful

        # Test deserialization
        deserialized_tuple = self.rds.serializer.deserialize(serialized_tuple)
        assert deserialized_tuple == tuple_data, "Deserialized data doesn't match original"

    def test_empty_tuple_serialization(self):
        """Test serialization of an empty tuple."""
        tuple_data: Tuple = ()
        serialized_tuple = self.rds.serializer.serialize(tuple_data)
        assert serialized_tuple is not None

        deserialized_tuple = self.rds.serializer.deserialize(serialized_tuple)
        assert deserialized_tuple == tuple_data

    def test_nested_tuple_serialization(self):
        """Test serialization of a nested tuple."""
        tuple_data: Tuple = (1, (2, 3), [4, 5])
        serialized_tuple = self.rds.serializer.serialize(tuple_data)
        assert serialized_tuple is not None

        deserialized_tuple = self.rds.serializer.deserialize(serialized_tuple)
        assert deserialized_tuple == tuple_data

    def test_serialization_of_dict(self):
        """Test serialization of a dictionary."""
        dict_data = {"key1": "value1", "key2": [1, 2, 3]}
        serialized_dict = self.rds.serializer.serialize(dict_data)
        assert serialized_dict is not None

        deserialized_dict = self.rds.serializer.deserialize(serialized_dict)
        assert deserialized_dict == dict_data

    def test_serialization_of_list(self):
        """Test serialization of a list."""
        list_data = [1, 2, 3, "four"]
        serialized_list = self.rds.serializer.serialize(list_data)
        assert serialized_list is not None

        deserialized_list = self.rds.serializer.deserialize(serialized_list)
        assert deserialized_list == list_data
