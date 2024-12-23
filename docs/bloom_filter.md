# Bloom Filter

A Redis-backed Bloom Filter implementation for probabilistic set membership testing. Perfect for reducing unnecessary database lookups, deduplication, and caching optimization.

## Features

- Space-efficient probabilistic data structure
- Configurable false positive rate
- Thread-safe operations
- Persistent storage with Redis
- Atomic operations
- No false negatives

## Operations

| Operation  | Time Complexity | Description |
|-----------|----------------|-------------|
| `add`     | O(k)          | Add an item to the filter |
| `contains`| O(k)          | Check if an item might exist |
| `clear`   | O(1)          | Clear the filter |
| `size`    | O(1)          | Get bit array size |

Where k is the number of hash functions (typically small and constant).

## Basic Usage

```python
from redis_data_structures import BloomFilter

# Initialize bloom filter
bf = BloomFilter(
    expected_elements=10000,  # Expected number of items
    false_positive_rate=0.01, # 1% false positive rate
    host='localhost',
    port=6379,
    db=0,
    username=None,  # Optional
    password=None   # Optional
)

# Basic operations
bf.add('my_filter', 'item1')
exists = bf.contains('my_filter', 'item1')  # Returns True
exists = bf.contains('my_filter', 'item2')  # Returns False
bf.clear('my_filter')
```

## Example Use Cases

### 1. Cache Miss Prevention

Perfect for reducing unnecessary database lookups by checking if a key definitely doesn't exist.

```python
class CacheOptimizer:
    def __init__(self, expected_keys: int = 1000000):
        self.bloom = BloomFilter(
            expected_elements=expected_keys,
            false_positive_rate=0.01
        )
        self.cache_key = 'cache:keys'
    
    def should_check_cache(self, key: str) -> bool:
        """Check if key might exist in cache."""
        return self.bloom.contains(self.cache_key, key)
    
    def add_to_cache(self, key: str, value: Any):
        """Add key to cache and Bloom filter."""
        # Add to actual cache (e.g., Redis)
        self._set_cache(key, value)
        # Add to Bloom filter
        self.bloom.add(self.cache_key, key)
    
    def get_value(self, key: str) -> Optional[Any]:
        """Get value using Bloom filter optimization."""
        # Check Bloom filter first
        if not self.should_check_cache(key):
            # Definitely not in cache
            return None
        
        # Might be in cache, check actual cache
        return self._get_cache(key)
    
    def _set_cache(self, key: str, value: Any):
        # Actual cache implementation
        pass
    
    def _get_cache(self, key: str) -> Optional[Any]:
        # Actual cache implementation
        pass

# Usage
cache = CacheOptimizer(expected_keys=1000000)
cache.add_to_cache('user:123', {'name': 'John'})
value = cache.get_value('user:123')  # Checks Bloom filter first
```

### 2. URL Deduplication

Ideal for checking if a URL has already been crawled in web crawlers.

```python
class URLDeduplicator:
    def __init__(self, expected_urls: int = 1000000):
        self.bloom = BloomFilter(
            expected_elements=expected_urls,
            false_positive_rate=0.001  # Lower false positive rate for URLs
        )
        self.urls_key = 'crawler:urls'
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL to avoid duplicates."""
        parsed = urlparse(url)
        # Remove trailing slash, query params, etc.
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
        return normalized.lower()
    
    def is_new_url(self, url: str) -> bool:
        """Check if URL hasn't been seen before."""
        normalized = self.normalize_url(url)
        if self.bloom.contains(self.urls_key, normalized):
            return False
        
        self.bloom.add(self.urls_key, normalized)
        return True
    
    def mark_url_seen(self, url: str):
        """Mark URL as seen."""
        normalized = self.normalize_url(url)
        self.bloom.add(self.urls_key, normalized)

# Usage
dedup = URLDeduplicator()
is_new = dedup.is_new_url('https://example.com')  # Returns True
is_new = dedup.is_new_url('https://example.com/')  # Returns False (normalized)
```

### 3. Email Deduplication

Perfect for checking if an email has been sent to avoid duplicates.

```python
class EmailDeduplicator:
    def __init__(self, campaign_id: str, expected_emails: int):
        self.bloom = BloomFilter(
            expected_elements=expected_emails,
            false_positive_rate=0.0001  # Very low false positive rate for emails
        )
        self.campaign_id = campaign_id
        self.filter_key = f'campaign:{campaign_id}:emails'
    
    def is_email_sent(self, email: str) -> bool:
        """Check if email was already sent."""
        return self.bloom.contains(self.filter_key, email.lower())
    
    def mark_email_sent(self, email: str):
        """Mark email as sent."""
        self.bloom.add(self.filter_key, email.lower())
    
    def process_email(self, email: str) -> bool:
        """Process email if not sent yet."""
        if self.is_email_sent(email):
            return False
        
        # Send email
        self._send_email(email)
        self.mark_email_sent(email)
        return True
    
    def _send_email(self, email: str):
        # Actual email sending implementation
        pass

# Usage
dedup = EmailDeduplicator('campaign123', expected_emails=100000)
is_new = dedup.process_email('user@example.com')  # Returns True
is_new = dedup.process_email('user@example.com')  # Returns False
```

