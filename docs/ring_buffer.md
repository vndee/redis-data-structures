# Ring Buffer

A Redis-backed ring buffer (circular buffer) implementation. Perfect for scenarios where you need a fixed-size buffer that automatically overwrites old data when full, such as log rotation, streaming data processing, and sliding window analytics.

## Features

- Fixed-size circular buffer
- O(1) operations for push and get
- Thread-safe operations
- Persistent storage with Redis
- JSON serialization for complex data types
- Atomic operations
- Size tracking

## Operations

| Operation    | Time Complexity | Description |
|-------------|----------------|-------------|
| `push`      | O(1)          | Add an item to the buffer, overwriting oldest if full |
| `get_all`   | O(n)          | Get all items in order (oldest to newest) |
| `get_latest`| O(k)          | Get k most recent items (newest to oldest) |
| `size`      | O(1)          | Get the current number of items |
| `clear`     | O(1)          | Remove all items from the buffer |

Where n is the buffer capacity and k is the number of items requested.

## Basic Usage

```python
from redis_data_structures import RingBuffer

# Initialize ring buffer with capacity
buffer = RingBuffer(
    capacity=1000,  # Maximum number of items
    host='localhost',
    port=6379,
    db=0,
    username=None,  # Optional
    password=None   # Optional
)

# Add items (overwrites oldest when full)
buffer.push('my_buffer', 'item1')
buffer.push('my_buffer', {'complex': 'item'})

# Get all items (oldest to newest)
items = buffer.get_all('my_buffer')

# Get latest 5 items (newest to oldest)
latest = buffer.get_latest('my_buffer', 5)

# Get current size
size = buffer.size('my_buffer')

# Clear buffer
buffer.clear('my_buffer')
```

## Example Use Cases

### 1. Log Rotation

Perfect for maintaining a fixed-size log history.

```python
class LogRotator:
    def __init__(self, max_logs: int = 1000):
        self.buffer = RingBuffer(capacity=max_logs, host='localhost', port=6379)
        self.log_key = 'app:logs'
    
    def log(self, level: str, message: str):
        """Add a log entry."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.buffer.push(self.log_key, entry)
    
    def get_recent_logs(self, n: int = 100) -> list:
        """Get most recent log entries."""
        return self.buffer.get_latest(self.log_key, n)
    
    def get_all_logs(self) -> list:
        """Get all logs in chronological order."""
        return self.buffer.get_all(self.log_key)

# Usage
logger = LogRotator(max_logs=1000)
logger.log('INFO', 'Application started')
logger.log('ERROR', 'Connection failed')
recent_logs = logger.get_recent_logs(10)  # Get last 10 logs
```

### 2. Streaming Data Processing

Ideal for maintaining a sliding window of data points.

```python
class DataStream:
    def __init__(self, window_size: int):
        self.buffer = RingBuffer(capacity=window_size, host='localhost', port=6379)
        self.stream_key = 'data:stream'
    
    def add_datapoint(self, value: float, timestamp: float):
        """Add a data point to the stream."""
        data = {'value': value, 'timestamp': timestamp}
        self.buffer.push(self.stream_key, data)
    
    def get_window(self) -> list:
        """Get all data points in the current window."""
        return self.buffer.get_all(self.stream_key)
    
    def get_latest_points(self, n: int) -> list:
        """Get n most recent data points."""
        return self.buffer.get_latest(self.stream_key, n)

# Usage
stream = DataStream(window_size=100)  # Keep last 100 points
stream.add_datapoint(42.0, time.time())
window_data = stream.get_window()
latest_10 = stream.get_latest_points(10)
```

### 3. Performance Monitoring

Perfect for tracking system metrics with a fixed history.

```python
class PerformanceMonitor:
    def __init__(self, history_size: int = 3600):  # 1 hour at 1 sample/second
        self.buffer = RingBuffer(capacity=history_size, host='localhost', port=6379)
        self.metrics_key = 'system:metrics'
    
    def record_metrics(self, cpu: float, memory: float, io: float):
        """Record system metrics."""
        metrics = {
            'timestamp': time.time(),
            'cpu_usage': cpu,
            'memory_usage': memory,
            'io_usage': io
        }
        self.buffer.push(self.metrics_key, metrics)
    
    def get_recent_metrics(self, minutes: int = 5) -> list:
        """Get last n minutes of metrics."""
        points = minutes * 60  # 60 samples per minute
        return self.buffer.get_latest(self.metrics_key, points)

# Usage
monitor = PerformanceMonitor()
monitor.record_metrics(cpu=45.2, memory=72.1, io=12.5)
last_5min = monitor.get_recent_metrics(5)  # Last 5 minutes
```

## Best Practices

1. **Capacity Planning**
   - Choose capacity based on memory constraints
   - Consider data retention requirements
   - Monitor Redis memory usage

2. **Error Handling**
   ```python
   try:
       buffer.push('my_buffer', data)
   except redis.RedisError as e:
       logger.error(f"Redis error: {e}")
       # Handle error...
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
       # Handle error...
   ```

3. **Memory Management**
   - Monitor buffer size
   - Clear unused buffers
   - Set appropriate TTL for temporary data

4. **Performance**
   - Use batch operations when possible
   - Consider data serialization overhead
   - Monitor Redis performance

## Implementation Details

The ring buffer is implemented using:

1. **Redis Lists**
   - Main storage for buffer items
   - O(1) push and pop operations
   - Efficient range queries

2. **Position Tracking**
   - Separate Redis key for write position
   - Atomic position updates
   - Wraps around at capacity

3. **Transactions**
   - Atomic operations for data consistency
   - Pipeline for better performance
   - Error handling and rollback

## Performance Considerations

1. **Time Complexity**
   - Push operations: O(1)
   - Get operations: O(n) where n is items requested
   - Size operations: O(1)

2. **Memory Usage**
   - Fixed size regardless of operations
   - Memory usage = capacity * avg_item_size
   - Consider Redis memory limits

3. **Concurrency**
   - Operations are atomic
   - Safe for multi-threaded use
   - Uses Redis transactions

## Troubleshooting

1. **Data Loss**
   - Check buffer capacity
   - Verify push operations
   - Monitor overwrite behavior

2. **Memory Issues**
   - Monitor Redis memory
   - Check item sizes
   - Verify capacity settings

3. **Performance Issues**
   - Check network latency
   - Monitor Redis performance
   - Consider batch operations 