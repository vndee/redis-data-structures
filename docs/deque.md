# Deque (Double-ended Queue)

A Redis-backed double-ended queue implementation that allows efficient insertion and removal of elements from both ends. Perfect for implementing work queues, sliding windows, and other algorithms requiring double-ended operations.

## Features

- O(1) operations at both ends
- Thread-safe operations
- Persistent storage
- Automatic type preservation
- Connection pooling and retries
- Circuit breaker pattern
- Health monitoring

## Basic Usage

```python
from redis_data_structures import Deque, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create deque with connection manager
deque = Deque(connection_manager=connection_manager)

# Add elements at both ends
deque.append_left('my_deque', 'first')
deque.append('my_deque', 'last')

# Remove elements from both ends
first = deque.pop_left('my_deque')  # Returns 'first'
last = deque.pop('my_deque')        # Returns 'last'

# Check size
size = deque.size('my_deque')

# Clear the deque
deque.clear('my_deque')
```

## Advanced Usage

```python
from redis_data_structures import Deque, ConnectionManager
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

# Create deque with connection manager
deque = Deque(connection_manager=connection_manager)

# Store complex types
data = {
    'timestamp': datetime.now(),
    'value': 42,
    'metadata': {'type': 'sensor_reading'}
}
deque.append('my_deque', data)

# Peek without removing
left = deque.peek_left('my_deque')
right = deque.peek('my_deque')

# Monitor health
health = connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
```

## Example Use Cases

### 1. Sliding Window

```python
from redis_data_structures import Deque, ConnectionManager
from datetime import datetime, timedelta

def process_sliding_window(window_size: int = 1000):
    connection_manager = ConnectionManager(host='localhost', port=6379)
    window = Deque(connection_manager=connection_manager)
    
    # Add new data point
    data = {'timestamp': datetime.now(), 'value': 42}
    window.append('sliding_window', data)
    
    # Remove old data points
    while window.size('sliding_window') > window_size:
        window.pop_left('sliding_window')
    
    # Process window data
    all_data = window.get_all('sliding_window')
    return all_data
```

### 2. Work Queue

```python
from redis_data_structures import Deque, ConnectionManager
import json

class WorkQueue:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.deque = Deque(connection_manager=self.connection_manager)
        self.queue_key = 'work_queue'
    
    def add_task(self, task: dict):
        """Add task to either end based on priority."""
        if task.get('priority') == 'high':
            self.deque.append_left(self.queue_key, task)
        else:
            self.deque.append(self.queue_key, task)
    
    def get_task(self) -> dict:
        """Get next task from queue."""
        return self.deque.pop_left(self.queue_key)
    
    def peek_next_task(self) -> dict:
        """Preview next task without removing."""
        return self.deque.peek_left(self.queue_key)

# Usage
queue = WorkQueue()
queue.add_task({'id': 1, 'priority': 'high'})
queue.add_task({'id': 2, 'priority': 'low'})
task = queue.get_task()  # Returns high priority task first
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
   
   # Reuse for multiple deques
   deque1 = Deque(connection_manager=connection_manager)
   deque2 = Deque(connection_manager=connection_manager)
   ```

2. **Error Handling**
   ```python
   try:
       deque.append('my_deque', item)
   except Exception as e:
       logger.error(f"Error adding item: {e}")
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
   # Monitor deque size
   size = deque.size('my_deque')
   print(f"Current size: {size}")
   ``` 