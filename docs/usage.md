# Redis Data Structures Usage Guide

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Connection Management](#connection-management)
4. [Data Structures](#data-structures)
5. [Type System](#type-system)
6. [Monitoring](#monitoring)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

## Installation

```bash
pip install redis-data-structures
```

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
export REDIS_DS_PREFIX=myapp
export REDIS_DS_COMPRESSION=true
export REDIS_DS_METRICS=true
export REDIS_DS_DEBUG=true
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
  retry_max_attempts: 3
  circuit_breaker_threshold: 5
  circuit_breaker_timeout: 60

data_structures:
  prefix: myapp
  compression_enabled: true
  compression_threshold: 1024
  metrics_enabled: true
  debug_enabled: true
```

### Using Configuration

```python
from redis_data_structures import Config, Queue

# Load from environment
config = Config.from_env()

# Or load from YAML
config = Config.from_yaml('config.yaml')

# Customize configuration
config.data_structures.compression_enabled = True
config.data_structures.compression_threshold = 2048

# Use configuration
queue = Queue(config=config)
```

## Connection Management

### Basic Connection

```python
from redis_data_structures import Queue

# Default connection (localhost:6379)
queue = Queue()

# Custom connection
queue = Queue(host='redis.example.com', port=6380)

# With SSL
queue = Queue(
    host='redis.example.com',
    port=6380,
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca.pem'
)
```

### Advanced Connection Management

```python
from redis_data_structures import ConnectionManager, Queue
from datetime import timedelta

# Create connection manager with advanced features
manager = ConnectionManager(
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

# Use connection manager
queue = Queue(connection_manager=manager)

# Check connection health
health = manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
print(f"Pool: {health['connection_pool']}")
print(f"Circuit Breaker: {health['circuit_breaker']}")
```

## Data Structures

### Deque (Double-ended Queue)

```python
from redis_data_structures import Deque

deque = Deque()

# Front operations
deque.push_front('my_deque', 'first')
deque.push_front('my_deque', 'second')
item = deque.pop_front('my_deque')  # Returns 'second'
front = deque.peek_front('my_deque')  # Returns 'first' without removing

# Back operations
deque.push_back('my_deque', 'last')
item = deque.pop_back('my_deque')  # Returns 'last'
back = deque.peek_back('my_deque')  # Returns 'first' without removing

# Other operations
size = deque.size('my_deque')
deque.clear('my_deque')

# With type preservation
from datetime import datetime
deque.push_front('my_deque', {
    'timestamp': datetime.now(),
    'data': [1, 2, 3]
})
data = deque.pop_front('my_deque')  # Returns dict with datetime preserved
```

### Queue (FIFO)

```python
from redis_data_structures import Queue

queue = Queue()

# Basic operations
queue.push('my_queue', 'item1')
item = queue.pop('my_queue')  # Returns 'item1'

# With TTL
from datetime import timedelta
queue.set_ttl('my_queue', timedelta(minutes=5))

# Check size
size = queue.size('my_queue')
```

### Stack (LIFO)

```python
from redis_data_structures import Stack

stack = Stack()

# Basic operations
stack.push('my_stack', 'item1')
item = stack.pop('my_stack')  # Returns 'item1'

# Peek without removing
item = stack.peek('my_stack')
```

### Hash Map

```python
from redis_data_structures import HashMap
from datetime import datetime

hm = HashMap()

# Store complex types
data = {
    'name': 'John',
    'joined': datetime.now(),
    'scores': [1, 2, 3]
}
hm.set('users', 'john', data)

# Retrieve with types preserved
user = hm.get('users', 'john')
print(f"Joined: {user['joined']}")  # datetime object

# Get all fields
all_data = hm.get_all('users')
fields = hm.get_fields('users')
```

### Bloom Filter

```python
from redis_data_structures import BloomFilter

# Create with expected elements and false positive rate
bf = BloomFilter(expected_elements=10000, false_positive_rate=0.01)

# Add items
bf.add('my_filter', 'item1')
bf.add('my_filter', {'complex': 'data'})

# Check membership
exists = bf.contains('my_filter', 'item1')  # True
exists = bf.contains('my_filter', 'item2')  # False

# Get size in bits
size = bf.size()
```

## Type System

### Custom Types

```python
from redis_data_structures import CustomRedisDataType
from datetime import datetime

class Event(CustomRedisDataType):
    def __init__(self, name: str, timestamp: datetime):
        self.name = name
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        return cls(
            name=data['name'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )

# Use in data structures
from redis_data_structures import Queue

queue = Queue()
event = Event('user_login', datetime.now())
queue.push('events', event)

# Retrieve with type preserved
retrieved = queue.pop('events')  # Returns Event object
print(f"Event: {retrieved.name} at {retrieved.timestamp}")
```

### Pydantic Integration

```python
from pydantic import BaseModel
from datetime import datetime

# Pydantic models work automatically
class UserModel(BaseModel):
    name: str
    email: str
    joined: datetime
    scores: list[int]

# Use with any data structure
from redis_data_structures import HashMap

hm = HashMap()
user = UserModel(
    name="John",
    email="john@example.com",
    joined=datetime.now(),
    scores=[1, 2, 3]
)

# Store and retrieve with full type preservation
hm.set('users', 'john', user)
retrieved = hm.get('users', 'john')  # Returns UserModel instance
```

## Monitoring

### Operation Metrics

All operations are automatically tracked with metrics:

```python
from redis_data_structures import Queue, Config

config = Config()
config.data_structures.metrics_enabled = True
queue = Queue(config=config)

# Operations are tracked
queue.push('my_queue', 'item')
queue.pop('my_queue')

# Check connection health
health = queue.connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
print(f"Pool: {health['connection_pool']}")
print(f"Circuit Breaker: {health['circuit_breaker']}")
```

## Error Handling

All data structures use proper error handling and logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

from redis_data_structures import Queue

queue = Queue()

# Operations handle errors gracefully
success = queue.push('my_queue', 'item')
if not success:
    print("Operation failed")

# Check connection health
health = queue.connection_manager.health_check()
if health['status'] != 'healthy':
    print(f"Connection issue: {health['error']}")
```

## Best Practices

1. **Connection Management**:
   - Use connection pooling for better performance
   - Enable circuit breaker for fault tolerance
   - Monitor connection health regularly

2. **Error Handling**:
   - Enable logging for better debugging
   - Check operation return values
   - Use health checks proactively

3. **Performance**:
   - Enable compression for large values
   - Use batch operations when possible
   - Monitor memory usage

4. **Type Safety**:
   - Use custom types or Pydantic models
   - Validate data before storing
   - Handle serialization errors

5. **Monitoring**:
   - Enable metrics collection
   - Monitor connection pool usage
   - Check circuit breaker status