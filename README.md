# Redis Data Structures

A Python package providing Redis-backed data structures for building scalable and resilient applications. This package includes implementations of common data structures that use Redis as the backend storage, making them suitable for distributed systems and applications requiring persistence.

## Features

- Multiple data structure implementations:
  - Queue (FIFO)
  - Stack (LIFO)
  - Priority Queue
  - Set (Unique items)
  - Hash Map (Key-value pairs)
  - Deque (Double-ended queue)
- Thread-safe operations
- Timestamp tracking for all operations
- JSON serialization for complex data types
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
from redis_data_structures import Queue, Stack, PriorityQueue, Set, HashMap, Deque

# Initialize data structures
queue = Queue(host='localhost', port=6379, db=0)
stack = Stack(host='localhost', port=6379, db=0)
pq = PriorityQueue(host='localhost', port=6379, db=0)
set_ds = Set(host='localhost', port=6379, db=0)
hash_map = HashMap(host='localhost', port=6379, db=0)
deque = Deque(host='localhost', port=6379, db=0)

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

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.