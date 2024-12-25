from unittest.mock import patch

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError

from redis_data_structures.health import check_redis_connection, get_redis_metrics


class TestHealthCheck:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup any necessary resources for testing."""
        self.host = "localhost"
        self.port = 6379
        self.password = None

    def test_check_redis_connection_success(self):
        """Test successful Redis connection."""
        with patch("redis.Redis.ping") as mock_ping:
            mock_ping.return_value = True  # Simulate successful ping
            is_healthy, message = check_redis_connection(self.host, self.port, self.password)
            assert is_healthy is True
            assert "Redis is healthy" in message

    def test_check_redis_connection_failure(self):
        """Test Redis connection failure."""
        with patch("redis.Redis.ping", side_effect=RedisConnectionError):
            is_healthy, message = check_redis_connection(self.host, self.port, self.password)
            assert is_healthy is False
            assert "Connection failed" in message

    def test_get_redis_metrics_success(self):
        """Test successful retrieval of Redis metrics."""
        mock_info = {
            "redis_version": "6.0.9",
            "used_memory_human": "1.23M",
            "connected_clients": 5,
            "uptime_in_days": 10,
            "total_commands_processed": 1000,
        }

        with patch("redis.Redis.info", return_value=mock_info):
            metrics = get_redis_metrics(self.host, self.port, self.password)
            assert metrics["version"] == "6.0.9"
            assert metrics["used_memory"] == "1.23M"
            assert metrics["connected_clients"] == "5"
            assert metrics["uptime_days"] == "10"
            assert metrics["total_commands_processed"] == "1000"

    def test_get_redis_metrics_failure(self):
        """Test failure to retrieve Redis metrics."""
        with patch("redis.Redis.info", side_effect=Exception("Failed to get info")):
            metrics = get_redis_metrics(self.host, self.port, self.password)
            assert "error" in metrics
            assert metrics["error"] == "Failed to get Redis metrics"

    def test_healthcheck_failed_without_connection_error(self):
        """Test healthcheck failed without connection error."""
        with patch("redis.Redis.ping", side_effect=Exception("Failed to ping")):
            is_healthy, message = check_redis_connection(self.host, self.port, self.password)
            assert is_healthy is False
            assert "Health check failed" in message
