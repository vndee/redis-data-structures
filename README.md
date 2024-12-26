# 🌟 Redis Data Structures

[![PyPI version](https://badge.fury.io/py/redis-data-structures.svg)](https://badge.fury.io/py/redis-data-structures)
![PyPI Downloads](https://static.pepy.tech/badge/redis-data-structures)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![codecov](https://codecov.io/gh/vndee/redis-data-structures/graph/badge.svg?token=O9DSUSEJCI)](https://codecov.io/gh/vndee/redis-data-structures)
[![code linting](https://github.com/vndee/redis-data-structures/actions/workflows/pylint.yaml/badge.svg)](https://github.com/vndee/redis-data-structures/actions/workflows/pylint.yaml)
[![tests](https://github.com/vndee/redis-data-structures/actions/workflows/pytest.yaml/badge.svg)](https://github.com/vndee/redis-data-structures/actions/workflows/pytest.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library providing high-level, Redis-backed data structures with a clean, Pythonic interface. Perfect for distributed systems, microservices, and any application requiring persistent, thread-safe data structures, especially in environments where multiple workers share the same data structure.

![Redis Data Structures (1)](https://github.com/user-attachments/assets/2c3ad6c9-4150-4626-9d27-40d3a1da3309)


💡 **[Examples](examples/)**


### 📋 Table of Contents
- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
- [📊 Data Structures](#-data-structures)
- [💻 Usage Examples](#-usage-examples)
- [🔗 Connection Management](#-connection-management)
- [🔍 Complex Types](#-complex-types)
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
queue = Queue("tasks", connection_manager=conn)
queue.push({'id': 1, 'action': 'process'})

stack = Stack("commands", connection_manager=conn)
stack.push({'action': 'create'})

set_ds = Set("users", connection_manager=conn)
set_ds.add({'id': 'user1', 'name': 'Alice'})
```

You can also skip using `ConnectionManager` if the following environment variables are set:

- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_DB`
- `REDIS_USERNAME`
- `REDIS_PASSWORD`

```python
from redis_data_structures import Queue, Stack, Set

queue = Queue("test_queue")
stack = Stack("test_stack")
set_ds = Set("test_set")
```

Refer to **[initialization](docs/initialization.md)** for more information.


### 📊 Data Structures

| Structure       | Description                | Use Case                          |
|------------------|----------------------------|-----------------------------------|
| [Queue](docs/queue.md)            | FIFO queue                 | Job processing, message passing    |
| [Stack](docs/stack.md)            | LIFO stack                 | Undo systems, execution contexts   |
| [Set](docs/set.md)              | Unique collection          | Membership testing, deduplication  |
| [Dict](docs/dict.md)              | Python-like dictionary (key-value store)            | Caching, metadata storage          |
| [HashMap](docs/hash_map.md)          | Key-value store            | Caching, metadata storage          |
| [PriorityQueue](docs/priority_queue.md)    | Priority-based queue       | Task scheduling                    |
| [RingBuffer](docs/ring_buffer.md)       | Fixed-size circular buffer  | Logs, metrics                      |
| [Graph](docs/graph.md)            | Graph with adjacency list  | Relationships, networks            |
| [Trie](docs/trie.md)             | Prefix tree                | Autocomplete, spell checking       |
| [BloomFilter](docs/bloom_filter.md)      | Probabilistic set          | Membership testing                  |
| [Deque](docs/deque.md)            | Double-ended queue         | Sliding windows                    |


### 💻 Usage Examples

![Redis Data Structures (2)](https://github.com/user-attachments/assets/06d8e6e6-af64-48f3-b422-a5e688d71c31)

```python
from redis_data_structures import Queue

queue = Queue("tasks")

# Basic operations
queue.push({'id': 1, 'action': 'process'})
task = queue.pop()
size = queue.size()

stack = Stack("commands")
stack.push({'action': 'create'})
command = stack.pop()
size = stack.size()

set_ds = Set("users")
set_ds.add({'id': 'user1'})
exists = set_ds.contains({'id': 'user1'})
members = set_ds.members()

hash_map = HashMap("users")
hash_map.set('user:1', {'name': 'Alice', 'age': 30})
user = hash_map.get('user:1')
exists = hash_map.exists('user:1')

priority_queue = PriorityQueue("tasks")
priority_queue.push({'id': 1, 'priority': 1})
task = priority_queue.pop()
peek = priority_queue.peek()

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
pq1 = PriorityQueue("tasks", connection_manager=conn)
pq2 = PriorityQueue("tasks", connection_manager=conn)

stack = Stack("commands", connection_manager=conn)
set_ds = Set("users", connection_manager=conn)
```

### 🔍 Complex Types

![Redis Data Structures (3)](https://github.com/user-attachments/assets/251753a3-f331-40a9-90a5-41d66ea796f4)


```python
from redis_data_structures import LRUCache, HashMap
from datetime import datetime, timezone
from pydantic import BaseModel

class User(CustomRedisDataType):
    """Example of a custom Redis data type using standard class."""

    def __init__(self, name: str, joined: datetime):
        """Initialize the User object."""
        self.name = name
        self.joined = joined

    def to_dict(self) -> dict:
        """Convert the User object to a dictionary."""
        return {
            "name": self.name,
            "joined": self.joined.isoformat(),  # Convert datetime to string
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create a User object from a dictionary."""
        return cls(
            name=data["name"],
            joined=datetime.fromisoformat(data["joined"]),  # Convert string back to datetime
        )

    def __str__(self) -> str:
        """Return a string representation of the User object."""
        return f"User(name='{self.name}', joined={self.joined.isoformat()})"


class Address(BaseModel):
    """Nested Pydantic model for demonstration."""

    street: str
    city: str
    country: str
    postal_code: Optional[str] = None


class UserModel(BaseModel):
    """Example of a Pydantic model - works automatically with Redis structures."""

    name: str
    email: str
    age: int = Field(gt=0, lt=150)
    joined: datetime
    address: Optional[Address] = None
    tags: Set[str] = set()

    def __str__(self) -> str:
        """Return a string representation of the UserModel instance."""
        return f"UserModel(name='{self.name}', email='{self.email}', age={self.age})"


# Initialize data structures
cache = LRUCache("test_cache", capacity=1000)  # Using default connection settings
hash_map = HashMap("type_demo_hash")  # Using default connection settings

# Example 1: Basic Python Types
data = {
    "string": "hello",
    "integer": 42,
    "float": 3.14,
    "boolean": True,
    "none": None,
}
for key, value in data.items():
    hash_map.set(key, value)
    result = hash_map.get(key)

# Example 2: Collections
collections = {
    "tuple": (1, "two", 3.0),
    "list": [1, 2, 3, "four"],
    "set": {1, 2, 3, 4},
    "dict": {"a": 1, "b": 2},
}
for key, value in collections.items():
    hash_map.set(key, value)
    result = hash_map.get(key)

# Example 3: DateTime Types
now = datetime.now(timezone.utc)
hash_map.set("datetime", now)
result = hash_map.get("datetime")

# Example 4: Custom Type
user = User("John Doe", datetime.now(timezone.utc))
hash_map.set("custom_user", user)
result = hash_map.get("custom_user")

# Example 5: Pydantic Models
user_model = UserModel(
    name="Jane Smith",
    email="jane@example.com",
    age=30,
    joined=datetime.now(timezone.utc),
    address=Address(
        street="123 Main St",
        city="New York",
        country="USA",
        postal_code="10001",
    ),
    tags={"developer", "python"},
)

# Store in different data structures
cache.put("pydantic_user", user_model)
hash_map.set("pydantic_user", user_model)

# Retrieve and verify
cache_result = cache.get("pydantic_user")
hash_result = hash_map.get("pydantic_user")

# Example 6: Nested Structures
nested_data = {
    "user": user,
    "model": user_model,
    "list": [1, user, user_model],
    "tuple": (user, user_model),
    "dict": {
        "user": user,
        "model": user_model,
        "date": now,
    },
}
hash_map.set("nested", nested_data)
result = hash_map.get("nested")

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
