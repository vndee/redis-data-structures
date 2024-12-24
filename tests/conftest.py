"""Shared test fixtures and configuration."""

import os
from typing import Generator

import pytest
import redis

from redis_data_structures import ConnectionManager


@pytest.fixture(scope="session")
def redis_config() -> dict:
    """Get Redis configuration from environment or defaults."""
    return {
        "host": os.getenv("TEST_REDIS_HOST", "localhost"),
        "port": int(os.getenv("TEST_REDIS_PORT", "6379")),
        "db": int(os.getenv("TEST_REDIS_DB", "0")),
    }


@pytest.fixture(scope="session")
def redis_client(redis_config: dict) -> Generator[redis.Redis, None, None]:
    """Create a Redis client for testing."""
    client = redis.Redis(**redis_config)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(scope="session")
def connection_manager(redis_config: dict) -> ConnectionManager:
    """Create a ConnectionManager instance for testing."""
    return ConnectionManager(**redis_config)


@pytest.fixture(autouse=True)
def clean_redis(redis_client: redis.Redis) -> Generator[None, None, None]:
    """Clean Redis database before and after each test."""
    redis_client.flushdb()
    yield
    redis_client.flushdb()
