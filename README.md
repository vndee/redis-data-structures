# Redis Data Structures

[![PyPI version](https://badge.fury.io/py/redis-data-structures.svg)](https://badge.fury.io/py/redis-data-structures)
[![Python Versions](https://img.shields.io/pypi/pyversions/redis-data-structures.svg)](https://pypi.org/project/redis-data-structures/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/redis-data-structures/badge/?version=latest)](https://redis-data-structures.readthedocs.io/en/latest/?badge=latest)

A Python package providing Redis-backed implementations of common data structures for building scalable and resilient applications. This package offers thread-safe, persistent, and distributed data structures built on top of Redis, making them perfect for microservices, distributed systems, and applications requiring persistence.

## 🌟 Key Features

- **Rich Data Structure Support**:
  - Queue (FIFO)
  - Stack (LIFO)
  - Priority Queue
  - Set (Unique items)
  - Hash Map (Key-value pairs)
  - Deque (Double-ended queue)
  - Bloom Filter (Probabilistic membership testing)
  - Trie (Prefix tree)
  - LRU Cache (Least Recently Used cache)
  - Graph (Directed graph with weighted edges)
  - Ring Buffer (Fixed-size circular buffer)

- **Advanced Connection Management**:
  - Connection pooling with configurable pool size
  - Automatic reconnection with exponential backoff
  - Circuit breaker pattern for fault tolerance
  - Health checks
  - SSL/TLS support

- **Robust Error Handling**:
  - Custom exception hierarchy
  - Proper logging and error tracking
  - Graceful fallbacks
  - Comprehensive error messages

- **Configuration Management**:
  - Environment variable support
  - YAML configuration files
  - Dynamic configuration updates
  - Type-safe configuration with validation

- **Performance Features**:
  - O(1) operations for most data structures
  - Connection pooling
  - Batch operations support
  - Data compression
  - Automatic type preservation

- **Type System**:
  - Automatic type preservation
  - Custom type support
  - Pydantic integration
  - Built-in support for datetime, bytes, etc.
  - Nested type support

## 📚 Documentation

- [Usage Guide](docs/usage.md) - Comprehensive guide for all data structures
- [Examples](examples/) - Example code for each data structure

## 🚀 Quick Start

### Installation

```bash
pip install redis-data-structures
```

### Prerequisites

- Python 3.7+
- Redis server (local installation or Docker)
- Dependencies:
  ```
  redis>=4.5.0
  pydantic>=2.0.0  # Optional, for enhanced type support
  mmh3>=5.0.1  # Optional, for BloomFilter
  pyyaml>=6.0  # Optional, for YAML configuration
  ```

### Basic Usage

```python
from redis_data_structures import Queue, Stack, PriorityQueue, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host="localhost",
    port=6379,
    db=0,
    max_connections=10
)

# Initialize data structures with connection manager
queue = Queue(connection_manager=connection_manager)
stack = Stack(connection_manager=connection_manager)

# Basic operations
queue.push('my_queue', 'item1')
item = queue.pop('my_queue')  # Returns 'item1'

# With type preservation
from datetime import datetime
stack.push('my_stack', {'timestamp': datetime.now(), 'value': 42})
data = stack.pop('my_stack')  # Returns dict with datetime preserved
```

### Advanced Usage

```python
from redis_data_structures import Graph, ConnectionManager, CustomRedisDataType
from datetime import datetime, timedelta

# Custom type example
class User(CustomRedisDataType):
    def __init__(self, name: str, joined: datetime):
        self.name = name
        self.joined = joined

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "joined": self.joined.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(
            name=data["name"],
            joined=datetime.fromisoformat(data["joined"])
        )

# Create connection manager with advanced settings
connection_manager = ConnectionManager(
    host="redis.example.com",
    port=6380,
    max_connections=20,
    retry_max_attempts=5,
    circuit_breaker_threshold=10,
    circuit_breaker_timeout=timedelta(minutes=5),
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca.pem'
)

# Initialize graph with connection manager
graph = Graph(connection_manager=connection_manager)

# Add vertices with custom type
user1 = User("Alice", datetime.now())
user2 = User("Bob", datetime.now())

graph.add_vertex('my_graph', 'v1', user1)
graph.add_vertex('my_graph', 'v2', user2)
graph.add_edge('my_graph', 'v1', 'v2', weight=1.5)

# Get vertex data (automatically deserializes to User object)
alice = graph.get_vertex_data('my_graph', 'v1')
print(f"User: {alice.name}, Joined: {alice.joined}")
```

## 🔧 Redis Setup

### Using Docker (Recommended)
```bash
# Pull and run Redis
docker run --name redis-ds -p 6379:6379 -d redis:latest
```

### Local Installation
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server
```

## 🔍 Configuration

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
```

## 🛠️ Advanced Features

### Connection Management
```python
from redis_data_structures import Queue, ConnectionManager
from datetime import timedelta

# Custom connection manager
connection_manager = ConnectionManager(
    host="localhost",
    max_connections=20,
    retry_max_attempts=5,
    circuit_breaker_threshold=10,
    circuit_breaker_timeout=timedelta(minutes=5),
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca.pem'
)

# Initialize data structure with connection manager
queue = Queue(connection_manager=connection_manager)

# Check connection health
health = connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
print(f"Pool: {health['connection_pool']}")
print(f"Circuit Breaker: {health['circuit_breaker']}")
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Redis team for the amazing database
- All our contributors
- Python community

## 📬 Support

- 🐛 [Report bugs](https://github.com/vndee/redis-data-structures/issues)
- 💡 [Request features](https://github.com/vndee/redis-data-structures/issues)
