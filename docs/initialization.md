# Redis Data Structures Connection Management Guide

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Connection Management](#connection-management)

## Installation

```bash
pip install redis-data-structures
```

> **Note:** Ensure that Redis is running for the library to function properly.

## Configuration

### Environment Variables

```bash
# Redis connection
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0
export REDIS_PASSWORD=secret
export REDIS_SSL=true
export REDIS_MAX_CONNECTIONS=10

# Data structure settings
export REDIS_DS_PREFIX=redis_ds
export REDIS_DS_DEBUG=true
export REDIS_DS_COMPRESSION_THRESHOLD=1024
```

### YAML Configuration

```yaml
redis:
  host: localhost
  port: 6379
  db: 0
  password: secret
  ssl: true
  max_connections: 10
  socket_timeout: 5.0
  socket_connect_timeout: 3.0
  socket_keepalive: true
  retry_max_attempts: 3
  circuit_breaker_threshold: 5
  circuit_breaker_timeout: 60
  ssl_keyfile: null
  ssl_certfile: null
  ssl_cert_reqs: required
  ssl_ca_certs: /path/to/ca.pem
data_structures:
  prefix: redis_ds
  compression_threshold: 1024
  debug_enabled: false
```

## Connection Management

### Basic Connection

```python
from redis_data_structures import ConnectionManager, Queue

# Create a basic connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Initialize data structure with connection manager
queue = Queue(connection_manager=connection_manager)

# With SSL
connection_manager = ConnectionManager(
    host='redis.example.com',
    port=6380,
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca.pem'
)
```

### Advanced Usage

```python
from redis_data_structures import ConnectionManager, Queue, Config
from datetime import timedelta

# If environment variables are set, you can skip the config parameter
queue = Queue("tasks")


# Initialize with configuration
config = Config.from_env()  # or Config.from_yaml('config.yaml')
queue = Queue(config=config)  # This will create its own connection manager

# Or use connection manager with advanced features
connection_manager = ConnectionManager(
    host='redis.example.com',
    port=6380,
    max_connections=20,
    retry_max_attempts=5,
    circuit_breaker_threshold=10,
    circuit_breaker_timeout=timedelta(minutes=5),
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca.pem'
)
queue = Queue("tasks", connection_manager=connection_manager)

# Check connection health
health = connection_manager.health_check()
print(f"Status: {health['status']}")  # 'healthy' or 'unhealthy'
print(f"Latency: {health['latency_ms']}ms")
print(f"Connected Clients: {health['connected_clients']}")
print(f"Memory Usage: {health['used_memory']}")
print(f"Redis Version: {health['version']}")
print(f"Connection Pool: {health['connection_pool']}")  # Shows max, current, and available connections
print(f"Circuit Breaker: {health['circuit_breaker']}")  # Shows failure count, threshold, and timeout

# Features:
# - Connection pooling with configurable pool size
# - Automatic reconnection with exponential backoff
# - Circuit breaker pattern for fault tolerance
# - Health checks and monitoring
# - SSL/TLS support
# - Configurable retry attempts and timeouts
# - JSON serialization for complex types
# - Compression support for large values
```

### Reusable Connection Manager

```python
from redis_data_structures import ConnectionManager

# Create a reusable connection manager
conn = ConnectionManager(host='localhost', port=6379, db=0)

# Use the connection manager for multiple data structures
queue = Queue("tasks", connection_manager=conn)
stack = Stack("commands", connection_manager=conn)
```
