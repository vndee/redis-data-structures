# Ring Buffer

A Redis-backed ring buffer (circular buffer) implementation that maintains a fixed-size buffer of elements. Perfect for sliding windows, log rotation, and any application requiring fixed-size data storage with automatic overwrite.

## Features

- Fixed-size circular storage
- O(1) operations for add/get
- Thread-safe operations
- Persistent storage
- Connection pooling and retries
- Circuit breaker pattern
- Health monitoring

## Basic Usage

```python
from redis_data_structures import RingBuffer, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create ring buffer with connection manager
rb = RingBuffer(connection_manager=connection_manager, max_size=5)

# Add items (automatically overwrites oldest when full)
rb.add('sensor_data', 'reading1')  # [reading1]
rb.add('sensor_data', 'reading2')  # [reading1, reading2]
rb.add('sensor_data', 'reading3')  # [reading1, reading2, reading3]
rb.add('sensor_data', 'reading4')  # [reading1, reading2, reading3, reading4]
rb.add('sensor_data', 'reading5')  # [reading1, reading2, reading3, reading4, reading5]
rb.add('sensor_data', 'reading6')  # [reading2, reading3, reading4, reading5, reading6]

# Get all items
items = rb.get_all('sensor_data')  # Returns last 5 items

# Get size
size = rb.size('sensor_data')

# Clear the buffer
rb.clear('sensor_data')
```

## Advanced Usage

```python
from redis_data_structures import RingBuffer, ConnectionManager
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

# Create ring buffer with connection manager
rb = RingBuffer(connection_manager=connection_manager, max_size=1000)

# Store complex types
data_point = {
    'timestamp': datetime.now(),
    'value': 42.5,
    'metadata': {'sensor_id': 'temp1', 'unit': 'celsius'}
}
rb.add('temperature_readings', data_point)

# Get latest items
latest = rb.get_latest('temperature_readings', count=10)

# Monitor health
health = connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
```

## Example Use Cases

### 1. Sensor Data Logger

```python
from redis_data_structures import RingBuffer, ConnectionManager
from datetime import datetime

class SensorLogger:
    def __init__(self, retention_size: int = 1000):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.buffer = RingBuffer(
            connection_manager=self.connection_manager,
            max_size=retention_size
        )
        self.buffer_key = 'sensor_readings'
    
    def log_reading(self, sensor_id: str, value: float):
        """Log a sensor reading."""
        reading = {
            'sensor_id': sensor_id,
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        self.buffer.add(self.buffer_key, reading)
    
    def get_recent_readings(self, count: int = 100) -> list:
        """Get recent readings."""
        return self.buffer.get_latest(self.buffer_key, count)

# Usage
logger = SensorLogger(retention_size=1000)
logger.log_reading('temp1', 25.5)
recent = logger.get_recent_readings(count=10)
```

### 2. Log Rotator

```python
from redis_data_structures import RingBuffer, ConnectionManager
import json

class LogRotator:
    def __init__(self, max_entries: int = 1000):
        self.connection_manager = ConnectionManager(host='localhost', port=6379)
        self.buffer = RingBuffer(
            connection_manager=self.connection_manager,
            max_size=max_entries
        )
        self.buffer_key = 'application_logs'
    
    def log(self, level: str, message: str, metadata: dict = None):
        """Add a log entry."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'metadata': metadata or {}
        }
        self.buffer.add(self.buffer_key, entry)
    
    def get_logs(self, count: int = None) -> list:
        """Get recent logs."""
        if count:
            return self.buffer.get_latest(self.buffer_key, count)
        return self.buffer.get_all(self.buffer_key)

# Usage
logger = LogRotator(max_entries=1000)
logger.log('INFO', 'Application started', {'version': '1.0.0'})
recent_logs = logger.get_logs(count=50)
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
   
   # Reuse for multiple buffers
   rb1 = RingBuffer(connection_manager=connection_manager, max_size=100)
   rb2 = RingBuffer(connection_manager=connection_manager, max_size=200)
   ```

2. **Error Handling**
   ```python
   try:
       rb.add('sensor_data', reading)
   except Exception as e:
       logger.error(f"Error adding reading: {e}")
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
- Fixed-size circular buffer
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
   # Monitor buffer size
   size = rb.size('sensor_data')
   print(f"Current size: {size}")
   ``` 