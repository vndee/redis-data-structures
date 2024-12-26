# Queue (FIFO)

A Redis-backed FIFO (First-In-First-Out) queue implementation. Perfect for job queues, message passing, and any application requiring ordered processing of items.

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | :---: | :---: | --- | --- |
| `push` | $O(1)$ | $O(1)$ | Add an item to the back of the queue | `RPUSH` |
| `pop` | $O(n)$ | $O(n)$ | Remove and return the oldest item | `LPOP` |
| `peek` | $O(1)$ | $O(1)$ | Return the oldest item without removing it | `LINDEX` |
| `size` | $O(1)$ | $O(1)$ | Return the number of items in the queue | `LLEN` |
| `clear` | $O(1)$ | $O(1)$ | Remove all items from the queue | `DELETE` |

where:

- $n$ is the number of items in the queue.

> **Note:** `pop` is $O(n)$ because we use `LPOP` of Redis List which is $O(n)$ operation.

## Basic Usage

```python
from redis_data_structures import Queue

# Initialize queue
queue = Queue("task_queue")

# Add items
queue.push("task1")
queue.push("task2")

# Get items (FIFO order)
task = queue.pop()  # Returns "task1"

# Check size
size = queue.size()  # Returns 1

# Peek at next item without removing
next_task = queue.peek()  # Returns "task2" without removing it

# Clear the queue
queue.clear()
```

## Advanced Usage

```python
from redis_data_structures import Queue

# Initialize queue
queue = Queue("tasks")

# Store complex data types
task = {
    "type": "user",
    "action": "registration",
    "data": {
        "email": "user@example.com"
    }
}
queue.push(task)

# Process tasks with error handling
while queue.size() > 0:
    task = queue.pop()
    if task:
        print(f"Processing: {task['type']}_{task['action']}")
    else:
        print("Error retrieving task")
```

## Example Use Cases

### 1. Task Processing System

```python
from redis_data_structures import Queue
import time

class TaskProcessor:
    def __init__(self):
        self.queue = Queue("task_queue")
    
    def add_task(self, task_type: str, action: str, data: dict):
        """Add a task to the queue."""
        task = {
            "type": task_type,
            "action": action,
            "data": data
        }
        return self.queue.push(task)
    
    def process_tasks(self):
        """Process all tasks in the queue."""
        while self.queue.size() > 0:
            task = self.queue.pop()
            if task:
                print(f"Processing: {task['type']}_{task['action']}")
                # Process task logic here
                time.sleep(1)  # Simulate processing time
            else:
                print("Error retrieving task")

# Usage
processor = TaskProcessor()
processor.add_task("user", "registration", {"email": "user@example.com"})
processor.add_task("email", "welcome", {"template": "welcome_email"})
processor.process_tasks()
```

### 2. Message Queue

```python
from redis_data_structures import Queue
from typing import Dict, Any

class MessageQueue:
    def __init__(self):
        self.queue = Queue("messages")
    
    def send_message(self, message_type: str, data: Dict[str, Any]):
        """Send a message to the queue."""
        message = {
            "type": message_type,
            "data": data
        }
        return self.queue.push(message)
    
    def get_next_message(self) -> Dict[str, Any]:
        """Get next message from queue."""
        return self.queue.pop()
    
    def preview_next_message(self) -> Dict[str, Any]:
        """Preview next message without removing."""
        return self.queue.peek()

# Usage
mq = MessageQueue()
mq.send_message("notification", {"user_id": 123, "content": "Hello!"})
message = mq.get_next_message()
```
