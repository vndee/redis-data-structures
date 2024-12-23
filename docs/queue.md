# Queue (FIFO)

A First-In-First-Out (FIFO) queue implementation backed by Redis. Elements are processed in the order they were added, making it perfect for task queues, job processing, and event handling systems.

## Features

- FIFO ordering guarantee
- Thread-safe operations
- Persistent storage with Redis
- JSON serialization for complex data types
- Atomic operations
- Size tracking

## Operations

| Operation | Time Complexity | Description |
|-----------|----------------|-------------|
| `push`    | O(1)          | Add an item to the back of the queue |
| `pop`     | O(1)          | Remove and return the item from the front |
| `size`    | O(1)          | Get the current size of the queue |
| `clear`   | O(1)          | Remove all items from the queue |

## Basic Usage

```python
from redis_data_structures import Queue

# Initialize queue
queue = Queue(
    host='localhost',
    port=6379,
    db=0,
    username=None,  # Optional
    password=None   # Optional
)

# Basic operations
queue.push('my_queue', 'item1')
queue.push('my_queue', {'complex': 'item'})
item = queue.pop('my_queue')
size = queue.size('my_queue')
queue.clear('my_queue')
```

## Example Use Cases

### 1. Task Processing System

Perfect for distributed task processing where tasks need to be processed in order.

```python
class TaskProcessor:
    def __init__(self):
        self.queue = Queue(host='localhost', port=6379)
        self.task_key = 'tasks:processing'
    
    def add_task(self, task_data: dict):
        """Add a task to the processing queue."""
        self.queue.push(self.task_key, {
            'id': str(uuid.uuid4()),
            'data': task_data,
            'timestamp': time.time()
        })
    
    def process_tasks(self):
        """Process tasks in FIFO order."""
        while True:
            task = self.queue.pop(self.task_key)
            if not task:
                time.sleep(1)  # Wait if queue is empty
                continue
            
            try:
                print(f"Processing task {task['id']}")
                # Process the task...
            except Exception as e:
                print(f"Error processing task: {e}")

# Usage
processor = TaskProcessor()
processor.add_task({'type': 'email', 'to': 'user@example.com'})
processor.add_task({'type': 'notification', 'user_id': 123})
```

### 2. Print Job Management

Ideal for managing print jobs that need to be processed in order.

```python
class PrintServer:
    def __init__(self):
        self.queue = Queue(host='localhost', port=6379)
        self.printer_key = 'printer:jobs'
    
    def add_print_job(self, document: str, user: str, priority: bool = False):
        """Add a print job to the queue."""
        job = {
            'id': str(uuid.uuid4()),
            'document': document,
            'user': user,
            'timestamp': time.time(),
            'status': 'pending'
        }
        
        self.queue.push(self.printer_key, job)
        return job['id']
    
    def process_print_jobs(self):
        """Process print jobs in order."""
        while True:
            job = self.queue.pop(self.printer_key)
            if not job:
                time.sleep(1)
                continue
            
            try:
                print(f"Printing document for {job['user']}")
                # Actual printing logic here...
                time.sleep(2)  # Simulate printing
                print(f"Completed printing job {job['id']}")
            except Exception as e:
                print(f"Error printing job {job['id']}: {e}")

# Usage
printer = PrintServer()
job_id = printer.add_print_job('report.pdf', 'john.doe')
```

### 3. Event Processing Pipeline

Great for event-driven architectures where events need to be processed in order.

```python
class EventPipeline:
    def __init__(self):
        self.queue = Queue(host='localhost', port=6379)
        self.events_key = 'events:processing'
    
    def log_event(self, event_type: str, data: dict):
        """Log an event for processing."""
        event = {
            'id': str(uuid.uuid4()),
            'type': event_type,
            'data': data,
            'timestamp': time.time()
        }
        self.queue.push(self.events_key, event)
        return event['id']
    
    def process_events(self):
        """Process events in order."""
        while True:
            event = self.queue.pop(self.events_key)
            if not event:
                time.sleep(1)
                continue
            
            try:
                print(f"Processing event: {event['type']}")
                if event['type'] == 'user_signup':
                    self._handle_signup(event['data'])
                elif event['type'] == 'purchase':
                    self._handle_purchase(event['data'])
                # ... handle other event types
            except Exception as e:
                print(f"Error processing event {event['id']}: {e}")
    
    def _handle_signup(self, data):
        # Handle signup logic
        pass
    
    def _handle_purchase(self, data):
        # Handle purchase logic
        pass

# Usage
pipeline = EventPipeline()
pipeline.log_event('user_signup', {
    'user_id': 123,
    'email': 'user@example.com'
})
pipeline.log_event('purchase', {
    'user_id': 123,
    'product_id': 456,
    'amount': 99.99
})
```

## Best Practices

1. **Key Management**
   - Use descriptive key names: `queue:tasks`, `queue:emails`, etc.
   - Consider implementing key expiration for temporary queues
   - Clear queues that are no longer needed

2. **Error Handling**
   ```python
   try:
       queue.push('my_queue', item)
   except redis.RedisError as e:
       logger.error(f"Redis error: {e}")
       # Handle error...
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
       # Handle error...
   ```

3. **Memory Management**
   - Monitor queue size to prevent memory issues
   - Implement size limits if needed
   ```python
   if queue.size('my_queue') > MAX_SIZE:
       # Handle queue full condition
       pass
   ```

4. **Performance**
   - Use batch processing when possible
   - Implement backoff strategies when queue is empty
   ```python
   def process_with_backoff():
       backoff = 1
       while True:
           item = queue.pop('my_queue')
           if item:
               process_item(item)
               backoff = 1
           else:
               time.sleep(min(backoff, 30))
               backoff *= 2
   ```

## Common Patterns

### 1. Producer-Consumer Pattern
```python
# Producer
def produce_items():
    while True:
        item = generate_item()
        queue.push('items', item)

# Consumer
def consume_items():
    while True:
        item = queue.pop('items')
        if item:
            process_item(item)
```

### 2. Fan-out Pattern
```python
def fan_out_task(task):
    """Distribute a task to multiple worker queues."""
    workers = ['worker1', 'worker2', 'worker3']
    for worker in workers:
        queue.push(f'tasks:{worker}', task)
```

### 3. Batch Processing
```python
def batch_process(batch_size: int = 10):
    """Process items in batches."""
    items = []
    while len(items) < batch_size:
        item = queue.pop('my_queue')
        if not item:
            break
        items.append(item)
    
    if items:
        process_batch(items)
```

## Limitations

1. **No Priority Support**
   - All items have equal priority
   - Use PriorityQueue if priority is needed

2. **No Peek Operation**
   - Cannot view items without removing them
   - Items are removed when accessed

3. **No Random Access**
   - Can only access items from the front
   - Must remove items to access ones behind

## Performance Considerations

1. **Network Latency**
   - Redis operations are network calls
   - Consider batch operations for better throughput

2. **Memory Usage**
   - Monitor Redis memory usage
   - Implement cleanup strategies

3. **Concurrency**
   - Operations are atomic
   - Multiple producers/consumers are safe

## Troubleshooting

1. **Queue Always Empty**
   - Check Redis connection
   - Verify key names
   - Check if items are being added correctly

2. **Memory Issues**
   - Monitor queue size
   - Implement size limits
   - Clear old/processed items

3. **Slow Processing**
   - Check network latency
   - Consider batch processing
   - Monitor Redis performance
