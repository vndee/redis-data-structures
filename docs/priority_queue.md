# Priority Queue

A priority queue implementation backed by Redis where elements are processed based on their priority level (lower number = higher priority). Perfect for task scheduling, resource allocation, and event prioritization.

## Features

- Priority-based ordering
- Thread-safe operations
- Persistent storage with Redis
- JSON serialization for complex data types
- Atomic operations
- Size tracking

## Operations

| Operation | Time Complexity | Description |
|-----------|----------------|-------------|
| `push`    | O(log N)      | Add an item with a priority |
| `pop`     | O(log N)      | Remove and return the highest priority item |
| `size`    | O(1)          | Get the current size of the queue |
| `clear`   | O(1)          | Remove all items from the queue |

## Basic Usage

```python
from redis_data_structures import PriorityQueue

# Initialize priority queue
pq = PriorityQueue(
    host='localhost',
    port=6379,
    db=0,
    username=None,  # Optional
    password=None   # Optional
)

# Basic operations
pq.push('my_queue', 'high_priority_item', priority=1)
pq.push('my_queue', 'low_priority_item', priority=5)
item, priority = pq.pop('my_queue')  # Returns ('high_priority_item', 1)
size = pq.size('my_queue')
pq.clear('my_queue')
```

## Example Use Cases

### 1. Hospital Emergency Room Triage

Perfect for managing patient priority in emergency situations.

```python
class ERSystem:
    def __init__(self):
        self.patients = PriorityQueue(host='localhost', port=6379)
        self.er_key = 'hospital:er'
        
        # Priority levels:
        self.PRIORITIES = {
            'critical': 1,    # Immediate life-threatening
            'emergency': 2,   # Severe but not immediately life-threatening
            'urgent': 3,      # Serious but not severe
            'semi_urgent': 4, # Minor injuries
            'non_urgent': 5   # Non-emergency cases
        }
    
    def add_patient(self, patient_info: dict, condition: str):
        """Add a patient to the ER queue."""
        priority = self.PRIORITIES.get(condition, 5)
        
        patient = {
            'id': str(uuid.uuid4()),
            'info': patient_info,
            'condition': condition,
            'arrival_time': time.time()
        }
        
        self.patients.push(self.er_key, patient, priority)
        return patient['id']
    
    def get_next_patient(self) -> Optional[tuple]:
        """Get the next highest priority patient."""
        result = self.patients.pop(self.er_key)
        if result:
            patient, priority = result
            return patient, self.PRIORITIES[patient['condition']]
        return None
    
    def get_waiting_count(self) -> int:
        """Get number of waiting patients."""
        return self.patients.size(self.er_key)

# Usage
er = ERSystem()
er.add_patient(
    {'name': 'John Doe', 'age': 45},
    'critical'
)
er.add_patient(
    {'name': 'Jane Smith', 'age': 30},
    'semi_urgent'
)
next_patient, priority = er.get_next_patient()  # Returns John Doe first
```

### 2. Task Scheduler

Ideal for scheduling tasks with different priority levels.

```python
class TaskScheduler:
    def __init__(self):
        self.tasks = PriorityQueue(host='localhost', port=6379)
        self.scheduler_key = 'scheduler:tasks'
    
    def schedule_task(self, task: dict, priority: int = 3):
        """Schedule a task with priority (1-5)."""
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 and 5")
        
        task_info = {
            'id': str(uuid.uuid4()),
            'task': task,
            'scheduled_at': time.time(),
            'priority': priority
        }
        
        self.tasks.push(self.scheduler_key, task_info, priority)
        return task_info['id']
    
    def process_tasks(self, worker_id: str):
        """Process tasks in priority order."""
        while True:
            result = self.tasks.pop(self.scheduler_key)
            if not result:
                time.sleep(1)
                continue
            
            task, priority = result
            try:
                print(f"Worker {worker_id} processing task {task['id']} "
                      f"with priority {priority}")
                self._execute_task(task['task'])
            except Exception as e:
                print(f"Error processing task {task['id']}: {e}")
    
    def _execute_task(self, task: dict):
        # Task execution logic
        pass

# Usage
scheduler = TaskScheduler()
scheduler.schedule_task(
    {'action': 'send_email', 'to': 'user@example.com'},
    priority=2
)
scheduler.schedule_task(
    {'action': 'cleanup_files', 'path': '/tmp'},
    priority=4
)
```

### 3. Network Packet Processing

Great for handling network packets with different QoS (Quality of Service) levels.

