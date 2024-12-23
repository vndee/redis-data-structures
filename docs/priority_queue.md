# Priority Queue

A Redis-backed priority queue implementation that maintains elements in sorted order by priority. Perfect for task scheduling, job queues, and any application requiring prioritized processing.

## Features

- O(log N) push and O(1) pop operations
- Priority-based ordering
- Thread-safe operations
- Persistent storage
- Connection pooling and retries
- Circuit breaker pattern
- Health monitoring

## Basic Usage

```python
from redis_data_structures import PriorityQueue, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create priority queue with connection manager
pq = PriorityQueue(connection_manager=connection_manager)

# Add items with priorities (lower number = higher priority)
pq.push('tasks', 'high_priority_task', priority=1)
pq.push('tasks', 'medium_priority_task', priority=2)
pq.push('tasks', 'low_priority_task', priority=3)

# Get highest priority item
task = pq.pop('tasks')  # Returns 'high_priority_task'

# Check size
size = pq.size('tasks')

# Clear the queue
pq.clear('tasks')
```

## Advanced Usage

```python
from redis_data_structures import PriorityQueue, ConnectionManager
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

# Create priority queue with connection manager
pq = PriorityQueue(connection_manager=connection_manager)

# Store complex types with priorities
task = {
    'id': 'task1',
    'type': 'process_data',
    'created_at': datetime.now(),
    'data': {'user_id': 123, 'action': 'update'}
}
pq.push('tasks', task, priority=1)

# Peek at highest priority item without removing
next_task = pq.peek('tasks')

# Monitor health
health = connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
```

## Example Use Cases

### 1. Task Scheduler

```python
from redis_data_structures import PriorityQueue, ConnectionManager
from datetime import datetime

class TaskScheduler:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.pq = PriorityQueue(connection_manager=self.connection_manager)
        self.queue_key = 'scheduled_tasks'
    
    def schedule_task(self, task: dict, execution_time: datetime):
        """Schedule a task for execution."""
        priority = execution_time.timestamp()
        task['scheduled_for'] = execution_time.isoformat()
        self.pq.push(self.queue_key, task, priority=priority)
    
    def get_next_task(self) -> dict:
        """Get the next task to execute."""
        now = datetime.now().timestamp()
        task = self.pq.peek(self.queue_key)
        if task and self.pq.get_priority(self.queue_key, task) <= now:
            return self.pq.pop(self.queue_key)
        return None

# Usage
scheduler = TaskScheduler()
scheduler.schedule_task(
    {'action': 'send_email', 'to': 'user@example.com'},
    datetime.now() + timedelta(hours=1)
)
```

### 2. Job Queue

```python
from redis_data_structures import PriorityQueue, ConnectionManager
import json

class JobQueue:
    def __init__(self):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.pq = PriorityQueue(connection_manager=self.connection_manager)
        self.queue_key = 'jobs'
    
    def add_job(self, job: dict, priority: int = 10):
        """Add a job to the queue."""
        job['created_at'] = datetime.now().isoformat()
        self.pq.push(self.queue_key, job, priority=priority)
    
    def get_job(self) -> dict:
        """Get highest priority job."""
        return self.pq.pop(self.queue_key)
    
    def peek_next_job(self) -> dict:
        """Preview next job without removing."""
        return self.pq.peek(self.queue_key)

# Usage
queue = JobQueue()
queue.add_job({'type': 'critical_task'}, priority=1)
queue.add_job({'type': 'normal_task'}, priority=5)
job = queue.get_job()  # Returns critical_task first
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
   pq1 = PriorityQueue(connection_manager=connection_manager)
   pq2 = PriorityQueue(connection_manager=connection_manager)
   ```

2. **Error Handling**
   ```python
   try:
       pq.push('tasks', task, priority=1)
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

- Uses Redis sorted sets for storage
- Priority-based ordering
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
   size = pq.size('tasks')
   print(f"Current size: {size}")
   ```
