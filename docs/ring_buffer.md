# Ring Buffer (Circular Buffer)

A Redis-backed ring buffer implementation that maintains a fixed-size circular buffer where new elements overwrite the oldest ones when the buffer is full. Perfect for log rotation, metrics collection, sliding window analytics, and real-time data processing.

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | :---: | :---: | --- | --- |
| `push` | $O(1)$ | $O(1)$ | Add an item (overwrites oldest if full) | `RPUSH`, `LPOP` |
| `get_all` | $O(n)$ | $O(n)$ | Get all items in order (oldest to newest) | `LRANGE` |
| `get_latest` | $O(n)$ | $O(n)$ | Get n most recent items | `LRANGE` |
| `size` | $O(1)$ | $O(1)$ | Get number of items | `LLEN` |
| `clear` | $O(1)$ | $O(1)$ | Remove all items | `DELETE` |

where:
- $n$ is the number of items in the ring buffer

## Basic Usage

```python
from redis_data_structures import RingBuffer

# Initialize ring buffer with capacity
buffer = RingBuffer("my_buffer", capacity=5)

# Add items
buffer.push("item1")
buffer.push("item2")
buffer.push("item3")

# Get all items in order
items = buffer.get_all()  # Returns ["item1", "item2", "item3"]

# Get most recent items
latest = buffer.get_latest(2)  # Returns ["item3", "item2"]

# Get buffer size
size = buffer.size()  # Returns 3

# Clear buffer
buffer.clear()
```

## Advanced Usage

```python
from redis_data_structures import RingBuffer
from typing import Dict, Any, List
from datetime import datetime, timedelta

class MetricsCollector:
    def __init__(self, window_size: int = 60):
        """Initialize metrics collector with window size in seconds."""
        self.buffer = RingBuffer("my_metrics", capacity=window_size)

    def record_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Record system metrics."""
        data = {
            "timestamp": datetime.now().isoformat(),
            **metrics
        }
        return self.buffer.push(data)
    
    def get_metrics_window(self, seconds: int) -> List[Dict[str, Any]]:
        """Get metrics for the last n seconds."""
        count = min(seconds, self.buffer.capacity)
        return self.buffer.get_latest(count)
    
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
        self.buffer = RingBuffer("my_logs", capacity=max_logs)
    
    def log(self, level: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a log entry."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
            "metadata": metadata or {}
        }
        return self.buffer.push(entry)
    
    def get_recent_logs(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get most recent log entries."""
        return self.buffer.get_latest(count)
    
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
        self.buffer = RingBuffer("my_time_series", capacity=window_size)
    
    def record_value(self, value: float, timestamp: Optional[datetime] = None):
        """Record a value with timestamp."""
        data = {
            "timestamp": (timestamp or datetime.now()).isoformat(),
            "value": value
        }
        return self.buffer.push(data)
    
    def get_window(self, points: int) -> List[Dict[str, Any]]:
        """Get latest n data points."""
        return self.buffer.get_latest(points)
    
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

