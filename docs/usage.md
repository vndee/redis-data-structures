# Redis Data Structures Usage Guide

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Connection Management](#connection-management)
4. [Data Structures](#data-structures)
5. [Type System](#type-system)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)

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
export REDIS_RETRY_MAX_ATTEMPTS=3
export REDIS_CIRCUIT_BREAKER_THRESHOLD=5
export REDIS_CIRCUIT_BREAKER_TIMEOUT=60

# Data structure settings
export REDIS_DS_PREFIX=myapp
export REDIS_DS_COMPRESSION=true
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
  debug_enabled: true
```

### Using Configuration

```python
from redis_data_structures import Config, ConnectionManager, Queue

# Load from environment
config = Config.from_env()

# Or load from YAML
config = Config.from_yaml('config.yaml')

# Create connection manager from config
connection_manager = ConnectionManager.from_config(config)

# Use connection manager with data structures
queue = Queue(connection_manager=connection_manager)

# Customize configuration
config.data_structures.compression_enabled = True
config.data_structures.compression_threshold = 2048
connection_manager = ConnectionManager.from_config(config)
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

### Advanced Connection Management

```python
from redis_data_structures import ConnectionManager, Queue
from datetime import timedelta

# Create connection manager with advanced features
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

# Use connection manager with data structures
queue = Queue(connection_manager=connection_manager)

# Check connection health
health = connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
print(f"Pool: {health['connection_pool']}")
print(f"Circuit Breaker: {health['circuit_breaker']}")

# Connection manager features:
# - Connection pooling with configurable pool size
# - Automatic reconnection with exponential backoff
# - Circuit breaker pattern for fault tolerance
# - Health checks and monitoring
# - SSL/TLS support
# - Configurable retry attempts and timeouts
```

## Data Structures

### Graph

```python
from redis_data_structures import Graph, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(host='localhost', port=6379)

# Create graph with connection manager
graph = Graph(connection_manager=connection_manager)

# Add vertices with data
graph.add_vertex('social_network', 'user1', {'name': 'Alice', 'age': 30})
graph.add_vertex('social_network', 'user2', {'name': 'Bob', 'age': 25})

# Add edges with weights (e.g., friendship strength)
graph.add_edge('social_network', 'user1', 'user2', weight=0.8)

# Get vertex data
alice = graph.get_vertex_data('social_network', 'user1')
print(f"Name: {alice['name']}, Age: {alice['age']}")

# Get neighbors
neighbors = graph.get_neighbors('social_network', 'user1')
for neighbor, weight in neighbors.items():
    print(f"Friend: {neighbor}, Strength: {weight}")

# Remove vertices and edges
graph.remove_edge('social_network', 'user1', 'user2')
graph.remove_vertex('social_network', 'user1')

# Clear the graph
graph.clear('social_network')
```

### Queue (FIFO)

```python
from redis_data_structures import Queue, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(host='localhost', port=6379)

# Create queue with connection manager
queue = Queue(connection_manager=connection_manager)

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
from redis_data_structures import Stack, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(host='localhost', port=6379)

# Create stack with connection manager
stack = Stack(connection_manager=connection_manager)

# Basic operations
stack.push('my_stack', 'item1')
item = stack.pop('my_stack')  # Returns 'item1'

# Peek without removing
item = stack.peek('my_stack')
```

### Hash Map

```python
from redis_data_structures import HashMap, ConnectionManager
from datetime import datetime

# Initialize connection manager
connection_manager = ConnectionManager(host='localhost', port=6379)

# Create hash map with connection manager
hm = HashMap(connection_manager=connection_manager)

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
from redis_data_structures import BloomFilter, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(host='localhost', port=6379)

# Create bloom filter with connection manager and parameters
bf = BloomFilter(
    connection_manager=connection_manager,
    expected_elements=10000,
    false_positive_rate=0.01
)

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