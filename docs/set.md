# Set

A Redis-backed set implementation that maintains a collection of unique elements. Perfect for managing unique items, tracking membership, and implementing set operations.

## Features

- O(1) operations for add/remove/contains
- Unique element storage
- Thread-safe operations
- Persistent storage
- Connection pooling and retries
- Circuit breaker pattern
- Health monitoring

## Basic Usage

```python
from redis_data_structures import Set, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create set with connection manager
s = Set(connection_manager=connection_manager)

# Add items (duplicates are ignored)
s.add('users', 'user1')
s.add('users', 'user2')
s.add('users', 'user1')  # Ignored

# Check membership
exists = s.contains('users', 'user1')  # Returns True

# Remove items
s.remove('users', 'user1')

# Get all items
items = s.get_all('users')

# Get size
size = s.size('users')

# Clear the set
s.clear('users')
```

## Advanced Usage

```python
from redis_data_structures import Set, ConnectionManager
from datetime import datetime, timedelta

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

# Create set with connection manager
s = Set(connection_manager=connection_manager)

# Store complex types
user = {
    'id': 'user1',
    'name': 'Alice',
    'joined': datetime.now(),
    'metadata': {'role': 'admin'}
}
s.add('active_users', user)

# Set operations
s.add_many('set1', ['a', 'b', 'c'])
s.add_many('set2', ['b', 'c', 'd'])

# Union
union = s.union(['set1', 'set2'])  # {'a', 'b', 'c', 'd'}

# Intersection
intersection = s.intersection(['set1', 'set2'])  # {'b', 'c'}

# Difference
difference = s.difference('set1', 'set2')  # {'a'}

# Monitor health
health = connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
```

## Example Use Cases

### 1. User Session Manager

```python
from redis_data_structures import Set, ConnectionManager
from datetime import datetime

class SessionManager:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.active = Set(connection_manager=self.connection_manager)
        self.active_key = 'active_sessions'
    
    def add_session(self, session_id: str, user_data: dict):
        """Add an active session."""
        session = {
            'id': session_id,
            'user_data': user_data,
            'started': datetime.now().isoformat()
        }
        self.active.add(self.active_key, session)
    
    def remove_session(self, session_id: str):
        """Remove a session."""
        self.active.remove(self.active_key, session_id)
    
    def is_active(self, session_id: str) -> bool:
        """Check if session is active."""
        return self.active.contains(self.active_key, session_id)
    
    def get_active_sessions(self) -> list:
        """Get all active sessions."""
        return self.active.get_all(self.active_key)

# Usage
sessions = SessionManager()
sessions.add_session('sess123', {'user_id': 'user1'})
is_active = sessions.is_active('sess123')
```

### 2. Tag System

```python
from redis_data_structures import Set, ConnectionManager
import json

class TagSystem:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.tags = Set(connection_manager=self.connection_manager)
    
    def add_tags(self, item_id: str, tags: list):
        """Add tags to an item."""
        self.tags.add_many(f'item:{item_id}:tags', tags)
    
    def remove_tag(self, item_id: str, tag: str):
        """Remove a tag from an item."""
        self.tags.remove(f'item:{item_id}:tags', tag)
    
    def get_tags(self, item_id: str) -> list:
        """Get all tags for an item."""
        return self.tags.get_all(f'item:{item_id}:tags')
    
    def find_common_tags(self, item1: str, item2: str) -> list:
        """Find common tags between items."""
        return self.tags.intersection([
            f'item:{item1}:tags',
            f'item:{item2}:tags'
        ])

# Usage
tag_system = TagSystem()
tag_system.add_tags('post1', ['python', 'redis', 'database'])
tag_system.add_tags('post2', ['python', 'async', 'database'])
common = tag_system.find_common_tags('post1', 'post2')  # ['python', 'database']
```

## Best Practices

1. **Connection Management**
   ```python
   # Create a shared connection manager
   connection_manager = ConnectionManager(
       host='localhost',
       max_connections=20,
       retry_max_attempts=5
   )
   
   # Reuse for multiple sets
   set1 = Set(connection_manager=connection_manager)
   set2 = Set(connection_manager=connection_manager)
   ```

2. **Error Handling**
   ```python
   try:
       s.add('users', user_data)
   except Exception as e:
       logger.error(f"Error adding user: {e}")
       # Handle error...
   ```

3. **Health Monitoring**
   ```python
   # Regular health checks
   health = connection_manager.health_check()
   if health['status'] != 'healthy':
       logger.warning(f"Connection issues: {health}")
   ```

## Implementation Details

- Uses Redis sets for storage
- O(1) membership testing
- Atomic operations for thread safety
- Connection pooling for performance
- Automatic reconnection with backoff
- Circuit breaker for fault tolerance
- JSON serialization for complex types

## Troubleshooting

1. **Connection Issues**
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

3. **Memory Usage**
   ```python
   # Monitor set size
   size = s.size('users')
   print(f"Current size: {size}")
   ```
