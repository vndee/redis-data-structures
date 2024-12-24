import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from redis_data_structures.base import CustomRedisDataType, RedisDataStructure
from redis_data_structures.config import Config
from redis_data_structures.connection import ConnectionManager
from redis_data_structures.exceptions import SerializationError


class User(CustomRedisDataType):
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def to_dict(self) -> dict:
        return {"name": self.name, "age": self.age}

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(data["name"], data["age"])

    def __eq__(self, other):
        return isinstance(other, User) and self.name == other.name and self.age == other.age
    
    def __str__(self) -> str:
        return f"User(name={self.name}, age={self.age})"


class TestRedisDataStructure:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup a RedisDataStructure instance for testing."""
        self.config = Config.from_env()
        mock_connection = Mock(spec=ConnectionManager)
        mock_connection.execute.return_value = True
        self.rds = RedisDataStructure(config=self.config, connection_manager=mock_connection)

    def test_serialize_custom_type(self):
        """Test serialization of a custom type."""
        user = User("Alice", 30)
        serialized_user = self.rds.serialize(user)
        serialized_user = json.loads(serialized_user)
        assert serialized_user is not None
        assert serialized_user["_type"] == "User"
        assert serialized_user["value"]["name"] == "Alice"
        assert serialized_user["value"]["age"] == 30

    def test_deserialize_custom_type(self):
        """Test deserialization of a custom type."""
        user_data = {
            "_type": "User",
            "module": "tests.test_base",
            "value": {"name": "Bob", "age": 25},
        }
        deserialized_user = self.rds.deserialize_value(user_data)
        assert isinstance(deserialized_user, User)
        assert deserialized_user.name == "Bob"
        assert deserialized_user.age == 25

    def test_serialize_dict(self):
        """Test serialization of a dictionary."""
        data = {"key1": "value1", "key2": 42}
        serialized_data = self.rds.serialize(data)
        serialized_data = json.loads(serialized_data)
        assert serialized_data is not None
        assert serialized_data["_type"] == "dict"

    def test_deserialize_dict(self):
        """Test deserialization of a dictionary."""
        data = {"_type": "dict", "value": {"key1": "value1", "key2": 42}}
        deserialized_data = self.rds.deserialize_value(data)
        assert deserialized_data == {"key1": "value1", "key2": 42}

    def test_serialize_list(self):
        """Test serialization of a list."""
        data = [1, 2, 3, "four"]
        serialized_data = self.rds.serialize(data)
        serialized_data = json.loads(serialized_data)
        assert serialized_data is not None
        assert serialized_data["_type"] == "list"

    def test_deserialize_list(self):
        """Test deserialization of a list."""
        data = {"_type": "list", "value": [1, 2, 3, "four"]}
        deserialized_data = self.rds.deserialize_value(data)
        assert deserialized_data == [1, 2, 3, "four"]

    def test_serialize_with_compression(self):
        """Test serialization with compression enabled."""
        config = Config.from_env()
        config.data_structures.compression_enabled = True
        config.data_structures.compression_threshold = 10
        mock_connection = Mock(spec=ConnectionManager)
        rds = RedisDataStructure(config=config, connection_manager=mock_connection)

        # Create a large string that will trigger compression
        large_data = "x" * 1000
        serialized = rds.serialize(large_data)
        assert isinstance(serialized, bytes)  # Compressed data should be bytes

        # Verify we can deserialize it back
        deserialized = rds.deserialize(serialized)
        assert deserialized == large_data

    def test_serialize_without_timestamp(self):
        """Test serialization without timestamp."""
        data = "test"
        serialized = self.rds.serialize(data, include_timestamp=False)
        parsed = json.loads(serialized)
        assert "timestamp" not in parsed

    def test_deserialize_empty_data(self):
        """Test deserialization of empty data."""
        assert self.rds.deserialize("") is None

    def test_deserialize_invalid_json(self):
        """Test deserialization of invalid JSON."""
        with pytest.raises(SerializationError):
            self.rds.deserialize("invalid json")

    def test_serialize_datetime(self):
        """Test serialization of datetime objects."""
        now = datetime.now(timezone.utc)
        serialized = self.rds.serialize(now)
        deserialized = self.rds.deserialize(serialized)
        assert isinstance(deserialized, datetime)
        assert deserialized.timestamp() == pytest.approx(now.timestamp())

    def test_serialize_timedelta(self):
        """Test serialization of timedelta objects."""
        delta = timedelta(days=1, hours=2, minutes=3)
        serialized = self.rds.serialize(delta)
        deserialized = self.rds.deserialize(serialized)
        assert isinstance(deserialized, timedelta)
        assert deserialized.total_seconds() == delta.total_seconds()

    def test_serialize_bytes(self):
        """Test serialization of bytes objects."""
        data = bytes([1, 2, 3, 4])
        serialized = self.rds.serialize(data)
        deserialized = self.rds.deserialize(serialized)
        assert isinstance(deserialized, bytes)
        assert deserialized == data

    def test_serialize_set(self):
        """Test serialization of set objects."""
        data = {1, "two", 3}  # Simplified set with hashable values
        serialized = self.rds.serialize(data, include_timestamp=False)
        deserialized = self.rds.deserialize(serialized)
        assert isinstance(deserialized, set)
        assert deserialized == data

    def test_serialize_tuple(self):
        """Test serialization of tuple objects."""
        data = (1, 2, "three")
        serialized = self.rds.serialize(data)
        deserialized = self.rds.deserialize(serialized)
        assert isinstance(deserialized, tuple)
        assert deserialized == data

    def test_ttl_operations(self):
        """Test TTL-related operations."""
        # Mock is already set up in setup()
        self.rds.connection_manager.execute.return_value = 100  # Mock TTL value

        key = "test_key"
        # Set TTL with integer
        assert self.rds.set_ttl(key, 100)

        # Set TTL with timedelta
        assert self.rds.set_ttl(key, timedelta(seconds=100))

        # Get TTL
        ttl = self.rds.get_ttl(key)
        assert isinstance(ttl, int)
        assert ttl == 100

        # Persist key
        assert self.rds.persist(key)

        # Verify correct Redis calls
        self.rds.connection_manager.execute.assert_called()

    def test_error_handling(self):
        """Test error handling in various operations."""

        # Test serialization error
        class UnserializableObject:
            def __repr__(self):
                raise Exception("Cannot serialize")

        with pytest.raises(SerializationError):
            self.rds.serialize(UnserializableObject())

        # Test deserialization of unknown type
        unknown_type_data = {"_type": "UnknownType", "module": "unknown_module", "value": {}}
        result = self.rds.deserialize_value(unknown_type_data)
        assert result == {}

    def test_custom_type_without_implementation(self):
        """Test custom type without required implementations."""

        class InvalidCustomType(CustomRedisDataType):
            pass

        invalid_type = InvalidCustomType()
        with pytest.raises(NotImplementedError):
            invalid_type.to_dict()
        with pytest.raises(NotImplementedError):
            InvalidCustomType.from_dict({})

    def test_clear_operation(self):
        """Test clear operation."""
        self.rds.connection_manager.execute.return_value = 1
        assert self.rds.clear("test_key") is True
        self.rds.connection_manager.execute.assert_called_with(
            "delete",
            self.rds._get_key("test_key"),
        )

    def test_connection_close(self):
        """Test connection close."""
        self.rds.close()
        self.rds.connection_manager.close.assert_called_once()

    def test_redis_error_handling(self):
        """Test Redis error handling."""
        # Test TTL error handling
        self.rds.connection_manager.execute.side_effect = Exception("Redis error")
        assert self.rds.set_ttl("key", 100) is False
        assert self.rds.get_ttl("key") is None
        assert self.rds.persist("key") is False
        assert self.rds.clear("key") is False
