# Stack (LIFO)

A Last-In-First-Out (LIFO) stack implementation backed by Redis. Elements are processed in reverse order of addition, making it perfect for undo systems, navigation history, and function call tracking.

## Features

- LIFO ordering guarantee
- Thread-safe operations
- Persistent storage with Redis
- JSON serialization for complex data types
- Atomic operations
- Size tracking

## Operations

| Operation | Time Complexity | Description |
|-----------|----------------|-------------|
| `push`    | O(1)          | Add an item to the top of the stack |
| `pop`     | O(1)          | Remove and return the item from the top |
| `size`    | O(1)          | Get the current size of the stack |
| `clear`   | O(1)          | Remove all items from the stack |

## Basic Usage

```python
from redis_data_structures import Stack

# Initialize stack
stack = Stack(
    host='localhost',
    port=6379,
    db=0,
    username=None,  # Optional
    password=None   # Optional
)

# Basic operations
stack.push('my_stack', 'item1')
stack.push('my_stack', {'complex': 'item'})
item = stack.pop('my_stack')  # Returns {'complex': 'item'}
size = stack.size('my_stack')
stack.clear('my_stack')
```

## Example Use Cases

### 1. Undo/Redo System

Perfect for implementing undo/redo functionality in applications.

```python
class TextEditor:
    def __init__(self):
        self.undo_stack = Stack(host='localhost', port=6379)
        self.redo_stack = Stack(host='localhost', port=6379)
        self.doc_key = 'editor:document'
        self.undo_key = 'editor:undo'
        self.redo_key = 'editor:redo'
    
    def make_change(self, change: dict):
        """Apply a change and save it for undo."""
        # Save the reverse operation for undo
        reverse_change = self._create_reverse_change(change)
        self.undo_stack.push(self.undo_key, {
            'change': reverse_change,
            'timestamp': time.time()
        })
        # Clear redo stack as we have a new change
        self.redo_stack.clear(self.redo_key)
        
        # Apply the change
        self._apply_change(change)
    
    def undo(self):
        """Undo the last change."""
        last_change = self.undo_stack.pop(self.undo_key)
        if last_change:
            # Save current state for redo
            self.redo_stack.push(self.redo_key, {
                'change': self._create_reverse_change(last_change['change']),
                'timestamp': time.time()
            })
            # Apply the reverse change
            self._apply_change(last_change['change'])
    
    def redo(self):
        """Redo the last undone change."""
        redo_change = self.redo_stack.pop(self.redo_key)
        if redo_change:
            # Save current state for undo
            self.undo_stack.push(self.undo_key, {
                'change': self._create_reverse_change(redo_change['change']),
                'timestamp': time.time()
            })
            # Apply the redo change
            self._apply_change(redo_change['change'])
    
    def _create_reverse_change(self, change: dict) -> dict:
        # Implementation to create reverse operation
        pass
    
    def _apply_change(self, change: dict):
        # Implementation to apply the change
        pass

# Usage
editor = TextEditor()
editor.make_change({'type': 'insert', 'position': 10, 'text': 'Hello'})
editor.make_change({'type': 'delete', 'position': 5, 'length': 3})
editor.undo()  # Undoes the delete
editor.redo()  # Redoes the delete
```

### 2. Browser History Navigation

Ideal for implementing browser-like navigation history.

```python
class BrowserHistory:
    def __init__(self):
        self.back_stack = Stack(host='localhost', port=6379)
        self.forward_stack = Stack(host='localhost', port=6379)
        self.back_key = 'browser:back'
        self.forward_key = 'browser:forward'
        self.current_page = None
    
    def visit_page(self, url: str):
        """Navigate to a new page."""
        if self.current_page:
            self.back_stack.push(self.back_key, {
                'url': self.current_page,
                'timestamp': time.time()
            })
        self.current_page = url
        # Clear forward history
        self.forward_stack.clear(self.forward_key)
    
    def go_back(self) -> Optional[str]:
        """Navigate back to the previous page."""
        if self.back_stack.size(self.back_key) == 0:
            return None
        
        # Save current page to forward stack
        if self.current_page:
            self.forward_stack.push(self.forward_key, {
                'url': self.current_page,
                'timestamp': time.time()
            })
        
        # Go back
        previous = self.back_stack.pop(self.back_key)
        self.current_page = previous['url']
        return self.current_page
    
    def go_forward(self) -> Optional[str]:
        """Navigate forward to the next page."""
        if self.forward_stack.size(self.forward_key) == 0:
            return None
        
        # Save current page to back stack
        if self.current_page:
            self.back_stack.push(self.back_key, {
                'url': self.current_page,
                'timestamp': time.time()
            })
        
        # Go forward
        next_page = self.forward_stack.pop(self.forward_key)
        self.current_page = next_page['url']
        return self.current_page

# Usage
history = BrowserHistory()
history.visit_page('https://example.com')
history.visit_page('https://example.com/about')
history.visit_page('https://example.com/contact')
history.go_back()    # Returns to /about
history.go_back()    # Returns to /
history.go_forward() # Returns to /about
```

