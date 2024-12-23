# Deque (Double-ended Queue)

A Redis-backed Double-ended Queue implementation that supports adding and removing elements from both ends. Perfect for sliding windows, browser history, and work-stealing algorithms.

## Features

- Double-ended operations
- Thread-safe operations
- Persistent storage with Redis
- JSON serialization for complex data types
- Atomic operations
- Size tracking

## Operations

| Operation     | Time Complexity | Description |
|--------------|----------------|-------------|
| `push_front` | O(1)          | Add an item to the front |
| `push_back`  | O(1)          | Add an item to the back |
| `pop_front`  | O(1)          | Remove and return the front item |
| `pop_back`   | O(1)          | Remove and return the back item |
| `size`       | O(1)          | Get the current size |
| `clear`      | O(1)          | Remove all items |

## Basic Usage

```python
from redis_data_structures import Deque

# Initialize deque
deque = Deque(
    host='localhost',
    port=6379,
    db=0,
    username=None,  # Optional
    password=None   # Optional
)

# Basic operations
deque.push_front('my_deque', 'first')
deque.push_back('my_deque', 'last')
front = deque.pop_front('my_deque')  # Returns 'first'
back = deque.pop_back('my_deque')    # Returns 'last'
size = deque.size('my_deque')
deque.clear('my_deque')
```

## Example Use Cases

### 1. Sliding Window Analysis

Perfect for maintaining a sliding window of recent data points.

```python
class SlidingWindow:
    def __init__(self, window_size: int):
        self.deque = Deque(host='localhost', port=6379)
        self.window_size = window_size
    
    def add_datapoint(self, key: str, value: float, timestamp: float = None):
        """Add a new datapoint to the window."""
        if timestamp is None:
            timestamp = time.time()
        
        datapoint = {
            'value': value,
            'timestamp': timestamp
        }
        
        # Add new point to back
        self.deque.push_back(key, json.dumps(datapoint))
        
        # Remove old points from front
        while self.deque.size(key) > self.window_size:
            self.deque.pop_front(key)
    
    def get_window(self, key: str) -> list:
        """Get all datapoints in the window."""
        size = self.deque.size(key)
        points = []
        
        # Get all points while maintaining order
        for _ in range(size):
            point = self.deque.pop_front(key)
            if point:
                points.append(json.loads(point))
                self.deque.push_back(key, point)
        
        return points
    
    def get_average(self, key: str) -> float:
        """Calculate average of values in window."""
        points = self.get_window(key)
        if not points:
            return 0.0
        return sum(p['value'] for p in points) / len(points)
    
    def get_recent(self, key: str, seconds: int) -> list:
        """Get points from last N seconds."""
        points = self.get_window(key)
        cutoff = time.time() - seconds
        return [p for p in points if p['timestamp'] >= cutoff]

# Usage
window = SlidingWindow(window_size=60)  # 60 point window
window.add_datapoint('temperature', 25.5)
window.add_datapoint('temperature', 26.0)
avg = window.get_average('temperature')
recent = window.get_recent('temperature', 30)  # Last 30 seconds
```

### 2. Enhanced Browser History

Ideal for implementing browser-like history with forward/back navigation.

```python
class BrowserHistory:
    def __init__(self):
        self.history = Deque(host='localhost', port=6379)
        self.forward = Deque(host='localhost', port=6379)
        self.history_key = 'browser:history'
        self.forward_key = 'browser:forward'
        self.current_page = None
    
    def visit(self, url: str):
        """Visit a new page."""
        if self.current_page:
            self.history.push_back(self.history_key, json.dumps({
                'url': self.current_page,
                'timestamp': time.time()
            }))
        
        self.current_page = url
        # Clear forward history
        self.forward.clear(self.forward_key)
    
    def back(self) -> Optional[str]:
        """Navigate back one page."""
        if self.history.size(self.history_key) == 0:
            return None
        
        # Save current page to forward history
        if self.current_page:
            self.forward.push_front(self.forward_key, json.dumps({
                'url': self.current_page,
                'timestamp': time.time()
            }))
        
        # Go back
        page = self.history.pop_back(self.history_key)
        if page:
            self.current_page = json.loads(page)['url']
            return self.current_page
        return None
    
    def forward(self) -> Optional[str]:
        """Navigate forward one page."""
        if self.forward.size(self.forward_key) == 0:
            return None
        
        # Save current page to back history
        if self.current_page:
            self.history.push_back(self.history_key, json.dumps({
                'url': self.current_page,
                'timestamp': time.time()
            }))
        
        # Go forward
        page = self.forward.pop_front(self.forward_key)
        if page:
            self.current_page = json.loads(page)['url']
            return self.current_page
        return None
    
    def get_history(self) -> list:
        """Get browsing history."""
        size = self.history.size(self.history_key)
        history = []
        
        for _ in range(size):
            page = self.history.pop_front(self.history_key)
            if page:
                history.append(json.loads(page))
                self.history.push_back(self.history_key, page)
        
        return history

# Usage
browser = BrowserHistory()
browser.visit('https://example.com')
browser.visit('https://example.com/about')
browser.back()    # Returns to home page
browser.forward() # Returns to about page
```

### 3. Work Stealing Queue

Perfect for implementing work-stealing algorithms in distributed systems.

