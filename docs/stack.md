# Stack (LIFO)

A Redis-backed LIFO (Last-In-First-Out) stack implementation. Perfect for managing execution contexts, undo operations, and any application requiring last-in-first-out processing.

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | --- | --- | --- | --- |
| `push` | $O(1)$ | $O(1)$ | Add an item to the top of the stack | `LPUSH` |
| `pop` | $O(1)$ | $O(1)$ | Remove and return the top item | `LPOP` |
| `peek` | $O(1)$ | $O(1)$ | Return the top item without removing it | `LINDEX` |
| `size` | $O(1)$ | $O(1)$ | Return the number of items in the stack | `LLEN` |
| `clear` | $O(1)$ | $O(1)$ | Remove all items from the stack | `DELETE` |

## Basic Usage

```python
from redis_data_structures import Stack

# Initialize stack
stack = Stack()
stack_key = "undo_stack"

# Add items
stack.push(stack_key, "operation1")
stack.push(stack_key, "operation2")

# Get items (LIFO order)
operation = stack.pop(stack_key)  # Returns "operation2"

# Check size
size = stack.size(stack_key)  # Returns 1

# Peek at top item without removing
next_operation = stack.peek(stack_key)  # Returns "operation1" without removing it

# Clear the stack
stack.clear(stack_key)
```

## Advanced Usage

```python
from redis_data_structures import Stack

# Initialize stack
stack = Stack()
stack_key = "operations"

# Store complex data types
operation = {
    "type": "edit",
    "action": "delete",
    "data": {
        "line": 10,
        "content": "Hello World"
    }
}
stack.push(stack_key, operation)

# Process operations with error handling
while stack.size(stack_key) > 0:
    operation = stack.pop(stack_key)
    if operation:
        print(f"Undoing: {operation['type']}_{operation['action']}")
    else:
        print("Error retrieving operation")
```

## Example Use Cases

### 1. Text Editor Undo System

```python
from redis_data_structures import Stack
from typing import Dict, Any

class UndoSystem:
    def __init__(self):
        self.stack = Stack()
        self.stack_key = "undo_operations"
    
    def add_operation(self, operation_type: str, data: Dict[str, Any]):
        """Add an operation to the undo stack."""
        operation = {
            "type": operation_type,
            "data": data
        }
        return self.stack.push(self.stack_key, operation)
    
    def undo(self) -> Dict[str, Any]:
        """Undo the last operation."""
        return self.stack.pop(self.stack_key)
    
    def peek_last_operation(self) -> Dict[str, Any]:
        """Preview the last operation without undoing."""
        return self.stack.peek(self.stack_key)

# Usage
undo_system = UndoSystem()
undo_system.add_operation("insert", {"position": 10, "text": "Hello"})
undo_system.add_operation("delete", {"start": 5, "end": 10})
last_operation = undo_system.undo()  # Undoes the delete operation
```

### 2. Navigation History

```python
from redis_data_structures import Stack
from typing import Dict, Any

class NavigationHistory:
    def __init__(self):
        self.stack = Stack()
        self.stack_key = "navigation"
    
    def visit_page(self, url: str, title: str):
        """Record a page visit."""
        page = {
            "url": url,
            "title": title
        }
        return self.stack.push(self.stack_key, page)
    
    def go_back(self) -> Dict[str, Any]:
        """Navigate to previous page."""
        return self.stack.pop(self.stack_key)
    
    def current_page(self) -> Dict[str, Any]:
        """Get current page without navigating away."""
        return self.stack.peek(self.stack_key)

# Usage
history = NavigationHistory()
history.visit_page("/home", "Home Page")
history.visit_page("/products", "Products")
previous_page = history.go_back()  # Returns to Home Page
```
