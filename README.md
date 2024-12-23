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
- **Thread-safe Operations**
- **Persistent Storage**
- **Type Preservation**:
  - Preserves Python types (tuples, sets, bytes, datetime)
  - Support for custom types and Pydantic models
- **Performance Optimized**:
  - O(1) operations for most data structures
  - Connection pooling
  - Batch operations support
- **Production Ready**:
  - Comprehensive error handling
  - Monitoring support
  - Graceful fallbacks
- **Developer Friendly**:
  - Consistent API across all structures
  - Extensive documentation
  - Type hints
  - Both synchronous and asynchronous implementations (async coming soon)

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
  ```

### Basic Usage

```python
from redis_data_structures import Queue, Stack, PriorityQueue, Set, HashMap, Graph

# Initialize with Redis connection
queue = Queue(host='localhost', port=6379, db=0)
graph = Graph(host='localhost', port=6379, db=0)

# Basic operations
queue.push('my_queue', 'item1')
item = queue.pop('my_queue')  # Returns 'item1'

# Graph operations
graph.add_vertex('my_graph', 'v1', {'name': 'Vertex 1'})
graph.add_vertex('my_graph', 'v2', {'name': 'Vertex 2'})
graph.add_edge('my_graph', 'v1', 'v2', weight=1.5)
```

See [Usage Guide](docs/usage.md) for detailed examples of all data structures.

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

## 🔍 Implementation Details

Each data structure is optimized for its specific use case:

### Queue (FIFO)
- Uses Redis Lists (`RPUSH`/`LPOP`)
- O(1) push and pop operations
- Perfect for task queues and job processing

### Ring Buffer
- Uses Redis Lists (`LPOP`/`RPUSH`)
- O(1) push and pop operations
- Fixed-size circular buffer
- Perfect for log rotation, streaming data, and sliding windows
- Automatic overwrite of oldest items when full

### Stack (LIFO)
- Uses Redis Lists (`LPUSH`/`LPOP`)
- O(1) push and pop operations
- Reverse insertion order

### Priority Queue
- Uses Redis Sorted Sets (`ZADD`/`ZRANGE`/`ZREM`)
- O(log N) push and pop operations
- Priority-based ordering (lower number = higher priority)

### Set
- Uses Redis Sets (`SADD`/`SREM`/`SMEMBERS`)
- O(1) add and remove operations
- Guarantees uniqueness of elements
- Supports set operations (union, intersection, difference)

### Hash Map
- Uses Redis Hashes (`HSET`/`HGET`/`HDEL`)
- O(1) operations for single field access
- Perfect for storing structured data
- Field-based access and updates

### Deque
- Uses Redis Lists (`LPUSH`/`RPUSH`/`LPOP`/`RPOP`)
- O(1) operations at both ends
- Efficient for both FIFO and LIFO use cases
- Supports peek operations at both ends

### Bloom Filter
- Uses Redis Sets (`SADD`/`SREM`/`SMEMBERS`)
- O(1) add and remove operations
- Probabilistic membership testing

### LRU Cache
- Uses Redis Hashes for storage and Sorted Sets for access tracking
- O(1) get and put operations
- Automatic eviction of least recently used items
- Perfect for caching with size limits
- Preserves Python types (tuples, sets, etc.)

### Trie (Prefix tree)
- Uses Redis Sorted Sets (`ZADD`/`ZRANGE`/`ZREM`)
- O(log N) operations for prefix matching
- Perfect for hierarchical data storage

### Graph
- Uses Redis Hashes for vertex data and adjacency lists
- O(1) operations for most graph operations
- Perfect for:
  - Social networks (user relationships)
  - Dependency graphs (task dependencies)
  - Knowledge graphs (entity relationships)
- Features:
  - Directed edges with weights
  - Vertex data storage
  - Efficient neighbor lookups
  - Thread-safe operations

## 🛠️ Advanced Usage

### Connection Pooling
```python
from redis import ConnectionPool
from redis_data_structures import Queue, Stack

# Create a connection pool
pool = ConnectionPool(host='localhost', port=6379, db=0)

# Share pool across instances
queue = Queue(connection_pool=pool)
stack = Stack(connection_pool=pool)
```

### Type Preservation
```python
from datetime import datetime
from pydantic import BaseModel

# Custom Pydantic model
class User(BaseModel):
    name: str
    joined: datetime

# Store with type preservation
user = User(name="John", joined=datetime.now())
hash_map.set('users', 'john', user)

# Retrieve with types intact
john = hash_map.get('users', 'john')  # Returns User object
```

### Error Handling
```python
from redis.exceptions import RedisError

try:
    value = queue.pop('my_queue')
except RedisError as e:
    logger.error(f"Redis operation failed: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

### TTL (Time To Live)
```python
from datetime import datetime, timedelta

# Set TTL for a key
queue.set_ttl('my_queue', timedelta(seconds=10))

# Check TTL
ttl = queue.get_ttl('my_queue')
print(f"TTL remaining: {ttl} seconds")
```

## 📈 Performance Tips

1. **Use Connection Pooling**
   - Share connection pools across instances
   - Configure pool size based on workload

3. **Memory Management**
   - Monitor Redis memory usage
   - Implement TTL for temporary data
   - Use appropriate data structures

4. **Key Naming**
   - Use consistent prefixes
   - Include version in keys
   - Consider namespacing

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
