# Type Preservation in Redis Data Structures

This document explains how Python types are preserved when storing data in Redis using our data structures.

## Overview

Redis natively supports only a limited set of data types, and JSON serialization typically loses information about Python's rich type system. Our implementation preserves Python types through a combination of:

1. A base class system (`CustomRedisDataType`) for custom types
2. Built-in type handlers for common Python types
3. Automatic serialization/deserialization with type information
4. Pydantic model support for schema validation and complex types

## Built-in Type Support

The following Python types are automatically preserved:

1. **Primitive Types**
   - `int`, `float`, `str`, `bool`, `NoneType`
   - Automatically preserved without special handling
   ```python
   hash_map.set("my_hash", "key", 42)  # int
   hash_map.set("my_hash", "key2", True)  # bool
   ```

2. **Tuples**
   - Preserved as ordered, immutable sequences
   - Nested tuples are also preserved
   ```python
   data = (1, "two", [3, 4])
   hash_map.set("my_hash", "tuple", data)
   result = hash_map.get("my_hash", "tuple")
   assert isinstance(result, tuple)
   ```

3. **Sets**
   - Preserved as unordered collections of unique elements
   - Elements are sorted during serialization for consistency
   ```python
   data = {1, 2, 3}
   hash_map.set("my_hash", "set", data)
   result = hash_map.get("my_hash", "set")
   assert isinstance(result, set)
   ```

4. **Bytes**
   - Preserved using hexadecimal encoding
   ```python
   data = b"binary data"
   hash_map.set("my_hash", "bytes", data)
   result = hash_map.get("my_hash", "bytes")
   assert isinstance(result, bytes)
   ```

5. **Datetime Objects**
   - Preserved with timezone information
   - Stored in ISO format
   ```python
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
   data = {
       "tuple": (1, 2, 3),
       "set": {4, 5, 6},
       "list": [7, 8, (9, 10)]
   }
   hash_map.set("my_hash", "nested", data)
   ```

## Custom Type Support

### Standard Class Approach

For simple custom types, you can inherit from `CustomRedisDataType` and implement the required methods:

```python
from redis_data_structures.base import CustomRedisDataType

class User(CustomRedisDataType):
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

### Pydantic Integration

For complex types with validation requirements, you can use Pydantic models:

```python
from pydantic import BaseModel, Field
from redis_data_structures.base import CustomRedisDataType

# Nested Pydantic model
class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: Optional[str] = None

# Main model with validation
class UserModel(CustomRedisDataType, BaseModel):
    name: str
    email: str
    age: int = Field(gt=0, lt=150)  # with validation
    joined: datetime
    address: Optional[Address] = None  # nested model
    tags: Set[str] = set()  # complex types
```

Pydantic models automatically get:
- Type validation
- Schema validation
- Nested model support
- Optional fields
- Default values
- Field validation
- Automatic serialization/deserialization

### Using Custom Types

Both standard and Pydantic models work seamlessly with Redis structures:

```python
# Standard class
user = User("John Doe", datetime.now(timezone.utc))
hash_map.set("users", "standard", user)
standard_user = hash_map.get("users", "standard")

# Pydantic model
pydantic_user = UserModel(
    name="Jane Smith",
    email="jane@example.com",
    age=30,
    joined=datetime.now(timezone.utc),
    address=Address(
        street="123 Main St",
        city="New York",
        country="USA"
    ),
    tags={"developer", "python"}
)
hash_map.set("users", "pydantic", pydantic_user)
retrieved_user = hash_map.get("users", "pydantic")
```

## Implementation Details

### Type Registration

The `CustomRedisDataType` base class handles type registration:

```python
class CustomRedisDataType:
    _registered_types: ClassVar[Dict[str, Type]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        
        # Handle Pydantic models
        if PYDANTIC_AVAILABLE and issubclass(cls, BaseModel):
            cls._registered_types[cls.__name__] = cls
            if not hasattr(cls, "to_dict"):
                cls.to_dict = lambda self: self.model_dump()
            if not hasattr(cls, "from_dict"):
                cls.from_dict = classmethod(lambda cls, data: cls.model_validate(data))
        # Handle standard classes
        elif hasattr(cls, "to_dict") and hasattr(cls, "from_dict"):
            cls._registered_types[cls.__name__] = cls
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

## Best Practices

1. **Choose the Right Approach**
   - Use standard classes for simple types
   - Use Pydantic for complex types needing validation
   - Consider using Pydantic for API interfaces

2. **Type Consistency**
   - Use consistent types for the same keys
   - Document expected types
   - Use type hints

3. **Validation**
   - Use Pydantic's validation features
   - Add custom validators when needed
   - Handle validation errors gracefully

4. **Performance**
   - Use batch operations when possible
   - Consider caching for frequently accessed data
   - Profile serialization performance

5. **Error Handling**
   ```python
   try:
       result = hash_map.get("key")
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

4. **Pydantic Version Compatibility**
   - Requires Pydantic v2.0 or later for `model_dump` and `model_validate`
   - Falls back to standard class behavior if Pydantic is not available

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

3. **Pydantic Features**
   - Custom serialization formats
   - Validation caching
   - Schema evolution support

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