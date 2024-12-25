"""Custom exceptions for Redis data structures."""


class RedisDataStructureError(Exception):
    """Base exception for all Redis data structure errors."""


class RedisConnectionError(RedisDataStructureError):
    """Raised when there are connection issues with Redis."""


class SerializationError(RedisDataStructureError):
    """Raised when there are issues serializing/deserializing data."""


class OperationError(RedisDataStructureError):
    """Raised when a Redis operation fails."""


class ValidationError(RedisDataStructureError):
    """Raised when data validation fails."""


class ConfigurationError(RedisDataStructureError):
    """Raised when there are configuration issues."""


class CircuitBreakerError(RedisDataStructureError):
    """Raised when the circuit breaker is open."""


class TypeRegistryError(RedisDataStructureError):
    """Raised when there are issues with the type registry."""


class CapacityError(RedisDataStructureError):
    """Raised when a data structure reaches its capacity limit."""


class TimeoutError(RedisDataStructureError):  # noqa: A001
    """Raised when an operation times out."""
