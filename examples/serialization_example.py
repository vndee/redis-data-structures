import uuid
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel

from redis_data_structures.serializer import SerializableType, Serializer

if __name__ == "__main__":
    serializer = Serializer()
    print(serializer.serialize(1))
    print(serializer.serialize([1, 2, 3, {"a": 1, "b": 2, "c": [b"hello", {1, 2, 3}]}]))
    print(serializer.serialize({"a": 1, "b": 2, "c": 3}))
    print(serializer.serialize(datetime.now(timezone.utc)))
    print(serializer.serialize(timedelta(seconds=10)))
    print(serializer.serialize(b"hello"))

    print("-" * 100)
    print(serializer.deserialize(serializer.serialize(1)))
    print(serializer.deserialize(serializer.serialize([1, 2, 3])))
    print(
        serializer.deserialize(
            serializer.serialize([1, 2, 3, {"a": 1, "b": 2, "c": [b"hello", {1, 2, 3}]}]),
        ),
    )
    print(serializer.deserialize(serializer.serialize({"a": 1, "b": 2, "c": 3})))
    print(serializer.deserialize(serializer.serialize(datetime.now(timezone.utc))))
    print(serializer.deserialize(serializer.serialize(timedelta(seconds=10))))
    print(serializer.deserialize(serializer.serialize(b"hello")))
    print(serializer.deserialize(b'{"_type": "int", "value": 1}'))
    print(serializer.deserialize(serializer.serialize(uuid.uuid4())))

    print("-" * 100)

    class Address(BaseModel):
        """An address with a street, city, state, and zipcode."""

        street: str
        city: str
        state: str
        zip: str

    class User(BaseModel):
        """A user with a name, age, joined date, and address."""

        name: str
        age: int
        joined: datetime
        address: Address

    print(
        serializer.serialize(
            User(
                name="John",
                age=30,
                joined=datetime.now(timezone.utc),
                address=Address(street="123 Main St", city="Anytown", state="CA", zip="12345"),
            ),
        ),
    )
    print(
        serializer.deserialize(
            serializer.serialize(
                User(
                    name="John",
                    age=30,
                    joined=datetime.now(timezone.utc),
                    address=Address(street="123 Main St", city="Anytown", state="CA", zip="12345"),
                ),
            ),
        ),
    )

    print("-" * 100)

    class Address(SerializableType):
        """An address with a street, city, state, and zipcode."""

        def __init__(self, street: str, city: str, state: str, zipcode: str):
            """Initialize an Address."""
            self.street = street
            self.city = city
            self.state = state
            self.zipcode = zipcode

        def to_dict(self) -> dict:
            """Serialize an Address to a dictionary."""
            return {
                "street": self.street,
                "city": self.city,
                "state": self.state,
                "zipcode": self.zipcode,
            }

        @classmethod
        def from_dict(cls, data: dict) -> "Address":
            """Deserialize an Address from a dictionary."""
            return cls(data["street"], data["city"], data["state"], data["zipcode"])

        def print_address(self):
            """Print the address."""
            print(f"{self.street}, {self.city}, {self.state} {self.zipcode}")

    class User(SerializableType):
        """A user with an address."""

        def __init__(self, name: str, age: int, joined: datetime, address: Address):
            """Initialize a User."""
            self.name = name
            self.age = age
            self.joined = joined
            self.address = address

        def to_dict(self) -> dict:
            """Serialize a User to a dictionary."""
            return {
                "name": self.name,
                "age": self.age,
                "joined": self.joined.isoformat(),
                "address": self.address.to_dict(),
            }

        @classmethod
        def from_dict(cls, data: dict) -> "User":
            """Deserialize a User from a dictionary."""
            return cls(
                data["name"],
                data["age"],
                datetime.fromisoformat(data["joined"]),
                Address.from_dict(data["address"]),
            )

        def print_user(self):
            """Print the user's information."""
            print(
                f"{self.name} is {self.age} years old and lives at {self.address.street}, "
                f"{self.address.city}, {self.address.state} {self.address.zipcode}",
            )

    print(
        serializer.serialize(
            Address(street="123 Main St", city="Anytown", state="CA", zipcode="12345"),
        ),
    )
    print(
        serializer.deserialize(
            serializer.serialize(
                Address(street="123 Main St", city="Anytown", state="CA", zipcode="12345"),
            ),
        ),
    )
    serializer.deserialize(
        serializer.serialize(
            Address(street="123 Main St", city="Anytown", state="CA", zipcode="12345"),
        ),
    ).print_address()

    print("-" * 100)

    print(
        serializer.serialize(
            User(
                name="John",
                age=30,
                joined=datetime.now(timezone.utc),
                address=Address(street="123 Main St", city="Anytown", state="CA", zipcode="12345"),
            ),
        ),
    )
    print(
        serializer.deserialize(
            serializer.serialize(
                User(
                    name="John",
                    age=30,
                    joined=datetime.now(timezone.utc),
                    address=Address(
                        street="123 Main St",
                        city="Anytown",
                        state="CA",
                        zipcode="12345",
                    ),
                ),
            ),
        ),
    )
    serializer.deserialize(
        serializer.serialize(
            User(
                name="John",
                age=30,
                joined=datetime.now(timezone.utc),
                address=Address(street="123 Main St", city="Anytown", state="CA", zipcode="12345"),
            ),
        ),
    ).print_user()
