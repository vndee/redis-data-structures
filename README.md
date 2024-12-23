# Redis Data Structures

A Python package providing Redis-backed data structures for building scalable and resilient applications. This package includes implementations of common data structures that use Redis as the backend storage, making them suitable for distributed systems and applications requiring persistence.

## Documentation

- [Usage Guide](docs/usage.md) - Comprehensive guide for all data structures
- [Type Preservation](docs/type_preservation.md) - Details about Python type preservation
- [Examples](examples/) - Example code for each data structure

## Features

- Multiple data structure implementations:
  - Queue (FIFO)
  - Stack (LIFO)
  - Priority Queue
  - Set (Unique items)
  - Hash Map (Key-value pairs)
  - Deque (Double-ended queue)
  - Bloom Filter (Probabilistic membership testing)
  - Trie (Prefix tree)
  - LRU Cache (Least Recently Used cache)
- Thread-safe operations
- Timestamp tracking for all operations
- JSON serialization with type preservation for:
  - Tuples
  - Sets
  - Bytes
  - Datetime objects
- Consistent API across all data structures
- Graceful error handling
- Both synchronous implementations (async coming soon)

## Prerequisites

- Python 3.7+
- Redis server (local installation or Docker)
- Python packages:
  ```
  redis>=4.5.0
  ```

## Installation

```bash
pip install redis-data-structures
```

## Quick Start

```python
from redis_data_structures import Queue, Stack, PriorityQueue, Set, HashMap, Deque, BloomFilter, LRUCache

# Initialize data structures
queue = Queue(host='localhost', port=6379, db=0)
stack = Stack(host='localhost', port=6379, db=0)
pq = PriorityQueue(host='localhost', port=6379, db=0)
set_ds = Set(host='localhost', port=6379, db=0)
hash_map = HashMap(host='localhost', port=6379, db=0)
deque = Deque(host='localhost', port=6379, db=0)
bloom = BloomFilter(expected_elements=10000, false_positive_rate=0.01)
cache = LRUCache(capacity=1000)

# Using Queue (FIFO)
queue.push('my_queue', 'first')
queue.push('my_queue', 'second')
first = queue.pop('my_queue')  # Returns 'first'

# Using Stack (LIFO)
stack.push('my_stack', 'first')
stack.push('my_stack', 'second')
last = stack.pop('my_stack')   # Returns 'second'

# Using Priority Queue
pq.push('my_pq', 'high', priority=1)
pq.push('my_pq', 'low', priority=3)
pq.push('my_pq', 'medium', priority=2)
highest = pq.pop('my_pq')      # Returns ('high', 1)

# Using Set
set_ds.add('my_set', 'unique1')
set_ds.add('my_set', 'unique2')
set_ds.add('my_set', 'unique1')  # Won't add duplicate
members = set_ds.members('my_set')  # Returns {'unique1', 'unique2'}
exists = set_ds.contains('my_set', 'unique1')  # Returns True

# Using Hash Map
hash_map.set('my_hash', 'field1', 'value1')
hash_map.set('my_hash', 'field2', 'value2')
value = hash_map.get('my_hash', 'field1')  # Returns 'value1'
all_items = hash_map.get_all('my_hash')  # Returns {'field1': 'value1', 'field2': 'value2'}

# Using Deque (Double-ended queue)
deque.push_front('my_deque', 'front1')
deque.push_back('my_deque', 'back1')
front = deque.pop_front('my_deque')  # Returns 'front1'
back = deque.pop_back('my_deque')    # Returns 'back1'

# Using Bloom Filter (Probabilistic membership testing)
bloom.add('my_filter', 'item1')
bloom.add('my_filter', 'item2')
exists = bloom.contains('my_filter', 'item1')  # Returns True
exists = bloom.contains('my_filter', 'item3')  # Returns False (definitely not in set)

# Using LRU Cache
cache.put('my_cache', 'key1', {'name': 'John', 'age': 30})
cache.put('my_cache', 'key2', ('tuple', 'data'))  # Tuples are preserved
cache.put('my_cache', 'key3', {1, 2, 3})         # Sets are preserved
value = cache.get('my_cache', 'key1')  # Returns {'name': 'John', 'age': 30}
```

## Type Preservation

All data structures automatically preserve Python types during serialization:

```python
# Tuples are preserved
data = (1, 'two', [3])
cache.put('my_cache', 'tuple_key', data)
result = cache.get('my_cache', 'tuple_key')
print(type(result))  # <class 'tuple'>

# Sets are preserved
data = {1, 2, 3}
set_ds.add('my_set', data)
result = set_ds.members('my_set').pop()
print(type(result))  # <class 'set'>

# Datetime objects are preserved
from datetime import datetime
data = datetime.now()
hash_map.set('my_hash', 'date', data)
result = hash_map.get('my_hash', 'date')
print(type(result))  # <class 'datetime.datetime'>
```

## Common Operations

All data structures support these common operations:

```python
# Check size
size = ds.size('my_key')

# Clear all items
ds.clear('my_key')
```

## Redis Setup

### Using Docker (Recommended)
```bash
# Pull Redis image
docker pull redis:latest

# Run Redis container
docker run --name redis-ds -p 6379:6379 -d redis:latest

# Stop Redis when done
docker stop redis-ds
docker rm redis-ds
```

### Local Installation
```bash
# On macOS with Homebrew
brew services start redis

# On Ubuntu/Debian
sudo service redis-server start
```

## Implementation Details

### Queue (FIFO)
- Uses Redis Lists (`RPUSH`/`LPOP`)
- O(1) push and pop operations
- Maintains insertion order

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

## Best Practices

### Type Preservation
1. **Consistent Types**: Always use consistent types for the same keys/fields
2. **Complex Objects**: For complex objects, consider serializing them yourself
3. **Custom Types**: For custom types, implement `__str__` and parsing methods

### Performance
1. **Batch Operations**: Use bulk operations when possible
2. **Connection Pooling**: Reuse data structure instances
3. **Key Naming**: Use consistent key naming conventions
4. **Monitoring**: Monitor Redis memory usage

### Error Handling
1. **Check Returns**: Always check return values
2. **Handle Exceptions**: Wrap operations in try-except blocks
3. **Logging**: Enable Redis logging for debugging

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.