### 3. Function Call Stack Tracing

Great for debugging and monitoring function call hierarchies.

```python
class CallTracer:
    def __init__(self):
        self.stack = Stack(host='localhost', port=6379)
        self.trace_key = 'debug:trace'
    
    def trace_decorator(self, func):
        """Decorator to trace function calls."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Push function call info
            call_info = {
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs,
                'timestamp': time.time(),
                'depth': self.stack.size(self.trace_key)
            }
            self.stack.push(self.trace_key, call_info)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Pop the call info when function exits
                self.stack.pop(self.trace_key)
        
        return wrapper
    
    def get_current_trace(self) -> list:
        """Get the current call stack trace."""
        trace = []
        while True:
            call = self.stack.pop(self.trace_key)
            if not call:
                break
            trace.append(call)
        
        # Restore the stack
        for call in reversed(trace):
            self.stack.push(self.trace_key, call)
        
        return trace

# Usage
tracer = CallTracer()

@tracer.trace_decorator
def function_a():
    function_b()

@tracer.trace_decorator
def function_b():
    function_c()

@tracer.trace_decorator
def function_c():
    pass

function_a()
trace = tracer.get_current_trace()
```

## Best Practices

1. **Key Management**
   - Use descriptive key names: `stack:history`, `stack:undo`, etc.
   - Consider implementing key expiration for temporary stacks
   - Clear stacks that are no longer needed

2. **Error Handling**
   ```python
   try:
       stack.push('my_stack', item)
   except redis.RedisError as e:
       logger.error(f"Redis error: {e}")
       # Handle error...
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
       # Handle error...
   ```

3. **Memory Management**
   - Monitor stack size to prevent memory issues
   - Implement size limits if needed
   ```python
   if stack.size('my_stack') > MAX_SIZE:
       oldest = stack.pop('my_stack')
       # Handle stack overflow...
   ```

4. **Performance**
   - Use batch operations when possible
   - Consider cleanup strategies for long-running stacks

## Common Patterns

### 1. State Management
```python
class StateManager:
    def __init__(self):
        self.states = Stack(host='localhost', port=6379)
        self.key = 'app:states'
    
    def save_state(self, state: dict):
        self.states.push(self.key, state)
    
    def restore_previous_state(self) -> Optional[dict]:
        return self.states.pop(self.key)
```

### 2. Transaction Rollback
```python
class TransactionManager:
    def __init__(self):
        self.rollbacks = Stack(host='localhost', port=6379)
        self.key = 'tx:rollbacks'
    
    def execute_operation(self, operation: dict):
        # Save rollback information
        rollback = self._create_rollback(operation)
        self.rollbacks.push(self.key, rollback)
        
        try:
            self._execute(operation)
        except:
            self.rollback()
            raise
    
    def rollback(self):
        while True:
            operation = self.rollbacks.pop(self.key)
            if not operation:
                break
            self._execute_rollback(operation)
```

### 3. Depth-First Search
```python
def depth_first_search(graph: Dict[str, List[str]], start: str):
    stack = Stack(host='localhost', port=6379)
    visited = set()
    stack_key = 'dfs:stack'
    
    stack.push(stack_key, start)
    
    while stack.size(stack_key) > 0:
        vertex = stack.pop(stack_key)
        if vertex not in visited:
            visited.add(vertex)
            for neighbor in graph[vertex]:
                if neighbor not in visited:
                    stack.push(stack_key, neighbor)
```

## Limitations

1. **No Random Access**
   - Can only access the top element
   - Must pop elements to access ones below

2. **No Size Limit**
   - Need to implement size limits manually
   - Memory usage grows linearly

3. **No Peek Operation**
   - Cannot view top element without removing it
   - Must implement peek using pop and push

## Performance Considerations

1. **Network Latency**
   - Redis operations are network calls
   - Consider batch operations for better throughput

2. **Memory Usage**
   - Each element adds to Redis memory
   - Consider cleanup strategies for old data

3. **Concurrency**
   - Operations are atomic
   - Safe for multi-threaded use

## Troubleshooting

1. **Stack Empty Unexpectedly**
   - Check Redis connection
   - Verify key names
   - Check if items are being pushed correctly

2. **Memory Issues**
   - Monitor stack size
   - Implement size limits
   - Clear old/unused stacks

3. **Slow Operations**
   - Check network latency
   - Consider batch operations
   - Monitor Redis performance
