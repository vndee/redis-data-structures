import uuid
import zlib
from datetime import datetime, timedelta
from typing import Any, ClassVar, Dict, Optional, Type

import orjson as json

try:
    from pydantic import BaseModel

    PYDANTIC_AVAILABLE = True
except ImportError:
    BaseModel = object  # type: ignore[assignment, misc]
    PYDANTIC_AVAILABLE = False


class CustomRedisDataType:
    """Base class for creating custom Redis data types.

    Example with standard class:
        ```python
        class User(CustomRedisDataType):
            def __init__(self, name: str, age: int):
                self.name = name
                self.age = age

            def to_dict(self) -> dict:
                return {"name": self.name, "age": self.age}

            @classmethod
            def from_dict(cls, data: dict) -> 'User':
                return cls(data["name"], data["age"])
        ```
    """

    def to_dict(self) -> dict:
        """Convert instance to dictionary."""
        raise NotImplementedError("Subclasses must implement to_dict()")

    @classmethod
    def from_dict(cls, data: dict) -> "CustomRedisDataType":
        """Create instance from dictionary."""
        raise NotImplementedError("Subclasses must implement from_dict()")


class TypeRegistry:
    """Registry for managing custom type mappings."""

    _instance = None
    _registry: ClassVar[Dict[str, Type]] = {}

    def __new__(cls) -> "TypeRegistry":
        """Create a new instance of the registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, type_name: str, type_cls: Type) -> None:
        """Register a type with a specific name."""
        cls._registry[type_name] = type_cls

    @classmethod
    def get(cls, type_name: str) -> Optional[Type]:
        """Get a type by its name."""
        return cls._registry.get(type_name)


class Serializer:
    """Serializer for Redis data structures."""

    COMPRESSION_MARKER = "434D5052:"  # CMPR:
    COMPRESSION_MARKER_LEN = len(COMPRESSION_MARKER)

    def __init__(self, compression_threshold: int = 1024):
        """Initialize the serializer.

        Args:
            compression_threshold: The threshold for compression.
        """
        self.custom_type_registry = TypeRegistry()
        self.pydantic_type_registry = TypeRegistry()
        self.compression_threshold = compression_threshold

        self.type_handlers = {
            "int": {
                "serialize": lambda x: {"_type": "int", "value": x},
                "deserialize": lambda x: int(x["value"]),
            },
            "float": {
                "serialize": lambda x: {"_type": "float", "value": x},
                "deserialize": lambda x: float(x["value"]),
            },
            "str": {
                "serialize": lambda x: {"_type": "str", "value": x},
                "deserialize": lambda x: str(x["value"]),
            },
            "bool": {
                "serialize": lambda x: {"_type": "bool", "value": x},
                "deserialize": lambda x: bool(x["value"]),
            },
            "list": {
                "serialize": lambda x: {
                    "_type": "list",
                    "value": [self._serialize_recursive(item) for item in x],
                },
                "deserialize": lambda x: [self._deserialize_recursive(item) for item in x["value"]],
            },
            "dict": {
                "serialize": lambda x: {
                    "_type": "dict",
                    "value": {str(k): self._serialize_recursive(v) for k, v in x.items()},
                },
                "deserialize": lambda x: {
                    k: self._deserialize_recursive(v) for k, v in x["value"].items()
                },
            },
            "tuple": {
                "serialize": lambda x: {
                    "_type": "tuple",
                    "value": [self._serialize_recursive(item) for item in x],
                },
                "deserialize": lambda x: tuple(
                    self._deserialize_recursive(item) for item in x["value"]
                ),
            },
            "set": {
                "serialize": lambda x: {
                    "_type": "set",
                    "value": [self._serialize_recursive(item) for item in x],
                },
                "deserialize": lambda x: {self._deserialize_recursive(item) for item in x["value"]},
            },
            "datetime": {
                "serialize": lambda x: {"_type": "datetime", "value": x.isoformat()},
                "deserialize": lambda x: datetime.fromisoformat(x["value"]),
            },
            "timedelta": {
                "serialize": lambda x: {"_type": "timedelta", "value": x.total_seconds()},
                "deserialize": lambda x: timedelta(seconds=float(x["value"])),
            },
            "bytes": {
                "serialize": lambda x: {"_type": "bytes", "value": x.hex()},
                "deserialize": lambda x: bytes.fromhex(x["value"]),
            },
            "UUID": {
                "serialize": lambda x: {"_type": "UUID", "value": str(x)},
                "deserialize": lambda x: uuid.UUID(x["value"]),
            },
            "NoneType": {
                "serialize": lambda _: {"_type": "NoneType", "value": None},
                "deserialize": lambda _: None,
            },
        }

    def _serialize_recursive(self, data: Any) -> Any:
        """Serialize data to a hex string."""
        if type(data).__name__ in self.type_handlers:
            return self.type_handlers[type(data).__name__]["serialize"](data)  # type: ignore[index]
        if isinstance(data, CustomRedisDataType):
            return {"_type": data.__class__.__name__, "value": data.to_dict()}
        if isinstance(data, BaseModel) and PYDANTIC_AVAILABLE:
            return {"_type": data.__class__.__name__, "value": data.model_dump(mode="json")}
        raise ValueError(f"Unsupported type: {type(data)} {type(data).__name__}")

    def _deserialize_recursive(self, data: Any) -> Any:
        """Deserialize data."""
        if isinstance(data, dict) and "_type" in data:
            if data["_type"] == "NoneType":
                return None

            type_name = data["_type"]
            if type_name in self.type_handlers:
                return self.type_handlers[type_name]["deserialize"](data)  # type: ignore[index]

        return data

    def serialize(self, data: Any) -> Any:
        """Serialize data to a string."""
        if isinstance(data, BaseModel) and PYDANTIC_AVAILABLE:
            raw_str_data = {
                "value": data.model_dump(mode="json"),
                "_type": data.__class__.__name__,
                "_registry": "pydantic",
            }
            self.pydantic_type_registry.register(data.__class__.__name__, data.__class__)
        elif isinstance(data, CustomRedisDataType):
            raw_str_data = {
                "value": data.to_dict(),
                "_type": data.__class__.__name__,
                "_registry": "custom",
            }
            self.custom_type_registry.register(data.__class__.__name__, data.__class__)
        else:
            raw_str_data = self._serialize_recursive(data)

        raw_str_data = json.dumps(raw_str_data)  # type: ignore[assignment]

        if len(raw_str_data) >= self.compression_threshold:
            return f"{self.COMPRESSION_MARKER}{zlib.compress(raw_str_data).hex()}".encode()  # type: ignore[arg-type]

        return raw_str_data

    def _is_compressed(self, data: Any) -> bool:
        """Check if data is compressed."""
        return data.startswith(self.COMPRESSION_MARKER)  # type: ignore[no-any-return]

    def deserialize(self, data: Any) -> Any:
        """Deserialize data from a string."""
        if not data:
            return None

        data = data.decode()
        if self._is_compressed(data):
            data = zlib.decompress(bytes.fromhex(data[self.COMPRESSION_MARKER_LEN :]))

        data = json.loads(data)
        if "_registry" in data and data["_registry"] == "pydantic":
            return self.pydantic_type_registry.get(data["_type"]).model_validate(data["value"])  # type: ignore[union-attr]
        if "_registry" in data and data["_registry"] == "custom":
            return self.custom_type_registry.get(data["_type"]).from_dict(data["value"])  # type: ignore[union-attr]
        return self._deserialize_recursive(data)