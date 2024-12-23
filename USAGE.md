# Usage Guide

This guide provides detailed examples and test cases for each Redis-backed data structure. Each data structure is demonstrated with practical use cases and comprehensive test coverage.

## Table of Contents
- [Queue (FIFO)](#queue-fifo)
- [Stack (LIFO)](#stack-lifo)
- [Priority Queue](#priority-queue)
- [Set](#set)
- [Hash Map](#hash-map)
- [Deque](#deque)

## Queue (FIFO)

### Example: Task Queue System
The Queue example demonstrates a task processing system where tasks are processed in the order they were added (First In, First Out).

```python
from redis_data_structures import Queue

# Initialize queue
queue = Queue(host='localhost', port=6379, db=0)
queue_key = 'task_queue'

# Add tasks
queue.push(queue_key, "Process user registration")
queue.push(queue_key, "Send welcome email")

# Process tasks in FIFO order
task = queue.pop(queue_key)  # Returns "Process user registration"
```

See [queue_example.py](examples/queue_example.py) for the complete example.

### Test Cases
The Queue implementation is tested for:
- Basic push and pop operations
- Empty queue handling
- Size tracking
- FIFO ordering
- Clear operation

See [test_queue.py](tests/test_queue.py) for all test cases.

## Stack (LIFO)

### Example: Text Editor Undo System
The Stack example simulates an undo system in a text editor, where operations can be undone in reverse order (Last In, First Out).

```python
from redis_data_structures import Stack

# Initialize stack
stack = Stack(host='localhost', port=6379, db=0)
stack_key = 'undo_stack'

# Record operations
stack.push(stack_key, "Add paragraph 1")
stack.push(stack_key, "Delete paragraph 2")

# Undo operations in LIFO order
operation = stack.pop(stack_key)  # Returns "Delete paragraph 2"
```

See [stack_example.py](examples/stack_example.py) for the complete example.

### Test Cases
The Stack implementation is tested for:
- Basic push and pop operations
- Empty stack handling
- Size tracking
- LIFO ordering
- Clear operation

See [test_stack.py](tests/test_stack.py) for all test cases.

## Priority Queue

### Example: Support Ticket System
The Priority Queue example demonstrates a support ticket system where tickets are processed based on their priority level (lower number = higher priority).

```python
from redis_data_structures import PriorityQueue

# Initialize priority queue
pq = PriorityQueue(host='localhost', port=6379, db=0)
pq_key = 'support_tickets'

# Add tickets with priorities
pq.push(pq_key, "System down", 1)  # Critical priority
pq.push(pq_key, "Feature request", 3)  # Low priority

# Process highest priority first
ticket, priority = pq.pop(pq_key)  # Returns ("System down", 1)
```

See [priority_queue_example.py](examples/priority_queue_example.py) for the complete example.

### Test Cases
The Priority Queue implementation is tested for:
- Priority-based ordering
- Same priority handling
- Empty queue handling
- Size tracking
- Clear operation

See [test_priority_queue.py](tests/test_priority_queue.py) for all test cases.

## Set

### Example: User Session Tracking
The Set example shows how to track unique active user sessions, ensuring no duplicate entries.

```python
from redis_data_structures import Set

# Initialize set
set_ds = Set(host='localhost', port=6379, db=0)
set_key = 'active_users'

# Add users (duplicates are automatically handled)
set_ds.add(set_key, "user123")
set_ds.add(set_key, "user123")  # Won't add duplicate

# Check membership
is_active = set_ds.contains(set_key, "user123")  # Returns True

# Get all unique users
active_users = set_ds.members(set_key)
```

See [set_example.py](examples/set_example.py) for the complete example.

### Test Cases
The Set implementation is tested for:
- Uniqueness constraint
- Membership testing
- Add and remove operations
- Size tracking
- Clear operation

See [test_set.py](tests/test_set.py) for all test cases.

## Hash Map

### Example: User Profile Management
The Hash Map example demonstrates storing and managing user profiles with field-based access.

```python
from redis_data_structures import HashMap
import json

# Initialize hash map
hash_map = HashMap(host='localhost', port=6379, db=0)
hash_key = 'user_profiles'

# Store user profile
profile = json.dumps({
    "name": "John Doe",
    "email": "john@example.com"
})
hash_map.set(hash_key, "user123", profile)

# Retrieve profile
profile = hash_map.get(hash_key, "user123")
```

See [hash_map_example.py](examples/hash_map_example.py) for the complete example.

### Test Cases
The Hash Map implementation is tested for:
- Field-based set and get operations
- Field updates
- Field deletion
- Size tracking
- Clear operation

See [test_hash_map.py](tests/test_hash_map.py) for all test cases.

## Deque

### Example: Browser History Navigation
The Deque example shows how to implement a browser history system with forward and backward navigation.

```python
from redis_data_structures import Deque

# Initialize deque
deque = Deque(host='localhost', port=6379, db=0)
deque_key = 'browser_history'

# Add pages to history
deque.push_back(deque_key, "homepage.com")
deque.push_back(deque_key, "search.com")

# Navigate back
previous_page = deque.pop_back(deque_key)  # Returns "search.com"
deque.push_front(deque_key, previous_page)  # Save for forward navigation
```

See [deque_example.py](examples/deque_example.py) for the complete example.

### Test Cases
The Deque implementation is tested for:
- Front and back operations
- Mixed operations
- Empty deque handling
- Size tracking
- Clear operation

See [test_deque.py](tests/test_deque.py) for all test cases.

## Running Examples

To run any example:
```bash
python examples/queue_example.py
python examples/stack_example.py
# ... etc.
```

## Running Tests

To run all tests:
```bash
python -m unittest discover tests
```

To run specific test:
```bash
python -m unittest tests/test_queue.py
# ... etc.
```

## Prerequisites

- Python 3.7+
- Redis server running locally (default: localhost:6379)
- Redis Python client: `redis>=4.5.0` 