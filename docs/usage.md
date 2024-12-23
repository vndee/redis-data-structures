# Redis Data Structures Usage Guide

## Table of Contents

1. [Installation](#installation)
2. [Basic Setup](#basic-setup)
3. [Data Structures](#data-structures)
   - [Queue (FIFO)](#queue)
   - [Stack (LIFO)](#stack)
   - [Priority Queue](#priority-queue)
   - [Set](#set)
   - [Hash Map](#hash-map)
   - [Deque](#deque)
   - [Bloom Filter](#bloom-filter)
   - [LRU Cache](#lru-cache)
   - [Trie](#trie)
   - [Graph](#graph)
   - [Ring Buffer](#ring-buffer)
4. [Common Features](#common-features)
5. [Connection Options](#connection-options)
6. [Advanced Topics](#advanced-topics)
   - [Type Preservation](type_preservation.md)
   - [Error Handling](#error-handling)
   - [Performance Optimization](#performance-optimization)
7. [Best Practices](#best-practices)

## Installation

```bash
pip install redis-data-structures
```

## Basic Setup

```python
from redis_data_structures import (
    Queue, Stack, PriorityQueue, Set,
    HashMap, Deque, BloomFilter, LRUCache,
    Trie, Graph, RingBuffer
)

# Common connection parameters
redis_config = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    # Optional parameters
    "username": "your_username",
    "password": "your_password",
    "socket_timeout": 5,
}
```

## Data Structures

### Queue

FIFO (First-In-First-Out) queue implementation. Perfect for task queues, message processing, and job scheduling.

```python
# Initialize
queue = Queue(**redis_config)

# Basic operations
queue.push("my_queue", "first")
queue.push("my_queue", "second")
first = queue.pop("my_queue")  # Returns "first"

# Check size
size = queue.size("my_queue")  # Returns 1

# Clear
queue.clear("my_queue")
```

### Stack

LIFO (Last-In-First-Out) stack implementation. Ideal for undo/redo operations, parsing, and depth-first algorithms.

```python
# Initialize
stack = Stack(**redis_config)

# Basic operations
stack.push("my_stack", "first")
stack.push("my_stack", "second")
last = stack.pop("my_stack")  # Returns "second"

# Check size
size = stack.size("my_stack")  # Returns 1

# Clear
stack.clear("my_stack")
```

### Priority Queue

Priority-based queue with O(log N) operations. Great for task scheduling, emergency systems, and resource allocation.

```python
# Initialize
pq = PriorityQueue(**redis_config)

# Add items with priorities (lower number = higher priority)
pq.push("my_pq", "critical task", priority=1)
pq.push("my_pq", "normal task", priority=2)
pq.push("my_pq", "low priority task", priority=3)

# Pop highest priority item
task, priority = pq.pop("my_pq")  # Returns ("critical task", 1)

# Peek without removing
task, priority = pq.peek("my_pq")  # Returns ("normal task", 2)

# Clear
pq.clear("my_pq")
```

### Set

Collection of unique items with O(1) operations. Perfect for tracking unique items, managing sessions, and filtering duplicates.

```python
# Initialize
set_ds = Set(**redis_config)

# Add items
set_ds.add("my_set", "unique1")
set_ds.add("my_set", "unique2")
set_ds.add("my_set", "unique1")  # Won't add duplicate

# Check membership
exists = set_ds.contains("my_set", "unique1")  # Returns True

# Get all members
members = set_ds.members("my_set")  # Returns {"unique1", "unique2"}

# Remove item
set_ds.remove("my_set", "unique1")

# Clear
set_ds.clear("my_set")
```

### Hash Map

Key-value store with field-based access. Ideal for user profiles, configuration management, and structured data.

```python
# Initialize
hash_map = HashMap(**redis_config)

# Set values
hash_map.set("my_hash", "field1", "value1")
hash_map.set("my_hash", "field2", {"nested": "data"})

# Get values
value = hash_map.get("my_hash", "field1")  # Returns "value1"

# Get all fields and values
all_items = hash_map.get_all("my_hash")

# Remove field
hash_map.remove("my_hash", "field1")

# Clear
hash_map.clear("my_hash")
```

### Deque

Double-ended queue with O(1) operations at both ends. Perfect for sliding windows, browser history, and work-stealing algorithms.

```python
# Initialize
deque = Deque(**redis_config)

# Add items at both ends
deque.push_front("my_deque", "front1")
deque.push_back("my_deque", "back1")

# Remove items from both ends
front = deque.pop_front("my_deque")
back = deque.pop_back("my_deque")

# Peek without removing
front = deque.peek_front("my_deque")
back = deque.peek_back("my_deque")

# Clear
deque.clear("my_deque")
```

### Bloom Filter

Space-efficient probabilistic data structure. Ideal for reducing unnecessary lookups, deduplication, and caching optimization.

```python
# Initialize with expected elements and false positive rate
bloom = BloomFilter(
    expected_elements=10000,
    false_positive_rate=0.01,
    **redis_config
)

# Add items
bloom.add("my_filter", "item1")
bloom.add("my_filter", "item2")

# Check membership
exists = bloom.contains("my_filter", "item1")  # Returns True
exists = bloom.contains("my_filter", "unknown")  # Returns False if definitely not in set

# Clear
bloom.clear("my_filter")
```

### LRU Cache

Least Recently Used cache with automatic eviction. Perfect for caching with size limits.

```python
# Initialize with capacity
cache = LRUCache(capacity=1000, **redis_config)

# Add items
cache.put("my_cache", "key1", {"name": "John", "age": 30})
cache.put("my_cache", "key2", ("tuple", "data"))  # Tuples preserved
cache.put("my_cache", "key3", {1, 2, 3})         # Sets preserved

# Get items (updates access time)
value = cache.get("my_cache", "key1")

# Peek (doesn't update access time)
value = cache.peek("my_cache", "key1")

# Get all items
all_items = cache.get_all("my_cache")

# Get items in LRU order
lru_order = cache.get_lru_order("my_cache")

# Clear
cache.clear("my_cache")
```

### Trie

Prefix tree implementation for efficient string operations. Perfect for autocomplete, spell checking, and prefix matching.

```python
# Initialize
trie = Trie(**redis_config)

# Add words
trie.insert("my_trie", "apple")
trie.insert("my_trie", "app")
trie.insert("my_trie", "application")

# Search for words
exists = trie.search("my_trie", "apple")  # Returns True

# Find words with prefix
words = trie.find_words_with_prefix("my_trie", "app")
# Returns ["app", "apple", "application"]

# Clear
trie.clear("my_trie")
```

### Graph

A Redis-backed directed graph implementation using adjacency lists. Perfect for representing relationships between entities, social networks, dependency graphs, and other connected data structures.

```python
# Initialize
graph = Graph(**redis_config)

# Add vertices with data
graph.add_vertex("my_graph", "v1", {"name": "Vertex 1", "value": 42})
graph.add_vertex("my_graph", "v2", {"name": "Vertex 2", "value": 84})

# Add weighted edges
graph.add_edge("my_graph", "v1", "v2", weight=1.5)

# Get vertex data
data = graph.get_vertex_data("my_graph", "v1")

# Get neighbors with weights
neighbors = graph.get_neighbors("my_graph", "v1")

# Remove vertex (and all its edges)
graph.remove_vertex("my_graph", "v1")

# Clear
graph.clear("my_graph")
```

### Ring Buffer

Fixed-size circular buffer implementation. Perfect for log rotation, streaming data processing, and sliding window analytics.

```python
# Initialize ring buffer with capacity
buffer = RingBuffer(
    capacity=1000,  # Maximum number of items
    host='localhost',
    port=6379,
    db=0,
    username=None,  # Optional
    password=None   # Optional
)

# Add items (overwrites oldest when full)
buffer.push('my_buffer', 'item1')
buffer.push('my_buffer', {'complex': 'item'})

# Get all items (oldest to newest)
items = buffer.get_all('my_buffer')

# Get latest 5 items (newest to oldest)
latest = buffer.get_latest('my_buffer', 5)

# Get current size
size = buffer.size('my_buffer')

# Clear buffer
buffer.clear('my_buffer')
```

Example use cases:

1. Log Rotation
```python
class LogRotator:
    def __init__(self, max_logs: int = 1000):
        self.buffer = RingBuffer(capacity=max_logs, host='localhost', port=6379)
        self.log_key = 'app:logs'
    
    def log(self, level: str, message: str):
        """Add a log entry."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.buffer.push(self.log_key, entry)
    
    def get_recent_logs(self, n: int = 100) -> list:
        """Get most recent log entries."""
        return self.buffer.get_latest(self.log_key, n)

# Usage
logger = LogRotator(max_logs=1000)
logger.log('INFO', 'Application started')
recent_logs = logger.get_recent_logs(10)  # Get last 10 logs
```

2. Streaming Data
```python
class DataStream:
    def __init__(self, window_size: int):
        self.buffer = RingBuffer(capacity=window_size, host='localhost', port=6379)
        self.stream_key = 'data:stream'
    
    def add_datapoint(self, value: float):
        """Add a data point to the stream."""
        data = {'value': value, 'timestamp': time.time()}
        self.buffer.push(self.stream_key, data)
    
    def get_window(self) -> list:
        """Get all data points in the current window."""
        return self.buffer.get_all(self.stream_key)

# Usage
stream = DataStream(window_size=100)  # Keep last 100 points
stream.add_datapoint(42.0)
window_data = stream.get_window()
```

## Common Features

All data structures share these features:
- Thread-safe operations
- Persistent storage with Redis
- JSON serialization for complex data types
- Atomic operations
- Size tracking
- Clear operation

## Connection Options

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

## Advanced Topics

### Error Handling

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

### Performance Optimization

1. **Use Connection Pooling**
   ```python
   from redis import ConnectionPool
   
   pool = ConnectionPool(**redis_config)
   structure = DataStructure(connection_pool=pool)
   ```

2. **Batch Operations**
   - Use multi-key operations when possible
   - Consider pipeline for multiple operations

3. **Memory Management**
   - Monitor Redis memory usage
   - Implement cleanup strategies
   - Use TTL for temporary data

## Best Practices

1. **Key Management**
   - Use descriptive key prefixes
   - Consider implementing key expiration
   - Clear unused structures

2. **Error Handling**
   - Always wrap Redis operations in try-except
   - Log errors appropriately
   - Implement retry mechanisms for timeouts

3. **Memory Management**
   - Monitor structure sizes
   - Implement size limits where appropriate
   - Regular cleanup of old data

4. **Performance**
   - Use batch operations when possible
   - Consider cleanup strategies
   - Monitor Redis memory usage