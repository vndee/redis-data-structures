# Hash Map

A Redis-backed hash map implementation that provides persistent key-value storage with type preservation. Perfect for caching, metadata storage, and managing structured data.

## Features

- Key-value storage with type preservation
- O(1) operations for get/set
- Thread-safe operations
- Persistent storage
- Connection pooling and retries
- Circuit breaker pattern
- Health monitoring

## Basic Usage

```python
from redis_data_structures import HashMap, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create hash map with connection manager
hm = HashMap(connection_manager=connection_manager)

# Store key-value pairs
hm.set('users', 'user1', {'name': 'Alice', 'age': 30})
hm.set('users', 'user2', {'name': 'Bob', 'age': 25})

# Get values
user = hm.get('users', 'user1')
print(f"Name: {user['name']}, Age: {user['age']}")

# Check existence
exists = hm.exists('users', 'user1')  # Returns True

# Delete key-value pairs
hm.delete('users', 'user1')

# Get all keys and values
all_users = hm.get_all('users')
user_ids = hm.get_fields('users')

# Clear the hash map
hm.clear('users')
```

## Advanced Usage

```python
from redis_data_structures import HashMap, ConnectionManager
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

# Create hash map with connection manager
hm = HashMap(connection_manager=connection_manager)

# Store complex types
data = {
    'name': 'Charlie',
    'joined': datetime.now(),
    'metadata': {
        'role': 'admin',
        'status': 'active',
        'permissions': ['read', 'write', 'delete']
    }
}
hm.set('users', 'user3', data)

# Batch operations
users = {
    'user4': {'name': 'David', 'age': 28},
    'user5': {'name': 'Eve', 'age': 32}
}
for user_id, user_data in users.items():
    hm.set('users', user_id, user_data)

# Monitor health
health = connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
```

## Example Use Cases

### 1. User Session Store

```python
from redis_data_structures import HashMap, ConnectionManager
from datetime import datetime, timedelta

class SessionStore:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.hm = HashMap(connection_manager=self.connection_manager)
        self.store_key = 'sessions'
    
    def create_session(self, session_id: str, user_data: dict):
        """Create a new session."""
        session = {
            'user_data': user_data,
            'created_at': datetime.now(),
            'last_accessed': datetime.now()
        }
        self.hm.set(self.store_key, session_id, session)
    
    def get_session(self, session_id: str) -> dict:
        """Get session data and update last accessed time."""
        session = self.hm.get(self.store_key, session_id)
        if session:
            session['last_accessed'] = datetime.now()
            self.hm.set(self.store_key, session_id, session)
        return session
    
    def delete_session(self, session_id: str):
        """Delete a session."""
        self.hm.delete(self.store_key, session_id)

# Usage
store = SessionStore()
store.create_session('sess123', {'user_id': 'user1', 'name': 'Alice'})
session = store.get_session('sess123')
```

### 2. Configuration Store

```python
from redis_data_structures import HashMap, ConnectionManager
import json

class ConfigStore:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.hm = HashMap(connection_manager=self.connection_manager)
        self.store_key = 'config'
    
    def set_config(self, app_id: str, config: dict):
        """Set configuration for an app."""
        config['updated_at'] = datetime.now().isoformat()
        self.hm.set(self.store_key, app_id, config)
    
    def get_config(self, app_id: str) -> dict:
        """Get app configuration."""
        return self.hm.get(self.store_key, app_id)
    
    def update_config(self, app_id: str, updates: dict):
        """Update specific config values."""
        config = self.get_config(app_id) or {}
        config.update(updates)
        self.set_config(app_id, config)

# Usage
config_store = ConfigStore()
config_store.set_config('app1', {
    'debug': True,
    'api_key': 'secret',
    'max_connections': 100
})
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
   
   # Reuse for multiple hash maps
   hm1 = HashMap(connection_manager=connection_manager)
   hm2 = HashMap(connection_manager=connection_manager)
   ```

2. **Error Handling**
   ```python
   try:
       hm.set('users', user_id, user_data)
   except Exception as e:
       logger.error(f"Error storing user data: {e}")
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

- Uses Redis hashes for storage
- Automatic type preservation
- JSON serialization for complex types
- Atomic operations for thread safety
- Connection pooling for performance
- Automatic reconnection with backoff
- Circuit breaker for fault tolerance

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
   # Monitor hash size
   fields = hm.get_fields('users')
   print(f"Number of fields: {len(fields)}")
   ```
