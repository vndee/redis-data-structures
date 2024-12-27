import logging
import time
from datetime import timedelta
from typing import Any, Dict, Optional

import backoff
import redis
from redis.connection import ConnectionPool
from redis.exceptions import RedisError

from .exceptions import CircuitBreakerError

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages Redis connections with advanced features like connection pooling, automatic reconnection, and circuit breaking."""  # noqa: E501

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        socket_timeout: Optional[float] = None,
        connection_pool: Optional[ConnectionPool] = None,
        max_connections: int = 10,
        retry_max_attempts: int = 3,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: timedelta = timedelta(seconds=60),
        ssl: bool = False,
        ssl_cert_reqs: Optional[str] = None,
        ssl_ca_certs: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the connection manager.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            socket_timeout: Socket timeout in seconds
            connection_pool: Optional pre-configured connection pool
            max_connections: Maximum number of connections in the pool
            retry_max_attempts: Maximum number of retry attempts
            circuit_breaker_threshold: Number of failures before circuit breaks
            circuit_breaker_timeout: How long to wait before retrying after circuit breaks
            ssl: Whether to use SSL/TLS for the connection
            ssl_cert_reqs: SSL certificate requirements ('none', 'optional', or 'required')
            ssl_ca_certs: Path to the CA certificate file
            **kwargs: Additional keyword arguments for the Redis connection
        """
        # Filter out None values to avoid passing them to Redis
        connection_params = {
            "host": host,
            "port": port,
            "db": db,
        }

        # Add optional parameters only if they are not None
        if password is not None:
            connection_params["password"] = password
        if socket_timeout is not None:
            connection_params["socket_timeout"] = socket_timeout
        if ssl:
            connection_params["ssl"] = True
            if ssl_cert_reqs:
                connection_params["ssl_cert_reqs"] = ssl_cert_reqs
            if ssl_ca_certs:
                connection_params["ssl_ca_certs"] = ssl_ca_certs

        # Add any remaining kwargs
        connection_params.update({k: v for k, v in kwargs.items() if v is not None})

        self.connection_params = connection_params
        self._pool = connection_pool or ConnectionPool(
            max_connections=max_connections,
            **connection_params,  # type: ignore[arg-type]
        )

        self._client: Optional[redis.Redis] = None
        self._failure_count = 0
        self._circuit_breaker_threshold = circuit_breaker_threshold
        self._circuit_breaker_timeout = circuit_breaker_timeout
        self._retry_max_attempts = retry_max_attempts

    @property
    def client(self) -> redis.Redis:
        """Get Redis client, creating it if necessary."""
        if self._client is None:
            self._client = redis.Redis(connection_pool=self._pool)
        return self._client

    @backoff.on_exception(
        backoff.expo,
        (RedisError, ConnectionError, CircuitBreakerError),
        max_tries=3,
        jitter=None,
        on_backoff=lambda details: logger.warning(
            f"Retrying Redis connection after {details['wait']:.2f}s",
        ),
    )
    def execute(self, func_name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a Redis command with automatic retries and circuit breaking.

        Args:
            func_name: Name of the Redis command to execute
            *args: Positional arguments for the command
            **kwargs: Keyword arguments for the command

        Returns:
            The result of the Redis command

        Raises:
            RedisError: If the command fails after retries
        """
        if self._failure_count >= self._circuit_breaker_threshold:
            logger.error("Circuit breaker is open, Redis commands are blocked")
            raise RedisError("Circuit breaker is open") from None

        try:
            func = getattr(self.client, func_name)
            result = func(*args, **kwargs)
            self._failure_count = 0  # Reset on success
            return result
        except (RedisError, ConnectionError, CircuitBreakerError):
            self._failure_count += 1
            logger.exception(f"Redis command failed: {func_name}")
            raise CircuitBreakerError("Circuit breaker is open") from None

    def pipeline(self) -> redis.client.Pipeline:
        """Get a Redis pipeline for batch operations."""
        return self.client.pipeline()

    def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health.

        Returns:
            Dict with health check information
        """
        try:
            start_time = time.time()
            self.client.ping()
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds

            info: Any = self.client.info()
            pool_info = {
                "max_connections": self._pool.max_connections,
                "current_connections": len(self._pool._in_use_connections),  # noqa: SLF001
                "available_connections": len(self._pool._available_connections),  # noqa: SLF001
            }

            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory_human"),
                "version": info.get("redis_version"),
                "connection_pool": pool_info,
                "circuit_breaker": {
                    "failure_count": self._failure_count,
                    "threshold": self._circuit_breaker_threshold,
                    "timeout": self._circuit_breaker_timeout.total_seconds(),
                },
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "circuit_breaker": {
                    "failure_count": self._failure_count,
                    "threshold": self._circuit_breaker_threshold,
                },
            }

    def close(self) -> None:
        """Close all connections in the pool."""
        if self._client:
            self._client.close()
            self._client = None
        if self._pool:
            self._pool.disconnect()
            self._pool = None  # type: ignore[assignment]
