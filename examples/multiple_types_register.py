from typing import List

from pydantic import BaseModel

from redis_data_structures import RedisDataStructure, SerializableType

if __name__ == "__main__":

    class Location(BaseModel):
        """Location model."""

        name: str
        country: str

    class Address(BaseModel):
        """Address model."""

        street: str
        city: str
        state: str
        zip_code: str
        location: Location

    class Person(BaseModel):
        """Person model."""

        name: str
        age: int
        address: Address

    class Company(BaseModel):
        """Company model."""

        name: str
        employees: List[Person]

    redis_ds = RedisDataStructure(key="test_key")
    redis_ds.register_types(Company)
    redis_ds.register_types([Person, Address, Location])

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

    serialized = redis_ds.serializer.serialize(company)
    print(serialized)

    deserialized = redis_ds.serializer.deserialize(serialized)
    print(deserialized)

    assert deserialized == company  # noqa: S101

    class CustomType1(SerializableType):
        """Custom type 1."""

        def __init__(self, name: str, value: int):
            """Initialize CustomType1."""
            self.name = name
            self.value = value

        def to_dict(self) -> dict:
            """Convert to dictionary."""
            return {"name": self.name, "value": self.value}

        @classmethod
        def from_dict(cls, data: dict) -> "CustomType1":
            """Create from dictionary."""
            return cls(data["name"], data["value"])

    class CustomType2(SerializableType):
        """Custom type 2."""

        def __init__(self, name: str, value: int):
            """Initialize CustomType2."""
            self.name = name
            self.value = value

        def to_dict(self) -> dict:
            """Convert to dictionary."""
            return {"name": self.name, "value": self.value}

        @classmethod
        def from_dict(cls, data: dict) -> "CustomType2":
            """Create from dictionary."""
            return cls(data["name"], data["value"])

    class CustomType3(SerializableType):
        """Custom type 3."""

        def __init__(self, name: str, value: int):
            """Initialize CustomType3."""
            self.name = name
            self.value = value

        def to_dict(self) -> dict:
            """Convert to dictionary."""
            return {"name": self.name, "value": self.value}

        @classmethod
        def from_dict(cls, data: dict) -> "CustomType3":
            """Create from dictionary."""
            return cls(data["name"], data["value"])

    redis_ds.register_types(CustomType1)
    redis_ds.register_types([CustomType1, CustomType2, CustomType3])
    print(redis_ds.serializer.get_registered_types())

    custom_type = CustomType1(name="Test", value=1)
    serialized = redis_ds.serializer.serialize(custom_type)
    deserialized = redis_ds.serializer.deserialize(serialized)
    print(deserialized == custom_type)
