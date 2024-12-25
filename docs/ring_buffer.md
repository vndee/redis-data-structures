# Ring Buffer (Circular Buffer)

A Redis-backed ring buffer implementation that maintains a fixed-size circular buffer where new elements overwrite the oldest ones when the buffer is full. Perfect for log rotation, metrics collection, sliding window analytics, and real-time data processing.

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | --- | --- | --- | --- |
| `push` | $O(1)$ | $O(1)$ | Add an item (overwrites oldest if full) | `RPUSH`, `LPOP` |
| `get_all` | $O(n)$ | $O(n)$ | Get all items in order (oldest to newest) | `LRANGE` |
| `get_latest` | $O(n)$ | $O(n)$ | Get n most recent items | `LRANGE` |
| `size` | $O(1)$ | $O(1)$ | Get number of items | `LLEN` |
| `clear` | $O(1)$ | $O(1)$ | Remove all items | `DELETE` |

where:
- n is the number of items in the ring buffer

## Basic Usage

```python
from redis_data_structures import RingBuffer

# Initialize ring buffer with capacity
buffer = RingBuffer(capacity=5)
buffer_key = "my_buffer"

# Add items
buffer.push(buffer_key, "item1")
buffer.push(buffer_key, "item2")
buffer.push(buffer_key, "item3")

# Get all items in order
items = buffer.get_all(buffer_key)  # Returns ["item1", "item2", "item3"]

# Get most recent items
latest = buffer.get_latest(buffer_key, 2)  # Returns ["item3", "item2"]

# Get buffer size
size = buffer.size(buffer_key)  # Returns 3

# Clear buffer
buffer.clear(buffer_key)
```

## Advanced Usage

```python
from redis_data_structures import RingBuffer
from typing import Dict, Any, List
from datetime import datetime, timedelta

class MetricsCollector:
    def __init__(self, window_size: int = 60):
        """Initialize metrics collector with window size in seconds."""
        self.buffer = RingBuffer(capacity=window_size)
        self.metrics_key = "system_metrics"
    
    def record_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Record system metrics."""
        data = {
            "timestamp": datetime.now().isoformat(),
            **metrics
        }
        return self.buffer.push(self.metrics_key, data)
    
    def get_metrics_window(self, seconds: int) -> List[Dict[str, Any]]:
        """Get metrics for the last n seconds."""
        count = min(seconds, self.buffer.capacity)
        return self.buffer.get_latest(self.metrics_key, count)
    
    def get_average_metrics(self, seconds: int) -> Dict[str, float]:
        """Calculate average metrics over the specified window."""
        metrics = self.get_metrics_window(seconds)
        if not metrics:
            return {}
        
        # Initialize sums
        sums = {}
        for metric_name in metrics[0].keys():
            if metric_name != "timestamp":
                sums[metric_name] = 0.0
        
        # Calculate sums
        for metric in metrics:
            for name, value in metric.items():
                if name != "timestamp" and isinstance(value, (int, float)):
                    sums[name] += value
        
        # Calculate averages
        return {
            name: value / len(metrics)
            for name, value in sums.items()
        }

# Usage
collector = MetricsCollector(window_size=60)

# Record metrics
collector.record_metrics({
    "cpu_usage": 75.5,
    "memory_usage": 82.3,
    "disk_io": 45.2
})

# Get averages
averages = collector.get_average_metrics(30)
```

## Example Use Cases

### 1. Log Rotation System

```python
from redis_data_structures import RingBuffer
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class LogRotator:
    def __init__(self, max_logs: int = 1000):
        self.buffer = RingBuffer(capacity=max_logs)
        self.logs_key = "application_logs"
    
    def log(self, level: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a log entry."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
            "metadata": metadata or {}
        }
        return self.buffer.push(self.logs_key, entry)
    
    def get_recent_logs(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get most recent log entries."""
        return self.buffer.get_latest(self.logs_key, count)
    
    def get_logs_by_level(self, level: str, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs of specific level."""
        logs = self.get_recent_logs(count)
        return [
            log for log in logs
            if log["level"] == level.upper()
        ]
    
    def search_logs(self, query: str, count: int = 100) -> List[Dict[str, Any]]:
        """Search recent logs for query string."""
        logs = self.get_recent_logs(count)
        return [
            log for log in logs
            if query.lower() in log["message"].lower()
        ]

# Usage
rotator = LogRotator(max_logs=1000)

# Add logs
rotator.log("INFO", "Application started")
rotator.log(
    "ERROR", 
    "Database connection failed",
    {"attempt": 1, "database": "users"}
)

# Get recent error logs
errors = rotator.get_logs_by_level("ERROR")

# Search logs
db_logs = rotator.search_logs("database")
```

