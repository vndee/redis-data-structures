from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple

from redis_data_structures import HashMap, LRUCache
from redis_data_structures.base import CustomRedisDataType


class User(CustomRedisDataType):
    """Example of a custom Redis data type for storing user information."""

    def __init__(self, name: str, joined: datetime):
        self.name = name
        self.joined = joined

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "joined": self.joined,  # datetime will be automatically preserved
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(data["name"], data["joined"])

    def __str__(self) -> str:
        return f"User(name='{self.name}', joined={self.joined.isoformat()})"


def demonstrate_type_preservation():
    """Demonstrate type preservation across different Redis data structures."""
    # Initialize data structures with Redis connection parameters
    cache = LRUCache(capacity=1000, host="localhost", port=6379, db=0)
    hash_map = HashMap(host="localhost", port=6379, db=0)

    # Clear any existing data
    cache.clear("type_demo_cache")
    hash_map.clear("type_demo_hash")

    print("=== Type Preservation Example ===")

    # Example 1: Tuples
    print("\nTuple Preservation:")
    tuple_data: Tuple[int, str, List[int]] = (1, "two", [3, 4])
    hash_map.set("type_demo_hash", "tuple", tuple_data)
    result = hash_map.get("type_demo_hash", "tuple")
    print(f"Original: {tuple_data} ({type(tuple_data)})")
    print(f"Retrieved: {result} ({type(result)})")

    # Example 2: Sets
    print("\nSet Preservation:")
    set_data: Set[int] = {1, 2, 3, 4}
    hash_map.set("type_demo_hash", "set", set_data)
    result = hash_map.get("type_demo_hash", "set")
    print(f"Original: {set_data} ({type(set_data)})")
    print(f"Retrieved: {result} ({type(result)})")

    # Example 3: Datetime
    print("\nDatetime Preservation:")
    date_data = datetime.now(timezone.utc)
    hash_map.set("type_demo_hash", "date", date_data)
    result = hash_map.get("type_demo_hash", "date")
    print(f"Original: {date_data} ({type(date_data)})")
    print(f"Retrieved: {result} ({type(result)})")

    # Example 4: Complex Nested Structures
    print("\nNested Structure Preservation:")
    complex_data: Dict[str, Any] = {
        "tuple": (1, 2, 3),
        "set": {4, 5, 6},
        "list": [7, 8, (9, 10)],
        "dict": {"key": (11, 12)},
    }
    hash_map.set("type_demo_hash", "nested", complex_data)
    result = hash_map.get("type_demo_hash", "nested")
    print("Original:")
    print_nested_types(complex_data)
    print("\nRetrieved:")
    print_nested_types(result)

    # Example 5: Custom Object (User) with Type Preservation
    print("\nCustom Object (User) Type Preservation:")
    user = User("John Doe", datetime.now(timezone.utc))

    # Store in different data structures
    cache.put("user_cache", "john", user)
    hash_map.set("user_hash", "john_doe", user)

    # Retrieve and verify
    cache_result = cache.get("user_cache", "john")
    hash_result = hash_map.get("user_hash", "john_doe")

    print(f"Original: {user}")
    print(f"From Cache: {cache_result}")
    print(f"From Hash: {hash_result}")

    # Example 6: Mixed Types in Hash
    print("\nMixed Types in Hash:")
    hash_map.set("mixed_hash", "string", "string value")
    hash_map.set("mixed_hash", "number", 42)
    hash_map.set("mixed_hash", "tuple", (1, 2, 3))
    hash_map.set("mixed_hash", "user", user)

    print("Hash entries:")
    for key in ["string", "number", "tuple", "user"]:
        value = hash_map.get("mixed_hash", key)
        print(f"  {key}: {value} ({type(value).__name__})")


def print_nested_types(obj: Any, indent: int = 0) -> None:
    """Print nested structure with type information."""
    prefix = "  " * indent
    if isinstance(obj, dict):
        print(f"{prefix}dict:")
        for key, value in obj.items():
            print(f"{prefix}  {key}:")
            print_nested_types(value, indent + 2)
    elif isinstance(obj, (list, tuple)):
        type_name = "list" if isinstance(obj, list) else "tuple"
        print(f"{prefix}{type_name}:")
        for item in obj:
            print_nested_types(item, indent + 1)
    elif isinstance(obj, set):
        print(f"{prefix}set: {obj}")
    else:
        print(f"{prefix}{obj} ({type(obj).__name__})")


if __name__ == "__main__":
    demonstrate_type_preservation()
