import json
from datetime import datetime, timedelta, timezone
from typing import List
from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from redis_data_structures.base import RedisDataStructure
from redis_data_structures.config import Config
from redis_data_structures.connection import ConnectionManager
from redis_data_structures.serializer import SerializableType


class User(SerializableType):
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

        class InvalidCustomType(SerializableType):
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

    def test_manual_type_registration(self):
        """Test manual registration of type handlers."""

        # Custom type for testing
        class Point:
            def __init__(self, x: float, y: float):
                self.x = x
                self.y = y

            def __eq__(self, other):
                if not isinstance(other, Point):
                    return False
                return self.x == other.x and self.y == other.y

        # Register type handlers
        self.rds.serializer.type_handlers["Point"] = {
            "serialize": lambda p: {"_type": "Point", "value": {"x": p.x, "y": p.y}},
            "deserialize": lambda d: Point(d["value"]["x"], d["value"]["y"]),
        }

        # Test serialization/deserialization with registered type
        point = Point(1.5, 2.5)
        serialized = self.rds.serializer.serialize(point)
        deserialized = self.rds.serializer.deserialize(serialized)

        assert isinstance(deserialized, Point)
        assert deserialized == point
        assert deserialized.x == 1.5
        assert deserialized.y == 2.5

    def test_manual_type_registration_override(self):
        """Test overriding existing type handlers."""

        # Custom serialization for datetime that only keeps date part
        def date_only_serializer(dt):
            return {"_type": "datetime", "value": dt.date().isoformat()}

        def date_only_deserializer(data):
            return datetime.fromisoformat(data["value"])

        # Store original handlers
        original_handlers = self.rds.serializer.type_handlers["datetime"]

        try:
            # Override datetime handlers
            self.rds.serializer.type_handlers["datetime"] = {
                "serialize": date_only_serializer,
                "deserialize": date_only_deserializer,
            }

            # Test with new handlers
            dt = datetime(2023, 1, 1, 12, 30, 45, tzinfo=timezone.utc)
            serialized = self.rds.serializer.serialize(dt)
            deserialized = self.rds.serializer.deserialize(serialized)

            # Should only preserve the date part
            assert deserialized.date() == dt.date()
            assert deserialized.hour == 0
            assert deserialized.minute == 0
            assert deserialized.second == 0
        finally:
            # Restore original handlers
            self.rds.serializer.type_handlers["datetime"] = original_handlers

    def test_manual_type_registration_via_base_model(self):
        class Point(BaseModel):
            x: float
            y: float

        self.rds.register_types(Point)

        point = Point(x=1.5, y=2.5)
        serialized = self.rds.serializer.serialize(point)
        deserialized = self.rds.serializer.deserialize(serialized)
        assert deserialized == point

        class Point2(SerializableType):
            def __init__(self, x: float, y: float):
                self.x = x
                self.y = y

            def to_dict(self) -> dict:
                return {"x": self.x, "y": self.y}

            @classmethod
            def from_dict(cls, data: dict) -> "Point2":
                return cls(data["x"], data["y"])

        self.rds.register_types(Point2)
        point2 = Point2(x=1.5, y=2.5)
        serialized = self.rds.serializer.serialize(point2)
        deserialized = self.rds.serializer.deserialize(serialized)
        assert deserialized == point2

    def test_get_registered_types(self):
        """Test getting registered types."""

        class Location(BaseModel):
            name: str
            country: str

        class Address(BaseModel):
            street: str
            city: str
            state: str
            zip_code: str
            location: Location

        class Person(BaseModel):
            name: str
            age: int
            address: Address

        class Company(BaseModel):
            name: str
            employees: List[Person]

        self.rds.register_types(Location)
        self.rds.register_types([Address, Person, Company])

        company = Company(
            name="Test Company",
            employees=[
                Person(
                    name="John Doe",
                    age=30,
                    address=Address(
                        street="123 Main St",
                        city="Anytown",
                        state="CA",
                        zip_code="12345",
                        location=Location(name="Home", country="USA"),
                    ),
                ),
                Person(
                    name="Jane Smith",
                    age=25,
                    address=Address(
                        street="456 Elm St",
                        city="Othertown",
                        state="NY",
                        zip_code="67890",
                        location=Location(name="Work", country="USA"),
                    ),
                ),
                Person(
                    name="Alice Johnson",
                    age=35,
                    address=Address(
                        street="789 Oak St",
                        city="Smalltown",
                        state="TX",
                        zip_code="11223",
                        location=Location(name="Home", country="USA"),
                    ),
                ),
            ],
        )

        serialized = self.rds.serializer.serialize(company)
        deserialized = self.rds.serializer.deserialize(serialized)
        assert deserialized == company

        class CustomType1(SerializableType):
            def __init__(self, name: str):
                self.name = name

            def to_dict(self) -> dict:
                return {"name": self.name}

            @classmethod
            def from_dict(cls, data: dict) -> "CustomType1":
                return cls(data["name"])

        self.rds.register_types(CustomType1)
        custom_type = CustomType1(name="Test")
        serialized = self.rds.serializer.serialize(custom_type)
        deserialized = self.rds.serializer.deserialize(serialized)
        assert deserialized == custom_type
