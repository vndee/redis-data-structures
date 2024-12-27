import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from redis_data_structures.base import RedisDataStructure
from redis_data_structures.config import Config
from redis_data_structures.connection import ConnectionManager
from redis_data_structures.serializer import CustomRedisDataType


class User(CustomRedisDataType):
    """User class for testing."""

    def __init__(self, name: str, age: int):
        """Initialize a User object."""
        self.name = name
        self.age = age

    def to_dict(self) -> dict:
        """Convert User object to a dictionary."""
        return {"name": self.name, "age": self.age}

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(data["name"], data["age"])

    def __eq__(self, other):
        """Check if two User objects are equal."""
        return isinstance(other, User) and self.name == other.name and self.age == other.age

    def __str__(self) -> str:
        """Return a string representation of the User object."""
        return f"User(name={self.name}, age={self.age})"


class TestRedisDataStructure:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup a RedisDataStructure instance for testing."""
        self.config = Config.from_env()
        mock_connection = Mock(spec=ConnectionManager)
        mock_connection.execute.return_value = True
        self.rds = RedisDataStructure(
            key="test_key",
            config=self.config,
            connection_manager=mock_connection,
        )

    def test_serialize_custom_type(self):
        """Test serialization of a custom type."""
        user = User("Alice", 30)
        serialized_user = self.rds.serializer.serialize(user)
        serialized_user = json.loads(serialized_user)
        assert serialized_user is not None
        assert serialized_user["_type"] == "User"
        assert serialized_user["value"]["name"] == "Alice"
        assert serialized_user["value"]["age"] == 30

    def test_deserialize_empty_data(self):
        """Test deserialization of empty data."""
        assert self.rds.serializer.deserialize("") is None

    def test_serialize_datetime(self):
        """Test serialization of datetime objects."""
        now = datetime.now(timezone.utc)
        serialized = self.rds.serializer.serialize(now)
        deserialized = self.rds.serializer.deserialize(serialized)
        assert isinstance(deserialized, datetime)
        assert deserialized.timestamp() == pytest.approx(now.timestamp())

    def test_serialize_timedelta(self):
        """Test serialization of timedelta objects."""
        delta = timedelta(days=1, hours=2, minutes=3)
        serialized = self.rds.serializer.serialize(delta)
        deserialized = self.rds.serializer.deserialize(serialized)
        assert isinstance(deserialized, timedelta)
        assert deserialized.total_seconds() == delta.total_seconds()

    def test_serialize_bytes(self):
        """Test serialization of bytes objects."""
        data = bytes([1, 2, 3, 4])
        serialized = self.rds.serializer.serialize(data)
        deserialized = self.rds.serializer.deserialize(serialized)
        assert isinstance(deserialized, bytes)
        assert deserialized == data

    def test_serialize_set(self):
        """Test serialization of set objects."""
        data = {1, "two", 3}  # Simplified set with hashable values
        serialized = self.rds.serializer.serialize(data)
        deserialized = self.rds.serializer.deserialize(serialized)
        assert isinstance(deserialized, set)
        assert deserialized == data

    def test_serialize_tuple(self):
        """Test serialization of tuple objects."""
        data = (1, 2, "three")
        serialized = self.rds.serializer.serialize(data)
        deserialized = self.rds.serializer.deserialize(serialized)
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
        assert self.rds.clear() is True
        self.rds.connection_manager.execute.assert_called_with(
            "delete",
            self.rds.key,
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
        assert self.rds.clear() is False
