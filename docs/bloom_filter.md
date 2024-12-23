# Bloom Filter

A Redis-backed Bloom filter implementation for efficient probabilistic membership testing. Perfect for reducing unnecessary lookups and improving performance in distributed systems.

## Features

- Probabilistic membership testing
- Space-efficient storage
- Configurable false positive rate
- Thread-safe operations
- Persistent storage
- Connection pooling and retries
- Circuit breaker pattern

## Basic Usage

```python
from redis_data_structures import BloomFilter, ConnectionManager

# Initialize connection manager
connection_manager = ConnectionManager(
    host='localhost',
    port=6379,
    db=0
)

# Create Bloom filter with connection manager
bf = BloomFilter(
    connection_manager=connection_manager,
    expected_elements=10000,  # Expected number of elements
    false_positive_rate=0.01  # Desired false positive rate
)

# Add elements
bf.add('my_filter', 'item1')
bf.add('my_filter', {'complex': 'data'})  # Supports any JSON-serializable data

# Check membership
exists = bf.contains('my_filter', 'item1')  # Returns True
exists = bf.contains('my_filter', 'item2')  # Returns False

# Get filter information
info = bf.info('my_filter')
print(f"Size in bits: {info['size_in_bits']}")
print(f"Number of hash functions: {info['num_hash_functions']}")
print(f"Items count: {info['count']}")

# Clear the filter
bf.clear('my_filter')
```

## Advanced Usage

```python
from redis_data_structures import BloomFilter, ConnectionManager
from datetime import timedelta

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

# Create Bloom filter with advanced settings
bf = BloomFilter(
    connection_manager=connection_manager,
    expected_elements=1000000,
    false_positive_rate=0.001
)

# Batch operations
items = ['item1', 'item2', 'item3']
bf.add_many('my_filter', items)
exists = bf.contains_many('my_filter', items)  # Returns list of booleans

# Monitor health
health = connection_manager.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
```

## Example Use Cases

### 1. Cache Layer

```python
from redis_data_structures import BloomFilter, ConnectionManager

def get_user(user_id: str) -> dict:
    # Initialize once and reuse
    connection_manager = ConnectionManager(host='localhost', port=6379)
    bf = BloomFilter(
        connection_manager=connection_manager,
        expected_elements=1000000,
        false_positive_rate=0.01
    )
    
    # Check if user might exist
    if not bf.contains('users_filter', user_id):
        return None  # User definitely doesn't exist
    
    # User might exist, check database
    user = database.get_user(user_id)
    if user and not bf.contains('users_filter', user_id):
        bf.add('users_filter', user_id)
    return user
```

### 2. Email Deduplication

```python
from redis_data_structures import BloomFilter, ConnectionManager

def is_email_sent(email: str) -> bool:
    connection_manager = ConnectionManager(host='localhost', port=6379)
    bf = BloomFilter(
        connection_manager=connection_manager,
        expected_elements=10000000,
        false_positive_rate=0.001
    )
    
    if bf.contains('sent_emails', email):
        return True  # Email probably sent before
    
    bf.add('sent_emails', email)
    return False  # Email definitely not sent before
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
   
   # Reuse for multiple filters
   bf1 = BloomFilter(connection_manager=connection_manager)
   bf2 = BloomFilter(connection_manager=connection_manager)
   ```

2. **Error Handling**
   ```python
   try:
       bf.add('my_filter', item)
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

- Uses Redis bit arrays for storage
- MurmurHash3 for hash functions
- Atomic operations for thread safety
- Connection pooling for performance
- Automatic reconnection with backoff
- Circuit breaker for fault tolerance

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
   # Get filter information
   info = bf.info('my_filter')
   print(f"Size in bits: {info['size_in_bits']}")
   print(f"Memory usage: {info['size_in_bits'] / 8 / 1024:.2f} KB")
   ``` 