### 2. Time Series Data Buffer

```python
from redis_data_structures import RingBuffer
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics

class TimeSeriesBuffer:
    def __init__(self, window_size: int):
        """Initialize with window size in data points."""
        self.buffer = RingBuffer(capacity=window_size)
        self.series_key = "time_series"
    
    def record_value(self, value: float, timestamp: Optional[datetime] = None):
        """Record a value with timestamp."""
        data = {
            "timestamp": (timestamp or datetime.now()).isoformat(),
            "value": value
        }
        return self.buffer.push(self.series_key, data)
    
    def get_window(self, points: int) -> List[Dict[str, Any]]:
        """Get latest n data points."""
        return self.buffer.get_latest(self.series_key, points)
    
    def calculate_statistics(self, window: int) -> Dict[str, float]:
        """Calculate statistics for the window."""
        data = self.get_window(window)
        if not data:
            return {}
            
        values = [point["value"] for point in data]
        return {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values)
        }
    
    def detect_anomalies(self, window: int, threshold: float) -> List[Dict[str, Any]]:
        """Detect anomalies using standard deviation."""
        data = self.get_window(window)
        if len(data) < 2:
            return []
            
        values = [point["value"] for point in data]
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        return [
            point for point in data
            if abs(point["value"] - mean) > threshold * std_dev
        ]

# Usage
ts_buffer = TimeSeriesBuffer(window_size=100)

# Record values
ts_buffer.record_value(42.5)
ts_buffer.record_value(43.2)
ts_buffer.record_value(41.8)
ts_buffer.record_value(100.0)  # Anomaly

# Calculate statistics
stats = ts_buffer.calculate_statistics(window=10)

# Detect anomalies (3 standard deviations)
anomalies = ts_buffer.detect_anomalies(window=10, threshold=3)
```

### 3. Rate Limiter with Sliding Window

```python
from redis_data_structures import RingBuffer
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, window_size: int, max_requests: int):
        """
        Initialize rate limiter.
        
        Args:
            window_size: Window size in seconds
            max_requests: Maximum requests allowed in window
        """
        self.buffer = RingBuffer(capacity=max_requests)
        self.window_size = window_size
        self.max_requests = max_requests
    
    def _get_key(self, client_id: str) -> str:
        """Get Redis key for client."""
        return f"rate_limit:{client_id}"
    
    def record_request(self, client_id: str, metadata: Optional[Dict[str, Any]] = None):
        """Record an API request."""
        request_time = datetime.now()
        
        # Clean up old requests first
        self.cleanup_old_requests(client_id)
        
        # Record new request
        request_data = {
            "timestamp": request_time.isoformat(),
            "metadata": metadata or {}
        }
        return self.buffer.push(self._get_key(client_id), request_data)
    
    def cleanup_old_requests(self, client_id: str):
        """Remove requests outside the window."""
        cutoff_time = datetime.now() - timedelta(seconds=self.window_size)
        
        # Get all requests
        requests = self.buffer.get_all(self._get_key(client_id))
        
        # Clear buffer if all requests are old
        if all(datetime.fromisoformat(r["timestamp"]) < cutoff_time for r in requests):
            self.buffer.clear(self._get_key(client_id))
    
    def can_make_request(self, client_id: str) -> bool:
        """Check if client can make a request."""
        self.cleanup_old_requests(client_id)
        return self.buffer.size(self._get_key(client_id)) < self.max_requests
    
    def get_request_count(self, client_id: str) -> int:
        """Get number of requests in current window."""
        self.cleanup_old_requests(client_id)
        return self.buffer.size(self._get_key(client_id))
    
    def get_request_history(self, client_id: str) -> List[Dict[str, Any]]:
        """Get request history in current window."""
        self.cleanup_old_requests(client_id)
        return self.buffer.get_all(self._get_key(client_id))

# Usage
limiter = RateLimiter(window_size=60, max_requests=100)

# Check and record requests
client_id = "user123"
if limiter.can_make_request(client_id):
    limiter.record_request(client_id, {
        "endpoint": "/api/data",
        "method": "GET"
    })
else:
    print("Rate limit exceeded")

# Get request statistics
count = limiter.get_request_count(client_id)
history = limiter.get_request_history(client_id)
```