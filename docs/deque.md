# Deque (Double-ended Queue)

A Redis-backed double-ended queue implementation that allows efficient insertion and removal of elements at both ends. Perfect for implementing browser history navigation, work stealing queues, undo/redo functionality, and other scenarios requiring bidirectional access.

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | :---: | :---: | --- | --- |
| `push_front` | $O(1)$ | $O(1)$ | Add an item to the front | `LPUSH` |
| `push_back` | $O(1)$ | $O(1)$ | Add an item to the back | `RPUSH` |
| `pop_front` | $O(n)$ | $O(n)$ | Remove and return the front item | `LPOP` |
| `pop_back` | $O(n)$ | $O(n)$ | Remove and return the back item | `RPOP` |
| `peek_front` | $O(1)$ | $O(1)$ | Return the front item without removing | `LINDEX 0` |
| `peek_back` | $O(1)$ | $O(1)$ | Return the back item without removing | `LINDEX -1` |
| `size` | $O(1)$ | $O(1)$ | Return the number of items | `LLEN` |
| `clear` | $O(1)$ | $O(1)$ | Remove all items | `DELETE` |

where:
- $n$ is the number of items in the deque.

> **Note:** `pop_front` and `pop_back` are $O(n)$ because we use `LPOP` and `RPOP` of Redis List which are $O(n)$ operations.

## Basic Usage

```python
from redis_data_structures import Deque

# Initialize deque
deque = Deque(key="my_deque")

# Add items at both ends
deque.push_front("first")
deque.push_back("last")

# Remove items from both ends
front_item = deque.pop_front()  # Returns "first"
back_item = deque.pop_back()    # Returns "last"

# Peek without removing
front = deque.peek_front()
back = deque.peek_back()

# Get size
size = deque.size()

# Clear all items
deque.clear()
```

## Advanced Usage

```python
from redis_data_structures import Deque
from typing import Any, Optional
from dataclasses import dataclass
import json

@dataclass
class BrowserState:
    url: str
    title: str
    scroll_position: int

class BrowserHistory:
    def __init__(self):
        self.deque = Deque(key="browser_history")
        self.current_index = 0
    
    def _serialize_state(self, state: BrowserState) -> str:
        """Serialize browser state to string."""
        return json.dumps({
            "url": state.url,
            "title": state.title,
            "scroll_position": state.scroll_position
        })
    
    def _deserialize_state(self, state_str: str) -> BrowserState:
        """Deserialize string to browser state."""
        data = json.loads(state_str)
        return BrowserState(
            url=data["url"],
            title=data["title"],
            scroll_position=data["scroll_position"]
        )
    
    def visit_page(self, url: str, title: str):
        """Record new page visit."""
        state = BrowserState(url=url, title=title, scroll_position=0)
        self.deque.push_back(self._serialize_state(state))
        self.current_index = self.deque.size() - 1
    
    def go_back(self) -> Optional[BrowserState]:
        """Navigate to previous page."""
        if self.current_index > 0:
            self.current_index -= 1
            state_str = self.deque.peek_back()
            return self._deserialize_state(state_str) if state_str else None
        return None
    
    def go_forward(self) -> Optional[BrowserState]:
        """Navigate to next page."""
        if self.current_index < self.deque.size() - 1:
            self.current_index += 1
            state_str = self.deque.peek_front()
            return self._deserialize_state(state_str) if state_str else None
        return None

# Usage
history = BrowserHistory()
history.visit_page("https://example.com", "Home")
history.visit_page("https://example.com/about", "About")
previous_page = history.go_back()
next_page = history.go_forward()
```

## Example Use Cases

### 1. Work Stealing Queue

```python
from redis_data_structures import Deque
from typing import Any, Optional
import random
import threading
from datetime import datetime

class WorkStealingQueue:
    def __init__(self, worker_id: str):
        self.deque = Deque(key=f"worker:{worker_id}:tasks")
        self.worker_id = worker_id
    
    def add_task(self, task: Any):
        """Add task to worker's queue."""
        self.deque.push_back({
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "worker": self.worker_id
        })
    
    def get_own_task(self) -> Optional[Any]:
        """Get task from own queue (LIFO)."""
        result = self.deque.pop_back()
        return result["task"] if result else None
    
    def steal_task(self, victim_id: str) -> Optional[Any]:
        """Steal task from another worker's queue (FIFO)."""
        result = self.deque.pop_front()
        return result["task"] if result else None
    
    def get_size(self) -> int:
        """Get number of tasks in queue."""
        return self.deque.size()

class WorkerThread(threading.Thread):
    def __init__(self, worker_id: str, other_workers: list[str]):
        super().__init__()
        self.queue = WorkStealingQueue(worker_id)
        self.other_workers = other_workers
        self.running = True
    
    def run(self):
        while self.running:
            # Try to get own task
            task = self.queue.get_own_task()
            if task:
                self.process_task(task)
                continue
            
            # If no tasks, try to steal
            victim_id = random.choice(self.other_workers)
            stolen_task = self.queue.steal_task(victim_id)
            if stolen_task:
                self.process_task(stolen_task)
                continue
            
            # No tasks found, sleep briefly
            time.sleep(0.1)
    
    def process_task(self, task: Any):
        """Process the task."""
        print(f"Worker {self.worker_id} processing task: {task}")

# Usage
workers = ["worker1", "worker2", "worker3"]
threads = [WorkerThread(w_id, [wid for wid in workers if wid != w_id]) 
          for w_id in workers]

# Start workers
for thread in threads:
    thread.start()

# Add tasks to workers
queue1 = WorkStealingQueue("worker1")
queue1.add_task("task1")
queue1.add_task("task2")
```

