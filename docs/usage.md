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
4. [Advanced Topics](#advanced-topics)
   - [Type Preservation](type_preservation.md)
   - [Error Handling](#error-handling)
   - [Performance Optimization](#performance-optimization)
5. [Best Practices](#best-practices)

## Installation

```bash
pip install redis-data-structures
```

## Basic Setup

```python
from redis_data_structures import (
    Queue, Stack, PriorityQueue, Set,
    HashMap, Deque, BloomFilter, LRUCache
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

FIFO (First-In-First-Out) queue implementation.

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

LIFO (Last-In-First-Out) stack implementation.

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

Priority-based queue with O(log N) operations.

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

Collection of unique items with O(1) operations.

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

Key-value store with field-based access.

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

Double-ended queue with O(1) operations at both ends.

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

Probabilistic membership testing with no false negatives.

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

Least Recently Used cache with automatic eviction.

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

## Advanced Topics

### Error Handling

```python
try:
    value = cache.get("my_cache", "key")
    if value is None:
        # Handle cache miss
        value = fetch_from_database()
        cache.put("my_cache", "key", value)
except redis.RedisError as e:
    # Handle Redis connection/operation errors
    logger.error(f"Redis error: {e}")
except Exception as e:
    # Handle other errors
    logger.error(f"Unexpected error: {e}")
```

### Performance Optimization

1. **Connection Pooling**
```python
from redis import ConnectionPool

pool = ConnectionPool(**redis_config)
redis_config["connection_pool"] = pool

# All data structures will use the same connection pool
cache1 = LRUCache(**redis_config)
cache2 = LRUCache(**redis_config)
```

2. **Batch Operations**
```python
# Use pipeline for multiple operations
with cache.redis_client.pipeline() as pipe:
    pipe.multi()
    pipe.hset("key1", "field1", "value1")
    pipe.hset("key2", "field2", "value2")
    pipe.execute()
```

## Best Practices

1. **Key Naming Conventions**
```python
# Use consistent prefixes
USER_PREFIX = "user:"
CACHE_PREFIX = "cache:"

# Use descriptive names
cache.put(f"{CACHE_PREFIX}user_profile", user_id, profile_data)
cache.put(f"{CACHE_PREFIX}user_settings", user_id, settings_data)
```

2. **TTL (Time To Live)**
```python
# Set expiration on keys
cache.redis_client.expire("my_key", 3600)  # Expires in 1 hour
```

3. **Memory Management**
```python
# Monitor memory usage
info = cache.redis_client.info("memory")
used_memory = info["used_memory_human"]
print(f"Used memory: {used_memory}")
```

4. **Type Safety**
```python
from typing import TypedDict, Optional

class UserProfile(TypedDict):
    name: str
    age: int
    email: str

def get_user_profile(user_id: str) -> Optional[UserProfile]:
    return cache.get(f"{USER_PREFIX}{user_id}")
```

For more detailed information about type preservation, see [Type Preservation](type_preservation.md). 