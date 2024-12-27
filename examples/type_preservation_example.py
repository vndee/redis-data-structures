from datetime import datetime, timezone
from typing import Any, Optional, Set

from pydantic import BaseModel, Field

from redis_data_structures import HashMap, LRUCache, SerializableType


class User(SerializableType):
    """Example of a custom Redis data type using standard class."""

    def __init__(self, name: str, joined: datetime):
        """Initialize the User object."""
        self.name = name
        self.joined = joined

    def to_dict(self) -> dict:
        """Convert the User object to a dictionary."""
        return {
            "name": self.name,
            "joined": self.joined.isoformat(),  # Convert datetime to string
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create a User object from a dictionary."""
        return cls(
            name=data["name"],
            joined=datetime.fromisoformat(data["joined"]),  # Convert string back to datetime
        )

    def __str__(self) -> str:
        """Return a string representation of the User object."""
        return f"User(name='{self.name}', joined={self.joined.isoformat()})"


class Address(BaseModel):
    """Nested Pydantic model for demonstration."""

    street: str
    city: str
    country: str
    postal_code: Optional[str] = None


class UserModel(BaseModel):
    """Example of a Pydantic model - works automatically with Redis structures."""

    name: str
    email: str
    age: int = Field(gt=0, lt=150)
    joined: datetime
    address: Optional[Address] = None
    tags: Set[str] = set()

    def __str__(self) -> str:
        """Return a string representation of the UserModel instance."""
        return f"UserModel(name='{self.name}', email='{self.email}', age={self.age})"


def demonstrate_type_preservation():
    """Demonstrate type preservation across different Redis data structures."""
    # Initialize data structures
    cache = LRUCache("test_cache", capacity=1000)  # Using default connection settings
    hash_map = HashMap("test_hash")  # Using default connection settings

    # Clear any existing data
    cache.clear()
    hash_map.clear()

    print("=== Type Preservation Example ===")

    # Example 1: Basic Python Types
    print("\nBasic Type Preservation:")
    data = {
        "string": "hello",
        "integer": 42,
        "float": 3.14,
        "boolean": True,
        "none": None,
    }
    for key, value in data.items():
        hash_map.set(key, value)
        result = hash_map.get(key)
        print(f"{key}: {result} ({type(result).__name__})")

    # Example 2: Collections
    print("\nCollection Type Preservation:")
    collections = {
        "tuple": (1, "two", 3.0),
        "list": [1, 2, 3, "four"],
        "set": {1, 2, 3, 4},
        "dict": {"a": 1, "b": 2},
    }
    for key, value in collections.items():
        hash_map.set(key, value)
        result = hash_map.get(key)
        print(f"{key}: {result} ({type(result).__name__})")

    # Example 3: DateTime Types
    print("\nDateTime Type Preservation:")
    now = datetime.now(timezone.utc)
    hash_map.set("datetime", now)
    result = hash_map.get("datetime")
    print(f"Original: {now} ({type(now).__name__})")
    print(f"Retrieved: {result} ({type(result).__name__})")

    # Example 4: Custom Type
    print("\nCustom Type Preservation:")
    user = User("John Doe", datetime.now(timezone.utc))
    hash_map.set("custom_user", user)
    result = hash_map.get("custom_user")
    print(f"Original: {user}")
    print(f"Retrieved: {result}")

    # Example 5: Pydantic Models
    print("\nPydantic Model Preservation:")
    user_model = UserModel(
        name="Jane Smith",
        email="jane@example.com",
        age=30,
        joined=datetime.now(timezone.utc),
        address=Address(
            street="123 Main St",
            city="New York",
            country="USA",
            postal_code="10001",
        ),
        tags={"developer", "python"},
    )

    # Store in different data structures
    cache.put("pydantic_user", user_model)
    hash_map.set("pydantic_user", user_model)

    # Retrieve and verify
    cache_result = cache.get("pydantic_user")
    hash_result = hash_map.get("pydantic_user")

    print("\nOriginal Pydantic Model:")
    print_model_details(user_model)
    print("\nRetrieved from Cache:")
    print_model_details(cache_result)
    print("\nRetrieved from Hash:")
    print_model_details(hash_result)

    # Example 6: Nested Structures
    print("\nNested Structure Preservation:")
    nested_data = {
        "user": user,
        "model": user_model,
        "list": [1, user, user_model],
        "tuple": (user, user_model),
        "dict": {
            "user": user,
            "model": user_model,
            "date": now,
        },
    }
    hash_map.set("nested", nested_data)
    result = hash_map.get("nested")
    print("Original structure types:")
    print_nested_structure(nested_data)
    print("\nRetrieved structure types:")
    print_nested_structure(result)


def print_model_details(model: UserModel) -> None:
    """Print details of a UserModel instance."""
    print(f"  Name: {model.name}")
    print(f"  Email: {model.email}")
    print(f"  Age: {model.age}")
    print(f"  Joined: {model.joined}")
    if model.address:
        print(f"  Address: {model.address.street}, {model.address.city}")
    print(f"  Tags: {model.tags}")


def print_nested_structure(obj: Any, indent: int = 2) -> None:
    """Print the structure of nested objects with their types."""
    prefix = " " * indent
    if isinstance(obj, dict):
        print(f"{prefix}dict:")
        for key, value in obj.items():
            print(f"{prefix}{key}:")
            print_nested_structure(value, indent + 2)
    elif isinstance(obj, (list, tuple)):
        container_type = "list" if isinstance(obj, list) else "tuple"
        print(f"{prefix}{container_type}:")
        for item in obj:
            print_nested_structure(item, indent + 2)
    elif isinstance(obj, set):
        print(f"{prefix}set: {obj}")
    else:
        type_name = type(obj).__name__
        if isinstance(obj, (User, UserModel)):
            print(f"{prefix}{type_name}: {obj}")
        else:
            print(f"{prefix}{type_name}: {obj}")


def set_examples():
    """Demonstrate the usage of the Set data structure."""
    from datetime import datetime

    from redis_data_structures import Set

    set_ds = Set("users")

    # Any JSON-serializable object
    user = {
        "id": "user1",
        "name": "Alice",
        "joined": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": {"role": "admin"},
    }

    set_ds.add(user)

    # Custom types
    from redis_data_structures import SerializableType

    class User(SerializableType):
        id: str
        name: str
        joined: datetime
        metadata: dict

        def __init__(self, id: str, name: str, joined: datetime, metadata: dict):  # noqa: A002
            """Initialize the User object."""
            self.id = id
            self.name = name
            self.joined = joined
            self.metadata = metadata

        @classmethod
        def from_dict(cls, data: dict) -> "User":
            """Create a User object from a dictionary."""
            return cls(
                id=data["id"],
                name=data["name"],
                joined=datetime.fromisoformat(data["joined"]),
                metadata=data["metadata"],
            )

        def to_dict(self) -> dict:
            """Convert the User object to a dictionary."""
            return {
                "id": self.id,
                "name": self.name,
                "joined": self.joined.isoformat(),
                "metadata": self.metadata,
            }

    user = User(
        id="user1",
        name="Alice",
        joined=datetime.now(timezone.utc),
        metadata={"role": "admin"},
    )
    set_ds.add(user)
    print(set_ds.contains(user))

    # Pydantic models
    from pydantic import BaseModel

    class User(BaseModel):
        id: str
        name: str
        joined: datetime
        metadata: dict

    user = User(
        id="user1",
        name="Alice",
        joined=datetime.now(timezone.utc),
        metadata={"role": "admin"},
    )
    set_ds.add(user)
    print(set_ds.contains(user))


if __name__ == "__main__":
    demonstrate_type_preservation()
    set_examples()
