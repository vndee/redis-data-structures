# Redis Data Structures Usage Guide

This document provides detailed usage examples and best practices for each data structure in the redis-data-structures package.

## Table of Contents
- [Installation](#installation)
- [Basic Setup](#basic-setup)
- [Data Structures](#data-structures)
  - [Queue](#queue)
  - [Stack](#stack)
  - [Priority Queue](#priority-queue)
  - [Set](#set)
  - [Hash Map](#hash-map)
  - [Deque](#deque)
  - [Bloom Filter](#bloom-filter)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Installation

Install the package using pip:

```bash
pip install redis-data-structures
```

For development installation with additional tools:

```bash
pip install redis-data-structures[dev]
```

## Basic Setup

Before using any data structure, ensure Redis is running. You can use Docker (recommended) or a local installation.

Using Docker:
```bash
# Start Redis
docker run --name redis-ds -p 6379:6379 -d redis:latest

# Stop Redis
docker stop redis-ds
docker rm redis-ds
```

Local installation:
```bash
# macOS
brew services start redis

# Ubuntu/Debian
sudo service redis-server start
```

## Data Structures

### Queue (FIFO)

A First-In-First-Out queue where elements are processed in the order they were added.

#### Example Use Cases

1. **Task Processing System**
```python
from redis_data_structures import Queue

queue = Queue(host='localhost', port=6379)

# Producer: Add tasks to the queue
def schedule_task(task_data: dict):
    queue.push('tasks:processing', task_data)

# Consumer: Process tasks in order
def process_next_task():
    task = queue.pop('tasks:processing')
    if task:
        # Process the task
        print(f"Processing task: {task}")

# Example usage
schedule_task({"type": "email", "to": "user@example.com"})
schedule_task({"type": "notification", "user_id": 123})
```

2. **Print Job Management**
```python
def add_print_job(document: str, user: str):
    queue.push('printer:jobs', {
        'document': document,
        'user': user,
        'timestamp': time.time()
    })

def process_print_jobs():
    while True:
        job = queue.pop('printer:jobs')
        if job:
            print_document(job['document'])
```

3. **Event Processing Pipeline**
```python
def log_event(event_type: str, data: dict):
    queue.push('events:processing', {
        'type': event_type,
        'data': data,
        'timestamp': time.time()
    })
```

### Stack (LIFO)

A Last-In-First-Out stack where the most recently added element is processed first.

#### Example Use Cases

1. **Undo/Redo System**
```python
from redis_data_structures import Stack

class TextEditor:
    def __init__(self):
        self.undo_stack = Stack(host='localhost', port=6379)
        self.doc_key = 'editor:undo'
    
    def make_change(self, change: dict):
        # Save the reverse operation for undo
        self.undo_stack.push(self.doc_key, {
            'operation': 'undo',
            'change': change,
            'timestamp': time.time()
        })
    
    def undo(self):
        last_change = self.undo_stack.pop(self.doc_key)
        if last_change:
            # Apply the reverse operation
            apply_change(last_change['change'])
```

2. **Navigation History**
```python
class BrowserHistory:
    def __init__(self):
        self.history = Stack(host='localhost', port=6379)
        self.key = 'browser:history'
    
    def visit_page(self, url: str):
        self.history.push(self.key, {
            'url': url,
            'timestamp': time.time()
        })
    
    def go_back(self):
        return self.history.pop(self.key)
```

3. **Function Call Stack Tracing**
```python
def trace_function_calls():
    stack = Stack(host='localhost', port=6379)
    trace_key = 'debug:trace'
    
    def trace_decorator(func):
        def wrapper(*args, **kwargs):
            stack.push(trace_key, {
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs
            })
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                stack.pop(trace_key)
        return wrapper
    return trace_decorator
```

### Priority Queue

A queue where elements are processed based on their priority level (lower number = higher priority).

#### Example Use Cases

1. **Hospital Emergency Room Triage**
```python
from redis_data_structures import PriorityQueue

class ERSystem:
    def __init__(self):
        self.patients = PriorityQueue(host='localhost', port=6379)
        self.er_key = 'hospital:er'
    
    def add_patient(self, patient: dict, severity: int):
        # Severity: 1 (Critical) to 5 (Non-urgent)
        self.patients.push(self.er_key, patient, severity)
    
    def get_next_patient(self):
        return self.patients.pop(self.er_key)

# Usage
er = ERSystem()
er.add_patient({"name": "John", "condition": "Heart Attack"}, 1)  # Critical
er.add_patient({"name": "Jane", "condition": "Sprained Ankle"}, 4)  # Non-urgent
```

2. **Task Scheduler with Priorities**
```python
class TaskScheduler:
    def __init__(self):
        self.tasks = PriorityQueue(host='localhost', port=6379)
        self.key = 'scheduler:tasks'
    
    def schedule_task(self, task: dict, priority: int):
        self.tasks.push(self.key, task, priority)
    
    def execute_next_task(self):
        task, priority = self.tasks.pop(self.key)
        if task:
            print(f"Executing task (priority {priority}): {task}")
```

3. **Network Packet Processing**
```python
def process_network_packets():
    packets = PriorityQueue(host='localhost', port=6379)
    
    # Priority levels:
    # 1: System critical
    # 2: Real-time (video/audio)
    # 3: Interactive
    # 4: Background
    
    def enqueue_packet(packet: dict, packet_type: str):
        priorities = {
            'system': 1,
            'realtime': 2,
            'interactive': 3,
            'background': 4
        }
        packets.push('network:packets', packet, priorities[packet_type])
```

### Set

A collection of unique elements with efficient membership testing.

#### Example Use Cases

1. **User Session Management**
```python
from redis_data_structures import Set

class SessionManager:
    def __init__(self):
        self.active_sessions = Set(host='localhost', port=6379)
        self.key = 'sessions:active'
    
    def start_session(self, session_id: str):
        self.active_sessions.add(self.key, session_id)
    
    def end_session(self, session_id: str):
        self.active_sessions.remove(self.key, session_id)
    
    def is_session_active(self, session_id: str):
        return self.active_sessions.contains(self.key, session_id)
```

2. **Tag Management System**
```python
class TagSystem:
    def __init__(self):
        self.tags = Set(host='localhost', port=6379)
    
    def add_tags_to_item(self, item_id: str, tags: list[str]):
        key = f'tags:{item_id}'
        for tag in tags:
            self.tags.add(key, tag)
    
    def has_tag(self, item_id: str, tag: str):
        return self.tags.contains(f'tags:{item_id}', tag)
```

3. **Unique Visitor Tracking**
```python
class VisitorTracker:
    def __init__(self):
        self.visitors = Set(host='localhost', port=6379)
    
    def track_visitor(self, visitor_id: str, page: str):
        key = f'visitors:{page}'
        self.visitors.add(key, visitor_id)
    
    def get_unique_visitors(self, page: str):
        return self.visitors.members(f'visitors:{page}')
```

### Hash Map

A key-value store where each key can have multiple fields with values.

#### Example Use Cases

1. **User Profile System**
```python
from redis_data_structures import HashMap

class UserProfiles:
    def __init__(self):
        self.profiles = HashMap(host='localhost', port=6379)
        self.key = 'users:profiles'
    
    def update_profile(self, user_id: str, field: str, value: str):
        self.profiles.set(self.key, user_id, {field: value})
    
    def get_profile(self, user_id: str):
        return self.profiles.get(self.key, user_id)
```

2. **Configuration Management**
```python
class ConfigManager:
    def __init__(self):
        self.config = HashMap(host='localhost', port=6379)
        self.key = 'app:config'
    
    def set_config(self, component: str, settings: dict):
        self.config.set(self.key, component, settings)
    
    def get_config(self, component: str):
        return self.config.get(self.key, component)
```

3. **Shopping Cart**
```python
class ShoppingCart:
    def __init__(self):
        self.carts = HashMap(host='localhost', port=6379)
    
    def add_item(self, cart_id: str, item_id: str, quantity: int):
        key = f'cart:{cart_id}'
        current = self.carts.get(key, item_id) or 0
        self.carts.set(key, item_id, current + quantity)
    
    def get_cart(self, cart_id: str):
        return self.carts.get_all(f'cart:{cart_id}')
```

### Deque (Double-ended Queue)

A queue that supports adding and removing elements from both ends.

#### Example Use Cases

1. **Sliding Window Analysis**
```python
from redis_data_structures import Deque

class SlidingWindow:
    def __init__(self, window_size: int):
        self.deque = Deque(host='localhost', port=6379)
        self.window_size = window_size
    
    def add_datapoint(self, key: str, value: float):
        self.deque.push_back(key, value)
        if self.deque.size(key) > self.window_size:
            self.deque.pop_front(key)
```

2. **Browser History with Forward/Back**
```python
class EnhancedBrowserHistory:
    def __init__(self):
        self.history = Deque(host='localhost', port=6379)
        self.key = 'browser:enhanced_history'
    
    def visit_page(self, url: str):
        self.history.push_back(self.key, url)
    
    def go_back(self):
        if self.history.size(self.key) > 1:
            current = self.history.pop_back(self.key)
            self.history.push_front(self.key, current)
            return self.history.peek_back(self.key)
    
    def go_forward(self):
        if self.history.size(self.key) > 0:
            return self.history.pop_front(self.key)
```

3. **Work Stealing Queue**
```python
class WorkStealingQueue:
    def __init__(self, worker_id: str):
        self.deque = Deque(host='localhost', port=6379)
        self.worker_id = worker_id
    
    def add_task(self, task: dict):
        # Add to the back for LIFO processing
        self.deque.push_back(f'worker:{self.worker_id}', task)
    
    def get_own_task(self):
        # Get from back (LIFO for better locality)
        return self.deque.pop_back(f'worker:{self.worker_id}')
    
    def steal_task(self, from_worker: str):
        # Steal from front (FIFO for better work distribution)
        return self.deque.pop_front(f'worker:{from_worker}')
```

### Bloom Filter

The Bloom Filter is a space-efficient probabilistic data structure used to test whether an element is a member of a set. It may produce false positives (indicating an element is in the set when it's not) but never false negatives (saying an element is not in the set when it is).

#### Basic Usage

```python
from redis_data_structures import BloomFilter

# Initialize with expected number of elements and desired false positive rate
bloom = BloomFilter(
    expected_elements=10000,  # Expected number of items to be added
    false_positive_rate=0.01  # 1% false positive rate
)

# Add items to the filter
bloom.add('my_filter', 'user@example.com')
bloom.add('my_filter', 'another@example.com')

# Check membership
exists = bloom.contains('my_filter', 'user@example.com')  # Returns True
exists = bloom.contains('my_filter', 'unknown@example.com')  # Returns False
```

#### Advanced Usage

```python
# Using with different data types
bloom.add('my_filter', 42)  # Numbers
bloom.add('my_filter', {'key': 'value'})  # Dictionaries
bloom.add('my_filter', ['list', 'items'])  # Lists
bloom.add('my_filter', ('tuple', 'items'))  # Tuples

# Clear the filter
bloom.clear('my_filter')

# Get filter size in bits
size = bloom.size('my_filter')
```

#### Configuration and Optimization

The Bloom Filter's performance and accuracy depend on two main parameters:

1. `expected_elements`: The expected number of elements to be added
2. `false_positive_rate`: The acceptable false positive probability

```python
# For high accuracy but more memory usage
high_accuracy = BloomFilter(
    expected_elements=1000000,
    false_positive_rate=0.001  # 0.1% false positive rate
)

# For memory efficiency but higher false positive rate
memory_efficient = BloomFilter(
    expected_elements=1000000,
    false_positive_rate=0.05  # 5% false positive rate
)
```

#### Common Use Cases

1. **Email Deduplication**
```python
def is_email_seen(email: str) -> bool:
    bloom = BloomFilter(expected_elements=1000000, false_positive_rate=0.01)
    if bloom.contains('seen_emails', email):
        return True
    bloom.add('seen_emails', email)
    return False
```

2. **Cache Optimization**
```python
def should_query_database(key: str) -> bool:
    bloom = BloomFilter(expected_elements=100000, false_positive_rate=0.01)
    return not bloom.contains('cache_keys', key)

def cache_item(key: str, value: Any) -> None:
    bloom = BloomFilter(expected_elements=100000, false_positive_rate=0.01)
    bloom.add('cache_keys', key)
    # Add to actual cache...
```

3. **URL Shortener**
```python
def is_url_unique(url: str) -> bool:
    bloom = BloomFilter(expected_elements=1000000, false_positive_rate=0.01)
    return not bloom.contains('urls', url)

def add_url(url: str) -> None:
    if is_url_unique(url):
        bloom = BloomFilter(expected_elements=1000000, false_positive_rate=0.01)
        bloom.add('urls', url)
        # Generate short URL...
```

#### Performance Considerations

1. **Memory Usage**
   - The memory usage is determined by the `expected_elements` and `false_positive_rate`
   - Lower false positive rates require more memory
   - The actual memory usage in bits is: `-n * ln(p) / (ln(2)²)`
   where n is `expected_elements` and p is `false_positive_rate`

2. **Number of Hash Functions**
   - The optimal number of hash functions is: `(m/n) * ln(2)`
   where m is the filter size in bits and n is `expected_elements`
   - More hash functions mean better accuracy but slower operations

3. **Redis Performance**
   - Uses Redis bit arrays (`SETBIT`/`GETBIT`) for efficient storage
   - Operations are O(k) where k is the number of hash functions
   - Uses pipelining for better performance when setting multiple bits

#### Best Practices

1. **Sizing**
   - Always set `expected_elements` higher than the actual expected number
   - Choose `false_positive_rate` based on your application's tolerance for false positives
   - Monitor the actual false positive rate in production

2. **Key Management**
   - Use descriptive key names: `bloom:emails`, `bloom:urls`, etc.
   - Consider implementing key expiration for temporary filters
   - Clear filters that are no longer needed

3. **Error Handling**
   - Always check return values for operations
   - Implement proper error handling for Redis connection issues
   - Consider implementing retry logic for critical operations

#### Limitations

1. **Cannot Remove Elements**
   - Bloom Filters do not support element removal
   - If you need removal, consider using Counting Bloom Filters (not implemented)

2. **False Positives**
   - False positives are possible and their rate increases as the filter fills up
   - Cannot retrieve the actual elements in the set

3. **Size is Fixed**
   - The size is set at initialization and cannot be changed
   - If you need to store more elements, create a new filter with larger capacity

#### Example: Web Crawler

Here's a complete example of using a Bloom Filter in a web crawler to avoid visiting the same URL twice:

```python
from redis_data_structures import BloomFilter
from urllib.parse import urlparse
import requests

class WebCrawler:
    def __init__(self):
        self.bloom = BloomFilter(
            expected_elements=1000000,  # Expect to crawl 1M URLs
            false_positive_rate=0.001   # Very low false positive rate
        )
        self.filter_key = 'crawler:visited_urls'

    def normalize_url(self, url: str) -> str:
        """Normalize URL to avoid duplicates due to different formats."""
        parsed = urlparse(url)
        return f"{parsed.netloc}{parsed.path.rstrip('/')}"

    def should_crawl(self, url: str) -> bool:
        """Check if URL should be crawled."""
        normalized = self.normalize_url(url)
        if self.bloom.contains(self.filter_key, normalized):
            return False
        self.bloom.add(self.filter_key, normalized)
        return True

    def crawl(self, start_url: str):
        """Simple crawler implementation."""
        if not self.should_crawl(start_url):
            return

        try:
            response = requests.get(start_url)
            # Process the page...
            print(f"Crawled: {start_url}")
        except Exception as e:
            print(f"Error crawling {start_url}: {e}")

# Usage
crawler = WebCrawler()
crawler.crawl('https://example.com')
```

This example demonstrates:
- Proper initialization with reasonable parameters
- URL normalization to avoid duplicates
- Error handling
- Integration with other components

Remember to adjust the `expected_elements` and `false_positive_rate` based on your specific needs and available memory.

## Error Handling

## Best Practices