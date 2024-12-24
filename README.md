# Redis Data Structures

[![PyPI version](https://badge.fury.io/py/redis-data-structures.svg)](https://badge.fury.io/py/redis-data-structures)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![codecov](https://codecov.io/gh/vndee/redis-data-structures/branch/main/graph/badge.svg?token=329aeb13-41d7-451e-892e-8ddc2d6ba28b)](https://codecov.io/gh/vndee/redis-data-structures)

A Python library providing high-level, Redis-backed data structures with a clean, Pythonic interface. Perfect for distributed systems, microservices, and any application requiring persistent, thread-safe data structures.

📚 [Detailed Usage Guide](docs/usage.md) | 💡 [Examples](examples/)

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Data Structures](#data-structures)
- [Usage Examples](#usage-examples)
  - [Queue](#queue)
  - [Stack](#stack)
  - [Set](#set)
- [Advanced Topics](#advanced-topics)
  - [Connection Management](#connection-management)
  - [Complex Types](#complex-types)
  - [Best Practices](#best-practices)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Features

✨ **Key Benefits**
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

# Initialize connection
conn = ConnectionManager(host='localhost', port=6379, db=0)

# Create and use data structures
queue = Queue(connection_manager=conn)
queue.push('tasks', {'id': 1, 'action': 'process'})

stack = Stack(connection_manager=conn)
stack.push('history', {'event': 'user_login'})

set_ds = Set(connection_manager=conn)
set_ds.add('users', {'id': 'user1', 'name': 'Alice'})
```

## Data Structures

| Structure | Description | Use Case |
|-----------|-------------|----------|
| Queue | FIFO queue | Job processing, message passing |
| Stack | LIFO stack | Undo systems, execution contexts |
| Set | Unique collection | Membership testing, deduplication |
| HashMap | Key-value store | Caching, metadata storage |
| PriorityQueue | Priority-based queue | Task scheduling |
| RingBuffer | Fixed-size circular buffer | Logs, metrics |
| Graph | Directed graph | Relationships, networks |
| Trie | Prefix tree | Autocomplete, spell checking |
| BloomFilter | Probabilistic set | Membership testing |
| Deque | Double-ended queue | Sliding windows |

## Usage Examples

### Queue

```python
from redis_data_structures import Queue, ConnectionManager

conn = ConnectionManager(host='localhost', port=6379)
queue = Queue(connection_manager=conn)

# Basic operations
queue.push('tasks', {'id': 1, 'action': 'process'})
task = queue.pop('tasks')
size = queue.size('tasks')
```

### Stack

```python
from redis_data_structures import Stack

stack = Stack(connection_manager=conn)

# Basic operations
stack.push('commands', {'action': 'create'})
command = stack.pop('commands')
size = stack.size('commands')
```

### Set

```python
from redis_data_structures import Set

set_ds = Set(connection_manager=conn)

# Basic operations
set_ds.add('users', {'id': 'user1'})
exists = set_ds.contains('users', {'id': 'user1'})
members = set_ds.members('users')
```

## Advanced Topics

### Connection Management

```python
from redis_data_structures import ConnectionManager
from datetime import timedelta

conn = ConnectionManager(
    host='redis.example.com',
    port=6380,
    max_connections=20,
    retry_max_attempts=5,
    circuit_breaker_threshold=10,
    circuit_breaker_timeout=timedelta(minutes=5),
    ssl=True
)
```

### Complex Types

```python
from datetime import datetime

# Any JSON-serializable object
user = {
    'id': 'user1',
    'name': 'Alice',
    'joined': datetime.now().isoformat(),
    'metadata': {'role': 'admin'}
}

set_ds.add('users', user)
```
See [type preservation](docs/type_preservation.md) for more information.

### Best Practices

1. **Connection Management**
   - Use a shared connection manager
   - Configure appropriate pool size
   - Enable automatic retries

2. **Error Handling**
   ```python
   try:
       queue.push('tasks', task)
   except Exception as e:
       logger.error(f"Error: {e}")
   ```

3. **Health Monitoring**
   ```python
   health = conn.health_check()
   if health['status'] != 'healthy':
       logger.warning(f"Issues: {health}")
   ```

## Documentation

For detailed usage instructions and advanced features, please refer to:

- 📖 [Usage Guide](docs/usage.md) - Comprehensive documentation covering all features
- 🎯 [Examples](examples/) - Real-world examples and use cases

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