```python
class WorkStealingQueue:
    def __init__(self, worker_id: str):
        self.deque = Deque(host='localhost', port=6379)
        self.worker_id = worker_id
        self.queue_key = f'worker:{worker_id}:tasks'
    
    def add_task(self, task: dict):
        """Add a task to own queue (at back)."""
        self.deque.push_back(self.queue_key, json.dumps({
            'task': task,
            'timestamp': time.time(),
            'owner': self.worker_id
        }))
    
    def get_own_task(self) -> Optional[dict]:
        """Get task from own queue (from back)."""
        task = self.deque.pop_back(self.queue_key)
        return json.loads(task) if task else None
    
    def steal_task(self, victim_id: str) -> Optional[dict]:
        """Steal task from another worker's queue (from front)."""
        victim_key = f'worker:{victim_id}:tasks'
        task = self.deque.pop_front(victim_key)
        if task:
            task_data = json.loads(task)
            task_data['stolen_by'] = self.worker_id
            task_data['stolen_at'] = time.time()
            return task_data
        return None
    
    def get_task_count(self) -> int:
        """Get number of tasks in queue."""
        return self.deque.size(self.queue_key)

# Usage
worker1 = WorkStealingQueue('worker1')
worker2 = WorkStealingQueue('worker2')

# Worker 1 adds tasks
worker1.add_task({'type': 'process', 'data': 'item1'})
worker1.add_task({'type': 'process', 'data': 'item2'})

# Worker 2 steals task when idle
stolen_task = worker2.steal_task('worker1')
```

## Best Practices

1. **Key Management**
   - Use descriptive key names: `deque:history`, `deque:window`, etc.
   - Consider implementing key expiration for temporary deques
   - Clear deques that are no longer needed

2. **Error Handling**
   ```python
   try:
       deque.push_back('my_deque', item)
   except redis.RedisError as e:
       logger.error(f"Redis error: {e}")
       # Handle error...
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
       # Handle error...
   ```

3. **Memory Management**
   - Monitor deque size
   - Implement size limits if needed
   ```python
   if deque.size('my_deque') > MAX_SIZE:
       oldest = deque.pop_front('my_deque')
       # Handle overflow...
   ```

4. **Performance**
   - Use appropriate end for operations
   - Consider cleanup strategies
   - Implement batch operations when possible

## Common Patterns

### 1. Circular Buffer
```python
class CircularBuffer:
    def __init__(self, max_size: int):
        self.deque = Deque(host='localhost', port=6379)
        self.max_size = max_size
    
    def add(self, key: str, item: Any):
        """Add item, removing oldest if full."""
        if self.deque.size(key) >= self.max_size:
            self.deque.pop_front(key)
        self.deque.push_back(key, json.dumps(item))
    
    def get_all(self, key: str) -> list:
        """Get all items while preserving order."""
        items = []
        size = self.deque.size(key)
        
        for _ in range(size):
            item = self.deque.pop_front(key)
            if item:
                items.append(json.loads(item))
                self.deque.push_back(key, item)
        
        return items
```

### 2. Moving Average
```python
class MovingAverage:
    def __init__(self, window_size: int):
        self.deque = Deque(host='localhost', port=6379)
        self.window_size = window_size
    
    def add_value(self, key: str, value: float):
        """Add value and maintain window size."""
        self.deque.push_back(key, str(value))
        if self.deque.size(key) > self.window_size:
            self.deque.pop_front(key)
    
    def get_average(self, key: str) -> float:
        """Calculate moving average."""
        values = []
        size = self.deque.size(key)
        
        for _ in range(size):
            value = self.deque.pop_front(key)
            if value:
                values.append(float(value))
                self.deque.push_back(key, value)
        
        return sum(values) / len(values) if values else 0.0
```

### 3. Task Queue with Priorities
```python
class PriorityTaskQueue:
    def __init__(self):
        self.high = Deque(host='localhost', port=6379)
        self.normal = Deque(host='localhost', port=6379)
        self.low = Deque(host='localhost', port=6379)
    
    def add_task(self, priority: str, task: dict):
        """Add task with priority."""
        queue_key = f'tasks:{priority}'
        if priority == 'high':
            self.high.push_back(queue_key, json.dumps(task))
        elif priority == 'normal':
            self.normal.push_back(queue_key, json.dumps(task))
        else:
            self.low.push_back(queue_key, json.dumps(task))
    
    def get_next_task(self) -> Optional[dict]:
        """Get highest priority task available."""
        for queue, key in [
            (self.high, 'tasks:high'),
            (self.normal, 'tasks:normal'),
            (self.low, 'tasks:low')
        ]:
            if queue.size(key) > 0:
                task = queue.pop_front(key)
                return json.loads(task) if task else None
        return None
```

## Limitations

1. **No Random Access**
   - Can only access ends of deque
   - Must remove elements to access middle

2. **No Size Limit**
   - Must implement size limits manually
   - Memory usage grows linearly

3. **No Peek Operation**
   - Cannot view elements without removing
   - Must implement peek using pop/push

## Performance Considerations

1. **Time Complexity**
   - All operations are O(1)
   - Consider end choice for operations

2. **Memory Usage**
   - Each element consumes memory
   - Consider cleanup strategies

3. **Concurrency**
   - Operations are atomic
   - Safe for multi-threaded use

## Troubleshooting

1. **Empty Deque**
   - Check if elements were added
   - Verify key names
   - Check for accidental removals

2. **Memory Issues**
   - Monitor deque size
   - Implement size limits
   - Regular cleanup of old data

3. **Performance Issues**
   - Use appropriate end for operations
   - Consider batch operations
   - Monitor Redis performance 