### 2. Undo/Redo System

```python
from redis_data_structures import Deque
from typing import Any, Callable, Optional
from dataclasses import dataclass

@dataclass
class Action:
    do: Callable[[], Any]
    undo: Callable[[], Any]
    description: str

class UndoRedoSystem:
    def __init__(self):
        self.undo_deque = Deque(key="undo_stack")
        self.redo_deque = Deque(key="redo_stack")
    
    def execute(self, action: Action):
        """Execute an action and add it to undo stack."""
        # Execute the action
        result = action.do()
        
        # Add to undo stack
        self.undo_deque.push_back({
            "description": action.description,
            "do": action.do.__name__,
            "undo": action.undo.__name__
        })
        
        # Clear redo stack since we've taken a new action
        self.redo_deque.clear()
        
        return result
    
    def undo(self) -> Optional[str]:
        """Undo last action."""
        action_data = self.undo_deque.pop_back()
        if not action_data:
            return None
        
        # Execute undo
        getattr(self, action_data["undo"])()
        
        # Add to redo stack
        self.redo_deque.push_back(action_data)
        return action_data["description"]
    
    def redo(self) -> Optional[str]:
        """Redo previously undone action."""
        action_data = self.redo_deque.pop_back()
        if not action_data:
            return None
        
        # Execute redo
        getattr(self, action_data["do"])()
        
        # Add back to undo stack
        self.undo_deque.push_back(action_data)
        return action_data["description"]
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self.undo_deque.size() > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self.redo_deque.size() > 0

# Usage
class TextEditor:
    def __init__(self):
        self.text = ""
        self.undo_redo = UndoRedoSystem()
    
    def insert_text(self, position: int, text: str):
        self.undo_redo.execute(Action(
            do=lambda: self._do_insert(position, text),
            undo=lambda: self._do_delete(position, len(text)),
            description=f"Insert '{text}' at position {position}"
        ))
    
    def delete_text(self, position: int, length: int):
        deleted_text = self.text[position:position+length]
        self.undo_redo.execute(Action(
            do=lambda: self._do_delete(position, length),
            undo=lambda: self._do_insert(position, deleted_text),
            description=f"Delete {length} characters at position {position}"
        ))
    
    def undo(self):
        return self.undo_redo.undo()
    
    def redo(self):
        return self.undo_redo.redo()
```

### 3. Message Buffer

```python
from redis_data_structures import Deque
from typing import Any, Optional
from datetime import datetime
import json

class MessageBuffer:
    def __init__(self, max_size: int = 1000):
        self.deque = Deque(key="message_buffer")
        self.max_size = max_size
    
    def add_message(self, message: Any):
        """Add message to buffer, removing oldest if full."""
        # Add new message
        msg_data = {
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        self.deque.push_back(msg_data)
        
        # Remove oldest if buffer is full
        while self.deque.size() > self.max_size:
            self.deque.pop_front()
    
    def get_latest_messages(self, count: int) -> list[dict]:
        """Get the most recent messages."""
        messages = []
        size = min(count, self.deque.size())
        
        # Temporarily store messages while we retrieve them
        temp_key = f"temp_buffer_{datetime.now().timestamp()}"
        
        for _ in range(size):
            msg = self.deque.pop_back()
            if msg:
                messages.append(msg)
                self.deque.push_front(temp_key, msg)
        
        # Restore messages
        for _ in range(len(messages)):
            msg = self.deque.pop_front(temp_key)
            if msg:
                self.deque.push_back(msg)
        
        return messages
    
    def clear_old_messages(self, before_timestamp: datetime):
        """Remove messages older than specified timestamp."""
        temp_key = f"temp_buffer_{datetime.now().timestamp()}"
        
        while True:
            msg = self.deque.pop_front()
            if not msg:
                break
                
            msg_time = datetime.fromisoformat(msg["timestamp"])
            if msg_time >= before_timestamp:
                self.deque.push_back(temp_key, msg)
        
        # Restore remaining messages
        while True:
            msg = self.deque.pop_back(temp_key)
            if not msg:
                break
            self.deque.push_front(msg)

# Usage
buffer = MessageBuffer(max_size=100)

# Add messages
buffer.add_message("Hello")
buffer.add_message("World")

# Get recent messages
latest = buffer.get_latest_messages(10)

# Clear old messages
buffer.clear_old_messages(datetime.now())
```