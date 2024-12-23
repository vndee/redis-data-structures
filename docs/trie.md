# Trie (Prefix Tree)

A Redis-backed trie (prefix tree) implementation perfect for building features like autocomplete, spell checking, and prefix matching. This implementation provides efficient string operations with persistent storage.

## Features

- Prefix-based word lookup
- Efficient string search operations
- Thread-safe operations
- Persistent storage with Redis
- JSON serialization for data
- Atomic operations
- Size tracking
- Clear operation
- Empty string support
- Advanced connection management with retries and circuit breaker

## Operations

| Operation    | Time Complexity | Description |
|-------------|----------------|-------------|
| `insert`    | O(m)          | Insert a word of length m |
| `search`    | O(m)          | Search for a word of length m |
| `starts_with`| O(p + n)      | Find words with prefix p (n = number of matches) |
| `delete`    | O(m)          | Delete a word of length m |
| `size`      | O(n)          | Get number of words (n = number of words) |
| `clear`     | O(n)          | Remove all words (n = number of nodes) |

## Basic Usage

```python
from redis_data_structures import Trie, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0,
    username=None,  # Optional
    password=None   # Optional
)

# Initialize trie with connection manager
trie = Trie(connection_manager=connection_manager)

# Basic operations
trie.insert('my_trie', 'hello')
trie.insert('my_trie', 'help')
trie.insert('my_trie', 'world')

# Search for words
exists = trie.search('my_trie', 'hello')  # Returns True
exists = trie.search('my_trie', 'help')   # Returns True
exists = trie.search('my_trie', 'hell')   # Returns False

# Find words with prefix
words = trie.starts_with('my_trie', 'hel')  # Returns ['hello', 'help']

# Delete a word
trie.delete('my_trie', 'hello')

# Get size and clear
size = trie.size('my_trie')
trie.clear('my_trie')

# Empty string handling
trie.insert('my_trie', '')  # Insert empty string
exists = trie.search('my_trie', '')  # Returns True
size = trie.size('my_trie')  # Returns 1 (counts empty string)
trie.delete('my_trie', '')  # Delete empty string
```

## Advanced Usage

### Connection Management

```python
from redis_data_structures import Trie, ConnectionManager
from datetime import timedelta

# Create connection manager with advanced features
connection_manager = ConnectionManager(
    host='redis.example.com',
    port=6380,
    max_connections=20,
    retry_max_attempts=5,
    circuit_breaker_threshold=10,
    circuit_breaker_timeout=timedelta(minutes=5),
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca.pem'
)

# Initialize trie with advanced connection manager
trie = Trie(connection_manager=connection_manager)

# Check connection health
health = connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
print(f"Pool: {health['connection_pool']}")
print(f"Circuit Breaker: {health['circuit_breaker']}")
```

## Example Use Cases

### 1. Autocomplete System

Perfect for implementing real-time search suggestions.

```python
from redis_data_structures import Trie, ConnectionManager
from typing import List

def get_suggestions(prefix: str) -> List[str]:
    connection_manager = ConnectionManager(host='localhost', port=6379)
    trie = Trie(connection_manager=connection_manager)
    return trie.starts_with('autocomplete', prefix)

# Add common search terms
trie.insert('autocomplete', 'python')
trie.insert('autocomplete', 'programming')
trie.insert('autocomplete', 'project')

# Get suggestions as user types
suggestions = get_suggestions('pro')  # Returns ['programming', 'project']
```

### 2. Spell Checker

Useful for implementing basic spell checking functionality.

```python
from redis_data_structures import Trie, ConnectionManager

def is_word_valid(word: str) -> bool:
    connection_manager = ConnectionManager(host='localhost', port=6379)
    trie = Trie(connection_manager=connection_manager)
    return trie.search('dictionary', word.lower())

# Add dictionary words
trie.insert('dictionary', 'apple')
trie.insert('dictionary', 'banana')

# Check spelling
is_valid = is_word_valid('apple')  # Returns True
is_valid = is_word_valid('appel')  # Returns False
```

### 3. Domain Name System

Efficient for storing and searching domain names.

```python
from redis_data_structures import Trie, ConnectionManager

def register_domain(domain: str) -> bool:
    connection_manager = ConnectionManager(host='localhost', port=6379)
    trie = Trie(connection_manager=connection_manager)
    if trie.search('domains', domain):
        return False  # Domain already exists
    return trie.insert('domains', domain)

# Register domains
register_domain('example.com')
register_domain('example.org')

# Check availability
is_taken = trie.search('domains', 'example.com')  # Returns True
```

## Implementation Details

The trie implementation uses Redis hashes to store nodes, where:
- Each node is a Redis hash containing its children
- Special marker '*' indicates end of word
- Keys are structured as `{trie_key}:{prefix}`
- Empty strings are stored in the root node
- Thread-safe operations using Redis atomic commands
- Connection management with retries and circuit breaker

## Best Practices

1. **Connection Management**
   ```python
   # Create a shared connection manager for multiple tries
   connection_manager = ConnectionManager(
       host='localhost',
       max_connections=20,
       retry_max_attempts=5
   )
   
   trie1 = Trie(connection_manager=connection_manager)
   trie2 = Trie(connection_manager=connection_manager)
   ```

2. **Error Handling**
   ```python
   try:
       trie.insert('my_trie', word)
   except Exception as e:
       logger.error(f"Error inserting word: {e}")
       # Handle error...
   ```

3. **Health Monitoring**
   ```python
   # Regular health checks
   health = connection_manager.health_check()
   if health['status'] != 'healthy':
       logger.warning(f"Connection issues: {health}")
   ```

## Common Issues

1. **Connection Issues**
   - Use connection manager's retry mechanism
   - Monitor circuit breaker status
   - Check SSL/TLS configuration
   - Verify network connectivity

2. **Performance**
   - Monitor connection pool usage
   - Configure appropriate pool size
   - Use health checks for monitoring

3. **Error Handling**
   - Implement proper retry strategies
   - Monitor circuit breaker status
   - Handle connection timeouts

## Troubleshooting

1. **Connection Problems**
   ```python
   # Check connection health
   health = connection_manager.health_check()
   print(f"Status: {health['status']}")
   print(f"Latency: {health['latency_ms']}ms")
   ```

2. **Performance Issues**
   ```python
   # Monitor connection pool
   health = connection_manager.health_check()
   print(f"Pool Status: {health['connection_pool']}")
   ```

3. **Circuit Breaker**
   ```python
   # Check circuit breaker status
   health = connection_manager.health_check()
   print(f"Circuit Breaker: {health['circuit_breaker']}")
   ```