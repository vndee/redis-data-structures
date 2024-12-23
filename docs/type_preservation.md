# Type Preservation in Redis Data Structures

This document explains how Python types are preserved when storing data in Redis using our data structures.

## Overview

Redis natively supports only a limited set of data types, and JSON serialization typically loses information about Python's rich type system. Our implementation preserves Python types through a combination of:

1. A base class system (`CustomRedisDataType`) for custom types
2. Built-in type handlers in the base class
3. Automatic serialization/deserialization with type information

## Built-in Type Support

The following Python types are automatically preserved:

1. **Primitive Types**
   - `int`, `float`, `str`, `bool`, `NoneType`
   - Automatically preserved without special handling
   ```python
   # Example
   hash_map.set("my_hash", "key", 42)  # int
   hash_map.set("my_hash", "key2", True)  # bool
   ```

2. **Tuples**
   - Preserved as ordered, immutable sequences
   - Nested tuples are also preserved
   ```python
   # Example
   data = (1, "two", [3, 4])
   cache.put("my_cache", "tuple_key", data)
   result = cache.get("my_cache", "tuple_key")
   assert isinstance(result, tuple)
   ```

3. **Sets**
   - Preserved as unordered collections of unique elements
   - Elements are sorted during serialization for consistency
   ```python
   # Example
   data = {1, 2, 3}
   set_ds.add("my_set", data)
   result = set_ds.members("my_set").pop()
   assert isinstance(result, set)
   ```

4. **Bytes**
   - Preserved using hexadecimal encoding
   ```python
   # Example
   data = b"binary data"
   hash_map.set("my_hash", "bytes", data)
   result = hash_map.get("my_hash", "bytes")
   assert isinstance(result, bytes)
   ```

5. **Datetime Objects**
   - Preserved with timezone information
   - Stored in ISO format
   ```python
   # Example
   from datetime import datetime, timezone
   data = datetime.now(timezone.utc)
   hash_map.set("my_hash", "date", data)
   result = hash_map.get("my_hash", "date")
   assert isinstance(result, datetime)
   ```

6. **Collections**
   - Lists and dictionaries are preserved with their nested types
   - Nested structures maintain their type information
   ```python
   # Example
   data = {
       "tuple": (1, 2, 3),
       "set": {4, 5, 6},
       "list": [7, 8, (9, 10)]
   }
   hash_map.set("my_hash", "nested", data)
   ```

## Custom Type Support

### Using CustomRedisDataType

To create a custom type that can be automatically serialized/deserialized:

```python
from redis_data_structures.base import CustomRedisDataType

class User(CustomRedisDataType):
    """Example of a custom Redis data type."""
    
    def __init__(self, name: str, joined: datetime):
        self.name = name
        self.joined = joined

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "joined": self.joined  # datetime automatically preserved
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(data["name"], data["joined"])
```

Requirements for custom types:
1. Must inherit from `CustomRedisDataType`
2. Must implement `to_dict()` method
3. Must implement `from_dict()` classmethod

### Using Custom Types

```python
# Create and store a custom type
user = User("John Doe", datetime.now(timezone.utc))
cache.set("users", "john", user)

# Retrieve the custom type
retrieved_user = cache.get("users", "john")
assert isinstance(retrieved_user, User)
assert retrieved_user.name == "John Doe"
```

## Implementation Details

### Type Registration

The `CustomRedisDataType` base class automatically registers types:

```python
class CustomRedisDataType:
    _registered_types: ClassVar[Dict[str, Type]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the type if it has the required methods
        if hasattr(cls, "to_dict") and hasattr(cls, "from_dict"):
            cls._registered_types[cls.__name__] = cls

    @classmethod
    def get_type(cls, type_name: str) -> Optional[Type]:
        """Get registered type by name."""
        return cls._registered_types.get(type_name)
```

### Serialization Format

Data is serialized with type information:

```python
{
    "_type": "type_name",
    "value": serialized_data,
    "timestamp": "2024-01-20T12:34:56.789Z"  # Optional
}
```

### Type Handlers

Built-in types are handled by registered handlers:

```python
self.type_handlers = {
    tuple: {
        "serialize": lambda x: {
            "_type": "tuple",
            "value": [self._serialize_value(item) for item in x],
        },
        "deserialize": lambda x: tuple(
            self._deserialize_value(item) for item in x["value"]
        ),
    },
    # ... other handlers
}
```

## Best Practices

1. **Type Consistency**
   - Use consistent types for the same keys
   - Document expected types in your codebase

2. **Custom Types**
   - Keep serialization methods simple and deterministic
   - Handle version changes gracefully
   - Consider implementing `__str__` for debugging

3. **Performance**
   - Batch operations when possible
   - Keep custom type serialization efficient
   - Consider caching for frequently accessed data

4. **Error Handling**
   ```python
   try:
       result = cache.get("key")
   except Exception as e:
       logger.error(f"Failed to deserialize: {e}")
       # Handle error appropriately
   ```

## Limitations

1. **Circular References**
   - Not supported due to JSON serialization
   - Will raise RecursionError

2. **File Objects**
   - Cannot serialize file handles or sockets
   - Store file paths or descriptors instead

3. **Lambda Functions**
   - Cannot serialize functions or lambdas
   - Store function names or references instead

## Future Enhancements

1. **Planned Type Support**
   - `frozenset`
   - `decimal.Decimal`
   - `uuid.UUID`
   - More datetime types

2. **Performance Improvements**
   - Caching of type information
   - Batch serialization
   - Compression for large objects

## Contributing

To add support for new types:

1. Add a type handler:
   ```python
   self.type_handlers[YourType] = {
       "serialize": lambda x: {"_type": "your_type", "value": ...},
       "deserialize": lambda x: YourType(x["value"])
   }
   ```

2. Add tests for the new type
3. Update this documentation
4. Submit a pull request