## Best Practices

1. **Sizing**
   - Set expected elements higher than actual
   - Choose false positive rate based on use case
   ```python
   # High accuracy but more memory
   accurate = BloomFilter(
       expected_elements=1000000,
       false_positive_rate=0.0001
   )
   
   # Memory efficient but more false positives
   efficient = BloomFilter(
       expected_elements=1000000,
       false_positive_rate=0.01
   )
   ```

2. **Error Handling**
   ```python
   try:
       bf.add('my_filter', item)
   except redis.RedisError as e:
       logger.error(f"Redis error: {e}")
       # Handle error...
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
       # Handle error...
   ```

3. **Key Management**
   - Use descriptive key names: `bloom:emails`, `bloom:urls`, etc.
   - Consider implementing key expiration
   - Clear filters that are no longer needed

4. **Performance**
   - Choose appropriate hash functions
   - Monitor false positive rate
   - Consider batch operations

## Common Patterns

### 1. Cascading Bloom Filters
```python
class CascadingBloomFilter:
    def __init__(self, sizes: list[int], rates: list[float]):
        self.filters = [
            BloomFilter(expected_elements=size, false_positive_rate=rate)
            for size, rate in zip(sizes, rates)
        ]
    
    def add(self, key: str, item: Any):
        """Add item to all filters."""
        for bf in self.filters:
            bf.add(key, item)
    
    def contains(self, key: str, item: Any) -> bool:
        """Check filters in sequence."""
        for bf in self.filters:
            if not bf.contains(key, item):
                return False
        return True
```

### 2. Counting with Reset
```python
class ResettableCounter:
    def __init__(self, window_size: int = 3600):
        self.bloom = BloomFilter(
            expected_elements=100000,
            false_positive_rate=0.01
        )
        self.window_size = window_size
        self.current_window = 0
    
    def increment(self, key: str, item: Any) -> bool:
        """Increment counter for current window."""
        window = int(time.time() / self.window_size)
        if window > self.current_window:
            # New window, clear old data
            self.bloom.clear(key)
            self.current_window = window
        
        # Check if already counted in this window
        if self.bloom.contains(key, f"{item}:{window}"):
            return False
        
        self.bloom.add(key, f"{item}:{window}")
        return True
```

### 3. Hierarchical Filtering
```python
class HierarchicalFilter:
    def __init__(self):
        self.domain_filter = BloomFilter(
            expected_elements=10000,
            false_positive_rate=0.01
        )
        self.url_filter = BloomFilter(
            expected_elements=1000000,
            false_positive_rate=0.001
        )
    
    def add_url(self, url: str):
        """Add URL and domain to filters."""
        domain = urlparse(url).netloc
        self.domain_filter.add('domains', domain)
        self.url_filter.add('urls', url)
    
    def should_crawl(self, url: str) -> bool:
        """Check if URL should be crawled."""
        domain = urlparse(url).netloc
        
        # Check domain first (coarse filter)
        if not self.domain_filter.contains('domains', domain):
            return True
        
        # Check specific URL (fine filter)
        return not self.url_filter.contains('urls', url)
```

## Limitations

1. **Cannot Remove Elements**
   - No support for element removal
   - Must create new filter to remove elements

2. **False Positives**
   - May return true for non-existent items
   - False positive rate increases with fullness

3. **Size is Fixed**
   - Cannot resize after creation
   - Must estimate capacity in advance

## Performance Considerations

1. **Memory Usage**
   - Size depends on expected elements and false positive rate
   - Memory usage is fixed regardless of actual elements

2. **Hash Functions**
   - More hash functions increase accuracy but slow operations
   - Optimal number calculated based on size and elements

3. **Concurrency**
   - Operations are atomic
   - Safe for multi-threaded use

## Troubleshooting

1. **High False Positive Rate**
   - Check if filter is too full
   - Verify expected elements estimate
   - Consider lower false positive rate

2. **Memory Issues**
   - Monitor bit array size
   - Check Redis memory usage
   - Consider higher false positive rate

3. **Performance Issues**
   - Check number of hash functions
   - Consider batch operations
   - Monitor Redis performance 