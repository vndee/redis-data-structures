# Priority Queue

A Redis-backed priority queue implementation that maintains elements in sorted order by priority. Perfect for task scheduling, job queues, and any application requiring prioritized processing.

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | :---: | :---: | --- | --- |
| `push` | $O(\log n)$ | $O(\log n)$ | Add an item with a priority | `ZADD` |
| `pop` | $O(\log n)$ | $O(\log n)$ | Remove and return the highest priority item | `ZRANGE`, `ZREM` |
| `peek` | $O(1)$ | $O(1)$ | Return the highest priority item without removing it | `ZRANGE` |
| `size` | $O(1)$ | $O(1)$ | Return the number of items in the queue | `ZCARD` |
| `clear` | $O(1)$ | $O(1)$ | Remove all items from the queue | `DELETE` |
| `get_all` | $O(n)$ | $O(n)$ | Get all items in priority order | `ZRANGE` |

where:
- $n$ is the number of items in the queue

## Basic Usage

```python
from redis_data_structures import PriorityQueue

# Initialize priority queue
pq = PriorityQueue("tasks")

# Add items with priorities (lower number = higher priority)
pq.push("critical_task", priority=1)
pq.push("normal_task", priority=2)
pq.push("low_priority_task", priority=3)

# Get highest priority item
task, priority = pq.pop()  # Returns ("critical_task", 1)

# Check size
size = pq.size()  # Returns 2

# Peek at highest priority item without removing
next_task, next_priority = pq.peek()  # Returns ("normal_task", 2)

# Clear the queue
pq.clear()
```

## Advanced Usage

```python
from redis_data_structures import PriorityQueue
from enum import IntEnum

# Define priority levels
class Priority(IntEnum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

# Initialize priority queue
pq = PriorityQueue("tasks")

# Store complex data types with priorities
task = {
    "type": "security_patch",
    "action": "deploy",
    "data": {
        "server": "prod-1",
        "patch_id": "CVE-2024-001"
    }
}
pq.push(task, priority=Priority.CRITICAL)

# Process tasks by priority with error handling
while pq.size() > 0:
    result = pq.pop()
    if result:
        task, priority = result
        print(f"Processing: {task['type']} (Priority: {Priority(priority).name})")
    else:
        print("Error retrieving task")

# Get all tasks in priority order
all_tasks = pq.get_all()
for task, priority in all_tasks:
    print(f"Task: {task}, Priority: {Priority(priority).name}")
```

## Example Use Cases

### 1. Time-based Task Scheduler

```python
from redis_data_structures import PriorityQueue
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time

class TimeBasedScheduler:
    def __init__(self):
        self.pq = PriorityQueue("scheduled_tasks")
    
    def schedule_task(self, task_type: str, data: Dict[str, Any], execute_at: datetime):
        """Schedule a task for execution at a specific time."""
        task = {
            "type": task_type,
            "data": data,
            "scheduled_for": execute_at.isoformat()
        }
        # Use timestamp as priority (earlier time = higher priority)
        priority = execute_at.timestamp()
        return self.pq.push(task, priority=priority)
    
    def schedule_recurring(self, task_type: str, data: Dict[str, Any], 
                         interval: timedelta, start_time: Optional[datetime] = None):
        """Schedule a recurring task with a fixed interval."""
        if start_time is None:
            start_time = datetime.now()
        
        # Schedule the first occurrence
        self.schedule_task(task_type, data, start_time)
        
        # Schedule the next occurrence
        next_time = start_time + interval
        task = {
            "type": task_type,
            "data": data,
            "interval": interval.total_seconds(),
            "is_recurring": True
        }
        return self.pq.push(task, priority=next_time.timestamp())
    
    def get_due_task(self) -> Optional[tuple[Dict[str, Any], float]]:
        """Get task if it's due for execution."""
        result = self.pq.peek()
        if not result:
            return None
        
        task, priority = result
        now = datetime.now().timestamp()
        
        # Check if task is due
        if priority <= now:
            # Remove and return the task
            return self.pq.pop()
        return None
    
    def process_tasks(self, stop_time: Optional[datetime] = None):
        """Process tasks until stop_time (if specified)."""
        while True:
            if stop_time and datetime.now() >= stop_time:
                break
                
            result = self.get_due_task()
            if not result:
                time.sleep(1)  # Wait if no tasks are due
                continue
                
            task, priority = result
            print(f"Executing task: {task['type']} (Scheduled for: {task['scheduled_for']})")
            
            # Reschedule if it's a recurring task
            if task.get('is_recurring'):
                next_time = datetime.fromtimestamp(priority) + \
                           timedelta(seconds=task['interval'])
                self.schedule_task(task['type'], task['data'], next_time)

# Usage
scheduler = TimeBasedScheduler()

# Schedule one-time task
scheduler.schedule_task(
    "backup",
    {"database": "users", "type": "full"},
    datetime.now() + timedelta(minutes=5)
)

# Schedule recurring task (every hour)
scheduler.schedule_recurring(
    "health_check",
    {"service": "api", "endpoint": "/health"},
    interval=timedelta(hours=1)
)

# Schedule daily report at specific time
tomorrow_9am = datetime.now().replace(hour=9, minute=0) + timedelta(days=1)
scheduler.schedule_task(
    "generate_report",
    {"report_type": "daily_metrics"},
    execute_at=tomorrow_9am
)

# Process tasks for the next hour
scheduler.process_tasks(stop_time=datetime.now() + timedelta(hours=1))
```

