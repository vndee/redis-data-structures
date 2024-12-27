import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, TypeVar, Union

from .config import Config
from .connection import ConnectionManager
from .serializer import Serializer

logger = logging.getLogger(__name__)
T = TypeVar("T")


class RedisDataStructure:
    """Base class for Redis-backed data structures."""

    def __init__(
        self,
        key: str,
        connection_manager: Optional[ConnectionManager] = None,
        config: Optional[Config] = None,
        **kwargs: Any,
    ):
        """Initialize Redis data structure."""
        self.config = config or Config.from_env()
        if kwargs:
            for key, value in kwargs.items():
                if hasattr(self.config.redis, key):
                    setattr(self.config.redis, key, value)

        self.connection_manager = connection_manager or ConnectionManager(
            **self.config.redis.__dict__,
        )

        if self.config.data_structures.debug_enabled:
            logger.setLevel(logging.DEBUG)

        self.serializer = Serializer(
            compression_threshold=self.config.data_structures.compression_threshold,
        )
        self.key = f"{self.config.data_structures.prefix}:{key}"

    def set_ttl(self, key: str, ttl: Union[int, timedelta, datetime]) -> bool:
        """Set Time To Live (TTL) for a key."""
        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            elif isinstance(ttl, datetime):
                if ttl.tzinfo is None:
                    ttl = ttl.replace(tzinfo=timezone.utc)  # Make it timezone-aware
                    ttl = int((ttl - datetime.now(timezone.utc)).total_seconds())
                else:
                    ttl = int((ttl - datetime.now(ttl.tzinfo)).total_seconds())
            else:
                ttl = int(ttl)

            return bool(self.connection_manager.execute("expire", key, ttl))
        except Exception:
            logger.exception("Error setting TTL")
            return False

    def get_ttl(self, key: str) -> Any:
        """Get remaining Time To Live (TTL) for a key."""
        try:
            return self.connection_manager.execute("ttl", key)
        except Exception:
            logger.exception("Error getting TTL")
            return None

    def persist(self, key: str) -> bool:
        """Remove TTL from a key."""
        try:
            return bool(self.connection_manager.execute("persist", key))
        except Exception:
            logger.exception("Error removing TTL")
            return False

    def clear(self) -> bool:
        """Clear all elements from the data structure."""
        try:
            return bool(self.connection_manager.execute("delete", self.key))
        except Exception:
            logger.exception("Error clearing data structure")
            return False

    def close(self) -> None:
        """Close Redis connection."""
        self.connection_manager.close()
