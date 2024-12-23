# Redis Data Structures

A Python library providing high-level, Redis-backed data structures with a clean, Pythonic interface. Perfect for distributed systems, microservices, and any application requiring persistent, thread-safe data structures.

## Features

- Thread-safe data structures backed by Redis
- Clean, Pythonic interface
- Connection pooling and automatic retries
- Circuit breaker pattern for fault tolerance
- JSON serialization for complex types
- Comprehensive documentation and examples

## Installation

```bash
pip install redis-data-structures
```

## Quick Start

```python
from redis_data_structures import Queue, Stack, Set, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create data structures
queue = Queue(connection_manager=connection_manager)
stack = Stack(connection_manager=connection_manager)
set_ds = Set(connection_manager=connection_manager)

# Use them like regular Python data structures
queue.push('tasks', {'id': 1, 'action': 'process'})
stack.push('history', {'event': 'user_login'})
set_ds.add('users', {'id': 'user1', 'name': 'Alice'})
```

## Available Data Structures

- **Queue**: FIFO queue for job processing and message passing
- **Stack**: LIFO stack for undo systems and execution contexts
- **Set**: Unique collection for membership testing and deduplication
- **HashMap**: Key-value store for caching and metadata
- **PriorityQueue**: Priority-based queue for task scheduling
- **RingBuffer**: Fixed-size circular buffer for logs and metrics
- **Graph**: Directed graph for relationships and networks
- **Trie**: Prefix tree for autocomplete and spell checking
- **BloomFilter**: Probabilistic set for membership testing
- **Deque**: Double-ended queue for sliding windows

## Basic Usage

### Queue Example

```python
from redis_data_structures import Queue, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create queue
queue = Queue(connection_manager=connection_manager)

# Add items
queue.push('tasks', {'id': 1, 'action': 'process'})
queue.push('tasks', {'id': 2, 'action': 'analyze'})

# Process items
task = queue.pop('tasks')  # Returns first task
size = queue.size('tasks')  # Get current size
```

### Stack Example

```python
from redis_data_structures import Stack, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create stack
stack = Stack(connection_manager=connection_manager)

# Add items
stack.push('commands', {'action': 'create', 'data': {'id': 1}})
stack.push('commands', {'action': 'update', 'data': {'id': 1}})

# Process items
command = stack.pop('commands')  # Returns last command
size = stack.size('commands')    # Get current size
```

### Set Example

```python
from redis_data_structures import Set, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create set
set_ds = Set(connection_manager=connection_manager)

# Add items
set_ds.add('users', {'id': 'user1', 'name': 'Alice'})
set_ds.add('users', {'id': 'user2', 'name': 'Bob'})

# Check membership
exists = set_ds.contains('users', {'id': 'user1'})
members = set_ds.members('users')
```

## Advanced Usage

### Connection Management

```python
from redis_data_structures import ConnectionManager
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

# Share connection manager across data structures
queue = Queue(connection_manager=connection_manager)
stack = Stack(connection_manager=connection_manager)
set_ds = Set(connection_manager=connection_manager)
```

### Complex Types

```python
from datetime import datetime

# Store any JSON-serializable Python object
user = {
    'id': 'user1',
    'name': 'Alice',
    'joined': datetime.now().isoformat(),
    'metadata': {
        'role': 'admin',
        'preferences': {'theme': 'dark'}
    }
}

# The object will be automatically serialized/deserialized
set_ds.add('users', user)
stored_user = set_ds.members('users')[0]
```

## Best Practices

1. **Connection Management**
   - Use a shared connection manager for multiple data structures
   - Configure appropriate connection pool size
   - Enable automatic retries for transient failures

2. **Error Handling**
   ```python
   try:
       queue.push('tasks', task)
   except Exception as e:
       logger.error(f"Error adding task: {e}")
       # Handle error...
   ```

3. **Health Checks**
   ```python
   health = connection_manager.health_check()
   if health['status'] != 'healthy':
       logger.warning(f"Connection issues: {health}")
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests with `pytest`
5. Submit a pull request

## License

MIT License. See LICENSE file for details.