```python
class PacketProcessor:
    def __init__(self):
        self.packets = PriorityQueue(host='localhost', port=6379)
        self.network_key = 'network:packets'
        
        # QoS levels
        self.QOS_LEVELS = {
            'voice': 1,      # Real-time voice/video
            'interactive': 2, # Interactive data
            'streaming': 3,   # Streaming media
            'background': 4   # Background traffic
        }
    
    def enqueue_packet(self, packet: dict, qos_level: str):
        """Add a packet to the processing queue."""
        priority = self.QOS_LEVELS.get(qos_level, 4)
        
        packet_info = {
            'id': str(uuid.uuid4()),
            'data': packet,
            'qos': qos_level,
            'timestamp': time.time()
        }
        
        self.packets.push(self.network_key, packet_info, priority)
        return packet_info['id']
    
    def process_packets(self):
        """Process packets based on QoS priority."""
        while True:
            result = self.packets.pop(self.network_key)
            if not result:
                time.sleep(0.001)  # Small delay if no packets
                continue
            
            packet, priority = result
            try:
                self._process_packet(packet, priority)
            except Exception as e:
                print(f"Error processing packet {packet['id']}: {e}")
    
    def _process_packet(self, packet: dict, priority: int):
        # Packet processing logic
        pass

# Usage
processor = PacketProcessor()
processor.enqueue_packet(
    {'source': '192.168.1.1', 'dest': '192.168.1.2', 'data': b'...'},
    'voice'
)
processor.enqueue_packet(
    {'source': '192.168.1.3', 'dest': '192.168.1.4', 'data': b'...'},
    'background'
)
```

## Best Practices

1. **Priority Management**
   - Use consistent priority levels across the application
   - Document priority meanings
   - Consider using enums or constants for priorities
   ```python
   from enum import IntEnum
   
   class Priority(IntEnum):
       CRITICAL = 1
       HIGH = 2
       MEDIUM = 3
       LOW = 4
       BACKGROUND = 5
   ```

2. **Error Handling**
   ```python
   try:
       pq.push('my_queue', item, priority)
   except redis.RedisError as e:
       logger.error(f"Redis error: {e}")
       # Handle error...
   except ValueError as e:
       logger.error(f"Invalid priority: {e}")
       # Handle error...
   ```

3. **Memory Management**
   - Monitor queue size
   - Implement size limits if needed
   ```python
   if pq.size('my_queue') > MAX_SIZE:
       # Handle queue full condition
       pass
   ```

4. **Performance**
   - Batch similar priority items when possible
   - Use appropriate priority ranges (typically 1-5 or 1-10)
   - Consider priority aging to prevent starvation

## Common Patterns

### 1. Priority Aging
```python
class AgingPriorityQueue:
    def __init__(self):
        self.queue = PriorityQueue(host='localhost', port=6379)
        self.key = 'aging:queue'
        self.age_interval = 300  # 5 minutes
    
    def push(self, item: dict, priority: int):
        item['timestamp'] = time.time()
        self.queue.push(self.key, item, priority)
    
    def pop(self) -> Optional[tuple]:
        result = self.queue.pop(self.key)
        if not result:
            return None
        
        item, priority = result
        age = (time.time() - item['timestamp']) / self.age_interval
        aged_priority = max(1, priority - int(age))
        
        if aged_priority < priority:
            # Re-insert with updated priority
            self.push(item, aged_priority)
            return self.pop()
        
        return item, priority
```

### 2. Multi-level Priority
```python
class MultiLevelQueue:
    def __init__(self):
        self.queues = {
            'high': PriorityQueue(host='localhost', port=6379),
            'medium': PriorityQueue(host='localhost', port=6379),
            'low': PriorityQueue(host='localhost', port=6379)
        }
    
    def push(self, level: str, item: dict, priority: int):
        if level not in self.queues:
            raise ValueError(f"Invalid queue level: {level}")
        self.queues[level].push(f'mlq:{level}', item, priority)
    
    def pop(self) -> Optional[tuple]:
        # Try high priority queue first
        for level in ['high', 'medium', 'low']:
            result = self.queues[level].pop(f'mlq:{level}')
            if result:
                return result
        return None
```

### 3. Priority Batching
```python
def batch_process_priority(pq: PriorityQueue, batch_size: int = 10):
    """Process items of the same priority in batches."""
    current_batch = []
    current_priority = None
    
    while len(current_batch) < batch_size:
        result = pq.pop('batch:queue')
        if not result:
            break
        
        item, priority = result
        if current_priority is None:
            current_priority = priority
        
        if priority != current_priority:
            # Re-insert item with different priority
            pq.push('batch:queue', item, priority)
            break
        
        current_batch.append(item)
    
    return current_batch, current_priority
```

## Limitations

1. **No Direct Access**
   - Cannot access items by index
   - Must pop items to access them

2. **Priority Collisions**
   - Items with same priority are not guaranteed order
   - Need additional timestamp if strict FIFO within priority is needed

3. **No Priority Updates**
   - Cannot change priority of existing items
   - Must remove and re-add with new priority

## Performance Considerations

1. **Time Complexity**
   - Push and Pop are O(log N)
   - Consider batching for better throughput

2. **Memory Usage**
   - Each item requires priority storage
   - Consider cleanup strategies for processed items

3. **Concurrency**
   - Operations are atomic
   - Safe for multi-producer/consumer scenarios

## Troubleshooting

1. **Priority Inversion**
   - Check priority assignments
   - Implement priority aging if needed
   - Monitor processing times

2. **Memory Issues**
   - Monitor queue size
   - Implement size limits
   - Regular cleanup of processed items

3. **Performance Issues**
   - Use appropriate priority ranges
   - Batch similar priority items
   - Monitor Redis sorted set performance