### 2. Priority Task Scheduler

```python
from redis_data_structures import PriorityQueue
from enum import IntEnum
from typing import Dict, Any

class TaskPriority(IntEnum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class TaskScheduler:
    def __init__(self):
        self.pq = PriorityQueue("scheduled_tasks")
    
    def add_task(self, task_type: str, data: Dict[str, Any], priority: TaskPriority):
        """Add a task with priority."""
        task = {
            "type": task_type,
            "data": data
        }
        return self.pq.push(task, priority=priority)
    
    def get_next_task(self) -> tuple[Dict[str, Any], int]:
        """Get highest priority task."""
        return self.pq.pop()
    
    def peek_next_task(self) -> tuple[Dict[str, Any], int]:
        """Preview next task without removing."""
        return self.pq.peek()
    
    def get_all_tasks(self) -> list[tuple[Dict[str, Any], int]]:
        """Get all tasks in priority order."""
        return self.pq.get_all()

# Usage
scheduler = TaskScheduler()
scheduler.add_task(
    "security_update",
    {"server": "prod-1", "patch": "security-001"},
    TaskPriority.CRITICAL
)
scheduler.add_task(
    "backup",
    {"database": "users", "type": "full"},
    TaskPriority.HIGH
)
next_task, priority = scheduler.get_next_task()  # Returns security_update task first
```

### 3. Service Request Handler

```python
from redis_data_structures import PriorityQueue
from enum import IntEnum
from typing import Dict, Any

class RequestPriority(IntEnum):
    PREMIUM = 1
    STANDARD = 2
    FREE = 3

class ServiceRequestHandler:
    def __init__(self):
        self.pq = PriorityQueue("service_requests")
    
    def add_request(self, user_id: str, request_type: str, data: Dict[str, Any], user_tier: str):
        """Add a service request with priority based on user tier."""
        request = {
            "user_id": user_id,
            "type": request_type,
            "data": data
        }
        priority = RequestPriority[user_tier.upper()]
        return self.pq.push(request, priority=priority)
    
    def process_next_request(self) -> tuple[Dict[str, Any], int]:
        """Process highest priority request."""
        return self.pq.pop()
    
    def get_pending_requests(self) -> list[tuple[Dict[str, Any], int]]:
        """Get all pending requests in priority order."""
        return self.pq.get_all()

# Usage
handler = ServiceRequestHandler()
handler.add_request(
    "user123",
    "support",
    {"issue": "login_failed"},
    "premium"
)
handler.add_request(
    "user456",
    "feature_request",
    {"feature": "dark_mode"},
    "standard"
)
request, priority = handler.process_next_request()  # Premium request processed first
```

### 4. Task Prioritization with Producer-Consumer Pattern

```python
import time
import argparse
from redis_data_structures import PriorityQueue
from typing import Dict, Any

class TaskProducer:
    def __init__(self, queue: PriorityQueue):
        self.queue = queue

    def produce(self, task_type: str, data: Any, priority: int):
        """Produce a new task and add it to the priority queue."""
        task = {
            "type": task_type,
            "data": data
        }
        self.queue.push(task, priority=priority)
        print(f"Produced task: {task} with priority {priority}")

class TaskConsumer:
    def __init__(self, queue: PriorityQueue):
        self.queue = queue

    def consume(self):
        """Consume tasks from the priority queue."""
        print("Consuming tasks...")
        while True:
            task = self.queue.pop()
            if task:
                data, priority = task
                print(f"Consumed task: {data['type']} with priority {priority}")
            
            time.sleep(0.25)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Priority Queue Producer-Consumer Example")
    parser.add_argument("--producer", action="store_true", help="Run the producer")
    parser.add_argument("--consumer", action="store_true", help="Run the consumer")
    args = parser.parse_args()

    if not args.producer and not args.consumer:
        print("Please specify either --producer or --consumer")
        parser.print_help()
        exit(1)

    pq = PriorityQueue("task_queue")

    if args.producer:
        # Create producer and consumer
        producer = TaskProducer(pq)
        
        # Produce some tasks
        producer.produce("task1", {"info": "data1"}, priority=2)
        producer.produce("task2", {"info": "data2"}, priority=1)
        producer.produce("task3", {"info": "data3"}, priority=3)

    if args.consumer:
        consumer = TaskConsumer(pq)
        consumer.consume()
```