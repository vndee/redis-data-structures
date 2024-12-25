from datetime import timedelta
from unittest.mock import Mock, patch

import pytest
from redis.exceptions import RedisError

from redis_data_structures.connection import ConnectionManager
from redis_data_structures.exceptions import CircuitBreakerError


@pytest.fixture
def connection_manager():
    """Create a ConnectionManager instance with mocked Redis."""
    with patch("redis.Redis") as mock_redis:
        # Setup mock Redis instance
        mock_instance = Mock()
        mock_redis.return_value = mock_instance

        # Create connection manager
        manager = ConnectionManager(
            host="localhost",
            port=6379,
            db=0,
            max_connections=10,
        )
        yield manager


def test_initialization(connection_manager):
    """Test ConnectionManager initialization."""
    assert connection_manager.connection_params["host"] == "localhost"
    assert connection_manager.connection_params["port"] == 6379
    assert connection_manager.connection_params["db"] == 0


def test_client_creation(connection_manager):
    """Test Redis client creation."""
    client = connection_manager.client
    assert client is not None
    assert client == connection_manager.client  # Should return same instance


def test_execute_success(connection_manager):
    """Test successful command execution."""
    connection_manager.client.get.return_value = "test_value"
    result = connection_manager.execute("get", "test_key")
    assert result == "test_value"
    connection_manager.client.get.assert_called_once_with("test_key")


def test_execute_failure(connection_manager):
    """Test command execution failure."""
    connection_manager.client.get.side_effect = RedisError("Test error")
    with pytest.raises(CircuitBreakerError):
        connection_manager.execute("get", "test_key")
    assert connection_manager._failure_count > 0  # noqa: SLF001


def test_health_check_success(connection_manager):
    """Test successful health check."""
    connection_manager.client.ping.return_value = True
    connection_manager.client.info.return_value = {
        "connected_clients": 1,
        "used_memory_human": "1M",
        "redis_version": "6.0.0",
    }
    health = connection_manager.health_check()
    assert health["status"] == "healthy"
    assert "latency_ms" in health
    assert health["connected_clients"] == 1


def test_health_check_failure(connection_manager):
    """Test health check failure."""
    connection_manager.client.ping.side_effect = RedisError("Connection failed")
    health = connection_manager.health_check()
    assert health["status"] == "unhealthy"
    assert "error" in health


def test_close_connection(connection_manager):
    """Test connection closing."""
    connection_manager.close()
    assert connection_manager._client is None  # noqa: SLF001
    assert connection_manager._pool is None  # noqa: SLF001


def test_pipeline(connection_manager):
    """Test pipeline creation."""
    mock_pipeline = Mock()
    connection_manager.client.pipeline.return_value = mock_pipeline
    pipeline = connection_manager.pipeline()
    assert pipeline == mock_pipeline


def test_health_check_with_info(connection_manager):
    """Test health check with detailed info."""
    connection_manager.client.ping.return_value = True
    connection_manager.client.info.return_value = {
        "connected_clients": 1,
        "used_memory_human": "1M",
        "redis_version": "6.0.0",
    }
    health = connection_manager.health_check()
    assert "connection_pool" in health
    assert "circuit_breaker" in health
    assert isinstance(health["circuit_breaker"]["timeout"], float)


def test_ssl_configuration():
    """Test SSL configuration."""
    manager = ConnectionManager(
        host="localhost",
        ssl=True,
        ssl_cert_reqs="required",
        ssl_ca_certs="/path/to/cert",
    )
    assert manager.connection_params["ssl"] is True
    assert manager.connection_params["ssl_cert_reqs"] == "required"
    assert manager.connection_params["ssl_ca_certs"] == "/path/to/cert"


def test_circuit_breaker():
    """Test circuit breaker functionality."""
    # Create manager with low threshold and no retries
    manager = ConnectionManager(
        host="localhost",
        circuit_breaker_threshold=2,
        circuit_breaker_timeout=timedelta(seconds=1),
        retry_max_attempts=1,  # Disable retries to make test more predictable
    )

    # Simulate failures
    with patch("redis.Redis") as mock_redis:
        mock_instance = Mock()
        mock_instance.get.side_effect = RedisError("Test error")
        mock_redis.return_value = mock_instance

        # First failure
        with pytest.raises(RedisError):
            manager.execute("get", "key")

        # Second failure should trigger circuit breaker
        with pytest.raises(RedisError):
            manager.execute("get", "key")

        # Third attempt should fail immediately due to circuit breaker
        with pytest.raises(RedisError) as exc_info:
            manager.execute("get", "key")
        assert "Circuit breaker is open" in str(exc_info.value)
        assert manager._failure_count >= manager._circuit_breaker_threshold  # noqa: SLF001


def test_connection_params_filtering():
    """Test connection parameters filtering."""
    manager = ConnectionManager(
        host="localhost",
        password=None,  # Should be filtered out
        socket_timeout=None,  # Should be filtered out
        custom_param="value",  # Should be included
    )
    assert "password" not in manager.connection_params
    assert "socket_timeout" not in manager.connection_params
    assert manager.connection_params["custom_param"] == "value"
