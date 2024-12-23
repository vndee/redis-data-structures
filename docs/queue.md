# Queue (FIFO)

A Redis-backed FIFO (First-In-First-Out) queue implementation. Perfect for job queues, message passing, and any application requiring ordered processing of items.

## Features

- O(1) push and pop operations
- FIFO ordering
- Thread-safe operations
- Persistent storage
- Connection pooling and retries
- Circuit breaker pattern
- Health monitoring

## Basic Usage

```python
from redis_data_structures import Queue, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create queue with connection manager
queue = Queue(connection_manager=connection_manager)

# Add items
queue.push('tasks', 'task1')
queue.push('tasks', 'task2')

# Get items (FIFO order)
task = queue.pop('tasks')  # Returns 'task1'

# Check size
size = queue.size('tasks')

# Clear the queue
queue.clear('tasks')
```

## Advanced Usage

```python
from redis_data_structures import Queue, ConnectionManager
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

# Create queue with connection manager
queue = Queue(connection_manager=connection_manager)

# Store complex types
task = {
    'id': 'task1',
    'type': 'process_data',
    'created_at': datetime.now(),
    'data': {'user_id': 123, 'action': 'update'}
}
queue.push('tasks', task)

# Peek at next item without removing
next_task = queue.peek('tasks')

# Monitor health
health = connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
```

## Example Use Cases

### 1. Message Queue

```python
from redis_data_structures import Queue, ConnectionManager
from datetime import datetime

class MessageQueue:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.queue = Queue(connection_manager=self.connection_manager)
        self.queue_key = 'messages'
    
    def send_message(self, message: dict):
        """Send a message to the queue."""
        message['timestamp'] = datetime.now().isoformat()
        self.queue.push(self.queue_key, message)
    
    def receive_message(self) -> dict:
        """Get next message from queue."""
        return self.queue.pop(self.queue_key)
    
    def peek_message(self) -> dict:
        """Preview next message without removing."""
        return self.queue.peek(self.queue_key)

# Usage
mq = MessageQueue()
mq.send_message({'type': 'notification', 'user_id': 123})
message = mq.receive_message()
```

### 2. Task Processor

```python
from redis_data_structures import Queue, ConnectionManager
import json

class TaskProcessor:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.queue = Queue(connection_manager=self.connection_manager)
        self.queue_key = 'tasks'
    
    def add_task(self, task: dict):
        """Add a task to the queue."""
        task['queued_at'] = datetime.now().isoformat()
        self.queue.push(self.queue_key, task)
    
    def process_tasks(self, batch_size: int = 10) -> list:
        """Process a batch of tasks."""
        tasks = []
        for _ in range(batch_size):
            task = self.queue.pop(self.queue_key)
            if task is None:
                break
            tasks.append(task)
        return tasks

# Usage
processor = TaskProcessor()
processor.add_task({'action': 'process_file', 'file_id': 'doc1'})
tasks = processor.process_tasks(batch_size=5)
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
   
   # Reuse for multiple queues
   queue1 = Queue(connection_manager=connection_manager)
   queue2 = Queue(connection_manager=connection_manager)
   ```

2. **Error Handling**
   ```python
   try:
       queue.push('tasks', task)
   except Exception as e:
       logger.error(f"Error adding task: {e}")
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
- FIFO ordering
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
   # Monitor queue size
   size = queue.size('tasks')
   print(f"Current size: {size}")
   ```
