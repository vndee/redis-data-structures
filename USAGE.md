# Redis Data Structures

A Python package providing Redis-backed implementations of common data structures. This package offers thread-safe, persistent, and scalable data structures built on top of Redis.

## Installation

```bash
pip install redis-data-structures
```

## Quick Start

```python
from redis_data_structures import Queue, Stack, PriorityQueue, Set, HashMap, Deque, BloomFilter, Trie

# Initialize any data structure
queue = Queue(host='localhost', port=6379)
queue.push('my_queue', 'item1')
item = queue.pop('my_queue')
```

## Available Data Structures

### [Queue (FIFO)](docs/queue.md)
- First-In-First-Out queue implementation
- Perfect for task queues, message processing, and job scheduling
- [View detailed documentation](docs/queue.md)

### [Stack (LIFO)](docs/stack.md)
- Last-In-First-Out stack implementation
- Ideal for undo/redo operations, parsing, and depth-first algorithms
- [View detailed documentation](docs/stack.md)

### [Priority Queue](docs/priority_queue.md)
- Queue with priority-based ordering
- Great for task scheduling, emergency systems, and resource allocation
- [View detailed documentation](docs/priority_queue.md)

### [Set](docs/set.md)
- Collection of unique elements
- Perfect for tracking unique items, managing sessions, and filtering duplicates
- [View detailed documentation](docs/set.md)

### [Hash Map](docs/hash_map.md)
- Key-value store with field-based access
- Ideal for user profiles, configuration management, and structured data
- [View detailed documentation](docs/hash_map.md)

### [Deque](docs/deque.md)
- Double-ended queue implementation
- Perfect for sliding windows, browser history, and work-stealing algorithms
- [View detailed documentation](docs/deque.md)

### [Bloom Filter](docs/bloom_filter.md)
- Space-efficient probabilistic data structure
- Ideal for reducing unnecessary lookups, deduplication, and caching optimization
- [View detailed documentation](docs/bloom_filter.md)

### [Trie](docs/trie.md)
- Prefix tree implementation for efficient string operations
- Perfect for autocomplete, spell checking, and prefix matching
- Supports empty string storage
- [View detailed documentation](docs/trie.md)

## Common Features

All data structures share these features:
- Thread-safe operations
- Persistent storage with Redis
- JSON serialization for complex data types
- Atomic operations
- Size tracking
- Clear operation

## Basic Connection

All data structures accept these connection parameters:
```python
structure = DataStructure(
    host='localhost',      # Redis host
    port=6379,            # Redis port
    db=0,                 # Redis database
    username=None,        # Optional username
    password=None,        # Optional password
    socket_timeout=None,  # Optional timeout
    socket_connect_timeout=None,  # Optional connection timeout
    socket_keepalive=None,       # Optional keepalive
    socket_keepalive_options=None,  # Optional keepalive options
    connection_pool=None,        # Optional connection pool
    unix_socket_path=None,       # Optional Unix socket path
    encoding='utf-8',            # Optional encoding
    encoding_errors='strict',    # Optional encoding error handling
    decode_responses=True,       # Optional response decoding
    retry_on_timeout=False,      # Optional timeout retry
    ssl=False,                   # Optional SSL
    ssl_keyfile=None,           # Optional SSL key file
    ssl_certfile=None,          # Optional SSL cert file
    ssl_cert_reqs='required',   # Optional SSL cert requirements
    ssl_ca_certs=None,          # Optional SSL CA certs
    max_connections=None        # Optional max connections
)
```

## Best Practices

1. **Key Management**
   - Use descriptive prefixes for keys
   - Consider implementing key expiration
   - Clear unused structures

2. **Error Handling**
   ```python
   try:
       structure.operation('key', value)
   except redis.RedisError as e:
       logger.error(f"Redis error: {e}")
       # Handle error...
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
       # Handle error...
   ```

3. **Memory Management**
   - Monitor structure sizes
   - Implement size limits where appropriate
   - Regular cleanup of old data

4. **Performance**
   - Use batch operations when possible
   - Consider cleanup strategies
   - Monitor Redis memory usage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.