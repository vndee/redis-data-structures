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
  - Health checks and monitoring
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

- **Monitoring and Observability**:
  - Operation timing metrics
  - Success/failure rate tracking
  - Performance statistics
  - Health monitoring
  - Debug logging

- **Type System**:
  - Automatic type preservation
  - Custom type support
  - Pydantic integration
  - Built-in support for datetime, bytes, etc.
  - Nested type support

- **Production Ready**:
  - Thread-safe operations
  - Persistent storage
  - Comprehensive error handling
  - Monitoring support
  - Graceful fallbacks

## 📚 Documentation

- [Usage Guide](docs/usage.md) - Comprehensive guide for all data structures
- [Type Preservation](docs/type_preservation.md) - Details about Python type preservation
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
from redis_data_structures import Queue, Stack, PriorityQueue, Config

# Initialize with default configuration
queue = Queue()

# Initialize with custom configuration
config = Config.from_env()  # Load from environment variables
# or
config = Config.from_yaml('config.yaml')  # Load from YAML file

stack = Stack(config=config)

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
from redis_data_structures import Graph, Config, CustomRedisDataType
from datetime import datetime

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

# Create configuration
config = Config.from_env()
config.data_structures.compression_enabled = True
config.data_structures.debug_enabled = True

# Initialize graph with configuration
graph = Graph(config=config)

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

data_structures:
  prefix: myapp
  compression_enabled: true
  compression_threshold: 1024
  metrics_enabled: true
  debug_enabled: true
```

## 📈 Monitoring

```python
from redis_data_structures import Queue, MetricsCollector
from datetime import timedelta

queue = Queue()

# Get metrics for last 5 minutes
metrics = MetricsCollector()
stats = metrics.get_metrics("Queue").get_stats(window=timedelta(minutes=5))

print(f"Total operations: {stats['total_operations']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"Average duration: {stats['avg_duration_ms']}ms")
print(f"Error count: {stats['error_count']}")
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
    circuit_breaker_timeout=timedelta(minutes=5)
)

queue = Queue(connection_manager=connection_manager)
```

### Type Registry
```python
from redis_data_structures import TypeRegistry, CustomRedisDataType

# Register custom type
class Point(CustomRedisDataType):
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: dict) -> 'Point':
        return cls(data["x"], data["y"])

registry = TypeRegistry()
registry.register(Point)
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
