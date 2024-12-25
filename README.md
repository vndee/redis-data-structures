# 🌟 Redis Data Structures

[![PyPI version](https://badge.fury.io/py/redis-data-structures.svg)](https://badge.fury.io/py/redis-data-structures)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![codecov](https://codecov.io/gh/vndee/redis-data-structures/graph/badge.svg?token=O9DSUSEJCI)](https://codecov.io/gh/vndee/redis-data-structures)

A Python library providing high-level, Redis-backed data structures with a clean, Pythonic interface. Perfect for distributed systems, microservices, and any application requiring persistent, thread-safe data structures, especially in environments where multiple workers share the same data structure.

💡 **[Examples](examples/)**


### 📋 Table of Contents
- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
- [📊 Data Structures](#-data-structures)
- [💻 Usage Examples](#-usage-examples)
- [🔗 Connection Management](#-connection-management)
- [🔍 Complex Types](#-complex-types)
- [📖 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)


### ✨ Features

- **Thread-safe** data structures backed by Redis
- Clean, **Pythonic interface**
- Connection pooling and **automatic retries**
- **Circuit breaker** pattern for fault tolerance
- JSON serialization and **type preservation** for complex types
- **Async support** (coming soon)


### 📦 Installation

```bash
pip install redis-data-structures
```

> **Note:** Ensure that Redis is running for the library to function properly.

### 🚀 Quick Start

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

You can also skip using `ConnectionManager` if the following environment variables are set:

- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_DB`
- `REDIS_USERNAME`
- `REDIS_PASSWORD`

```python
from redis_data_structures import Queue, Stack, Set

queue = Queue()
stack = Stack()
set_ds = Set()
```

Refer to **[initialization](docs/initialization.md)** for more information.


### 📊 Data Structures

| Structure       | Description                | Use Case                          |
|------------------|----------------------------|-----------------------------------|
| [Queue](docs/queue.md)            | FIFO queue                 | Job processing, message passing    |
| [Stack](docs/stack.md)            | LIFO stack                 | Undo systems, execution contexts   |
| [Set](docs/set.md)              | Unique collection          | Membership testing, deduplication  |
| [HashMap](docs/hash_map.md)          | Key-value store            | Caching, metadata storage          |
| [PriorityQueue](docs/priority_queue.md)    | Priority-based queue       | Task scheduling                    |
| [RingBuffer](docs/ring_buffer.md)       | Fixed-size circular buffer  | Logs, metrics                      |
| [Graph](docs/graph.md)            | Graph with adjacency list  | Relationships, networks            |
| [Trie](docs/trie.md)             | Prefix tree                | Autocomplete, spell checking       |
| [BloomFilter](docs/bloom_filter.md)      | Probabilistic set          | Membership testing                  |
| [Deque](docs/deque.md)            | Double-ended queue         | Sliding windows                    |


### 💻 Usage Examples

```python
from redis_data_structures import Queue

queue = Queue()

# Basic operations
queue.push('tasks', {'id': 1, 'action': 'process'})
task = queue.pop('tasks')
size = queue.size('tasks')

stack = Stack()
stack.push('commands', {'action': 'create'})
command = stack.pop('commands')
size = stack.size('commands')

set_ds = Set()
set_ds.add('users', {'id': 'user1'})
exists = set_ds.contains('users', {'id': 'user1'})
members = set_ds.members('users')

hash_map = HashMap()
hash_map.set('user:1', {'name': 'Alice', 'age': 30})
user = hash_map.get('user:1')
exists = hash_map.exists('user:1')

priority_queue = PriorityQueue()
priority_queue.push('tasks', {'id': 1, 'priority': 1})
task = priority_queue.pop('tasks')
peek = priority_queue.peek('tasks')

...
```
For more examples, see **[examples](examples/)**.


### 🔗 Connection Management

```python
from redis_data_structures import ConnectionManager
from datetime import timedelta

conn = ConnectionManager(
    host='localhost',
    port=6379,
    db=0,
    max_connections=20,
    retry_max_attempts=5,
    circuit_breaker_threshold=10,
    circuit_breaker_timeout=timedelta(minutes=5),
    ssl=True
)

# Reuse for multiple queues
pq1 = PriorityQueue(connection_manager=connection_manager)
pq2 = PriorityQueue(connection_manager=connection_manager)

stack = Stack(connection_manager=connection_manager)
set_ds = Set(connection_manager=connection_manager)
```

### 🔍 Complex Types

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

# Custom types
from redis_data_structures import CustomRedisDataType

class User(CustomRedisDataType):
    id: str
    name: str
    joined: datetime
    metadata: dict

    def __init__(self, id: str, name: str, joined: datetime, metadata: dict):
        self.id = id
        self.name = name
        self.joined = joined
        self.metadata = metadata

    def from_dict(cls, data: dict):
        return cls(id=data['id'], name=data['name'], joined=data['joined'], metadata=data['metadata'])

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'joined': self.joined,
            'metadata': self.metadata
        }

user = User(id='user1', name='Alice', joined=datetime.now(), metadata={'role': 'admin'})
set_ds.add('users', user)

# Pydantic models
from pydantic import BaseModel

class User(BaseModel):
    id: str
    name: str
    joined: datetime
    metadata: dict

user = User(id='user1', name='Alice', joined=datetime.now(), metadata={'role': 'admin'})
set_ds.add('users', user)
```
See **[type preservation](docs/type_preservation.md)** for more information.

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


### 📝 License

This project is licensed under the MIT License - see the **[LICENSE](LICENSE)** file for details.
