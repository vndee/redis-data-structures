"""Health check utilities for Redis Data Structures."""

import time
from typing import Dict, Optional, Tuple

import redis

from .logging import logger


def check_redis_connection(
    host: str = "localhost",
    port: int = 6379,
    password: Optional[str] = None,
    timeout: float = 5.0
) -> Tuple[bool, str]:
    """Check Redis connection health.
    
    Args:
        host: Redis host
        port: Redis port
        password: Optional Redis password
        timeout: Connection timeout in seconds
    
    Returns:
        Tuple[bool, str]: (is_healthy, message)
    """
    try:
        start_time = time.time()
        client = redis.Redis(
            host=host,
            port=port,
            password=password,
            socket_timeout=timeout
        )
        
        # Test connection
        client.ping()
        
        # Get basic info
        info = client.info()
        latency = time.time() - start_time
        
        return True, f"Redis is healthy (latency: {latency:.3f}s)"
        
    except redis.ConnectionError as e:
        logger.error(f"Redis connection failed: {e}")
        return False, f"Connection failed: {str(e)}"
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False, f"Health check failed: {str(e)}"
    finally:
        try:
            client.close()
        except:
            pass


def get_redis_metrics(
    host: str = "localhost",
    port: int = 6379,
    password: Optional[str] = None
) -> Dict[str, str]:
    """Get basic Redis metrics.
    
    Args:
        host: Redis host
        port: Redis port
        password: Optional Redis password
    
    Returns:
        Dict[str, str]: Dictionary of metrics
    """
    try:
        client = redis.Redis(
            host=host,
            port=port,
            password=password
        )
        
        info = client.info()
        
        return {
            "version": info.get("redis_version", "unknown"),
            "used_memory": info.get("used_memory_human", "unknown"),
            "connected_clients": str(info.get("connected_clients", "unknown")),
            "uptime_days": str(info.get("uptime_in_days", "unknown")),
            "total_commands_processed": str(info.get("total_commands_processed", "unknown"))
        }
        
    except Exception as e:
        logger.error(f"Failed to get Redis metrics: {e}")
        return {"error": str(e)}
    finally:
        try:
            client.close()
        except:
            pass 