"""Configuration management for Redis data structures."""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import yaml

from .exceptions import ConfigurationError


@dataclass
class RedisConfig:
    """Redis connection configuration."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    socket_timeout: Optional[float] = None
    socket_connect_timeout: Optional[float] = None
    socket_keepalive: Optional[bool] = None
    connection_pool: Optional[Any] = None
    max_connections: int = 10
    retry_max_attempts: int = 3
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    ssl: bool = False
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_cert_reqs: str = "required"
    ssl_ca_certs: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate configuration values."""
        if self.port < 1 or self.port > 65535:
            raise ConfigurationError(f"Invalid port number: {self.port}")

        if self.db < 0:
            raise ConfigurationError(f"Invalid database number: {self.db}")

        if self.socket_timeout is not None and self.socket_timeout <= 0:
            raise ConfigurationError(f"Invalid socket timeout: {self.socket_timeout}")

        if self.max_connections < 1:
            raise ConfigurationError(f"Invalid max connections: {self.max_connections}")


@dataclass
class DataStructureConfig:
    """Configuration for data structures."""

    prefix: str = "redis_ds"
    compression_threshold: int = 1024  # bytes
    debug_enabled: bool = False


@dataclass
class Config:
    """Global configuration container."""

    redis: RedisConfig = field(default_factory=RedisConfig)
    data_structures: DataStructureConfig = field(default_factory=DataStructureConfig)

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        redis_config = RedisConfig(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
            ssl=os.getenv("REDIS_SSL", "").lower() == "true",
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
        )

        ds_config = DataStructureConfig(
            prefix=os.getenv("REDIS_DS_PREFIX", "redis_ds"),
            debug_enabled=os.getenv("REDIS_DS_DEBUG", "").lower() == "true",
            compression_threshold=int(os.getenv("REDIS_DS_COMPRESSION_THRESHOLD", "1024")),
        )

        return cls(redis=redis_config, data_structures=ds_config)

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """Create configuration from YAML file."""
        try:
            with open(path) as f:
                data = yaml.safe_load(f)

            redis_config = RedisConfig(**data.get("redis", {}))
            ds_config = DataStructureConfig(**data.get("data_structures", {}))

            return cls(redis=redis_config, data_structures=ds_config)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration from {path}: {e}",
            ) from None

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "redis": {
                "host": self.redis.host,
                "port": self.redis.port,
                "db": self.redis.db,
                "password": "***" if self.redis.password else None,
                "ssl": self.redis.ssl,
                "max_connections": self.redis.max_connections,
            },
            "data_structures": {
                "prefix": self.data_structures.prefix,
                "debug_enabled": self.data_structures.debug_enabled,
                "compression_threshold": self.data_structures.compression_threshold,
            },
        }

    def validate(self) -> None:
        """Validate entire configuration."""
        self.redis.validate()

        if self.data_structures.compression_threshold < 0:
            raise ConfigurationError(
                f"Invalid compression threshold: {self.data_structures.compression_threshold}",
            )
