# Stack (LIFO)

A Redis-backed LIFO (Last-In-First-Out) stack implementation. Perfect for managing execution contexts, undo operations, and any application requiring last-in-first-out processing.

## Features

- O(1) push and pop operations
- LIFO ordering
- Thread-safe operations
- Persistent storage
- Connection pooling and retries
- Circuit breaker pattern
- Health monitoring

## Basic Usage

```python
from redis_data_structures import Stack, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create stack with connection manager
stack = Stack(connection_manager=connection_manager)

# Add items
stack.push('commands', 'command1')
stack.push('commands', 'command2')

# Get items (LIFO order)
command = stack.pop('commands')  # Returns 'command2'

# Check size
size = stack.size('commands')

# Clear the stack
stack.clear('commands')
```

## Advanced Usage

```python
from redis_data_structures import Stack, ConnectionManager
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

# Create stack with connection manager
stack = Stack(connection_manager=connection_manager)

# Store complex types
command = {
    'id': 'cmd1',
    'action': 'update_user',
    'timestamp': datetime.now(),
    'data': {'user_id': 123, 'changes': {'name': 'Alice'}}
}
stack.push('commands', command)

# Peek at top item without removing
next_command = stack.peek('commands')

# Monitor health
health = connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
```

## Example Use Cases

### 1. Command History

```python
from redis_data_structures import Stack, ConnectionManager
from datetime import datetime

class CommandHistory:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.history = Stack(connection_manager=self.connection_manager)
        self.history_key = 'command_history'
    
    def add_command(self, command: dict):
        """Add a command to history."""
        command['timestamp'] = datetime.now().isoformat()
        self.history.push(self.history_key, command)
    
    def undo_last_command(self) -> dict:
        """Get and remove last command."""
        return self.history.pop(self.history_key)
    
    def peek_last_command(self) -> dict:
        """Preview last command without removing."""
        return self.history.peek(self.history_key)

# Usage
history = CommandHistory()
history.add_command({'action': 'update', 'data': {'id': 1}})
last_command = history.undo_last_command()
```

### 2. Navigation History

```python
from redis_data_structures import Stack, ConnectionManager
import json

class NavigationHistory:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.stack = Stack(connection_manager=self.connection_manager)
        self.stack_key = 'navigation'
    
    def push_page(self, page: dict):
        """Add a page to history."""
        page['visited_at'] = datetime.now().isoformat()
        self.stack.push(self.stack_key, page)
    
    def go_back(self) -> dict:
        """Navigate to previous page."""
        return self.stack.pop(self.stack_key)
    
    def current_page(self) -> dict:
        """Get current page."""
        return self.stack.peek(self.stack_key)

# Usage
nav = NavigationHistory()
nav.push_page({'url': '/home', 'title': 'Home'})
nav.push_page({'url': '/products', 'title': 'Products'})
previous = nav.go_back()  # Returns to Home page
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
   
   # Reuse for multiple stacks
   stack1 = Stack(connection_manager=connection_manager)
   stack2 = Stack(connection_manager=connection_manager)
   ```

2. **Error Handling**
   ```python
   try:
       stack.push('commands', command)
   except Exception as e:
       logger.error(f"Error adding command: {e}")
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

- Uses Redis lists for storage
- LIFO ordering
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
   # Monitor stack size
   size = stack.size('commands')
   print(f"Current size: {size}")
   ```
