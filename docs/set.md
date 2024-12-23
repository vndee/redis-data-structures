# Set

A Redis-backed Set implementation that maintains a collection of unique elements. Perfect for managing unique items, tracking membership, and implementing relationships between entities.

## Features

- Unique element guarantee
- Thread-safe operations
- Persistent storage with Redis
- JSON serialization for complex data types
- Atomic operations
- Size tracking
- Set operations (union, intersection, difference)

## Operations

| Operation    | Time Complexity | Description |
|-------------|----------------|-------------|
| `add`       | O(1)          | Add an item to the set |
| `remove`    | O(1)          | Remove an item from the set |
| `contains`  | O(1)          | Check if an item exists in the set |
| `members`   | O(N)          | Get all items in the set |
| `size`      | O(1)          | Get the current size of the set |
| `clear`     | O(1)          | Remove all items from the set |

## Basic Usage

```python
from redis_data_structures import Set

# Initialize set
set_ds = Set(
    host='localhost',
    port=6379,
    db=0,
    username=None,  # Optional
    password=None   # Optional
)

# Basic operations
set_ds.add('my_set', 'item1')
set_ds.add('my_set', 'item2')
set_ds.add('my_set', 'item1')  # Won't add duplicate
exists = set_ds.contains('my_set', 'item1')  # Returns True
members = set_ds.members('my_set')  # Returns {'item1', 'item2'}
size = set_ds.size('my_set')
set_ds.remove('my_set', 'item1')
set_ds.clear('my_set')
```

## Example Use Cases

### 1. User Session Management

Perfect for tracking active user sessions and managing authentication.

```python
class SessionManager:
    def __init__(self):
        self.sessions = Set(host='localhost', port=6379)
        self.session_key = 'sessions:active'
    
    def create_session(self, user_id: str) -> str:
        """Create a new session for a user."""
        session_id = str(uuid.uuid4())
        session = {
            'id': session_id,
            'user_id': user_id,
            'created_at': time.time(),
            'last_active': time.time()
        }
        
        self.sessions.add(self.session_key, json.dumps(session))
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """Check if a session is valid."""
        return self.sessions.contains(self.session_key, session_id)
    
    def end_session(self, session_id: str):
        """End a user session."""
        self.sessions.remove(self.session_key, session_id)
    
    def get_active_sessions(self) -> list:
        """Get all active sessions."""
        return [json.loads(s) for s in self.sessions.members(self.session_key)]
    
    def cleanup_expired_sessions(self, max_age: int = 3600):
        """Remove expired sessions."""
        current_time = time.time()
        for session in self.get_active_sessions():
            if current_time - session['last_active'] > max_age:
                self.end_session(session['id'])

# Usage
session_mgr = SessionManager()
session_id = session_mgr.create_session('user123')
is_valid = session_mgr.validate_session(session_id)
session_mgr.end_session(session_id)
```

### 2. Tag Management System

Ideal for managing tags and categories for items.

```python
class TagSystem:
    def __init__(self):
        self.tags = Set(host='localhost', port=6379)
    
    def add_tags(self, item_id: str, tags: list[str]):
        """Add tags to an item."""
        key = f'tags:{item_id}'
        for tag in tags:
            self.tags.add(key, tag.lower())
    
    def remove_tag(self, item_id: str, tag: str):
        """Remove a tag from an item."""
        self.tags.remove(f'tags:{item_id}', tag.lower())
    
    def get_item_tags(self, item_id: str) -> set:
        """Get all tags for an item."""
        return self.tags.members(f'tags:{item_id}')
    
    def has_tag(self, item_id: str, tag: str) -> bool:
        """Check if an item has a specific tag."""
        return self.tags.contains(f'tags:{item_id}', tag.lower())
    
    def clear_tags(self, item_id: str):
        """Remove all tags from an item."""
        self.tags.clear(f'tags:{item_id}')

# Usage
tag_system = TagSystem()
tag_system.add_tags('post123', ['python', 'redis', 'database'])
tags = tag_system.get_item_tags('post123')
has_python = tag_system.has_tag('post123', 'python')
```

### 3. Unique Visitor Tracking

Great for tracking unique visitors or events.

```python
class VisitorTracker:
    def __init__(self):
        self.visitors = Set(host='localhost', port=6379)
        self.ttl = 86400  # 24 hours in seconds
    
    def track_visitor(self, page_id: str, visitor_id: str):
        """Track a unique visitor for a page."""
        key = f'visitors:{page_id}:{self._get_date_key()}'
        self.visitors.add(key, visitor_id)
        # Implement TTL in actual Redis client
    
    def get_unique_visitors(self, page_id: str) -> set:
        """Get unique visitors for today."""
        key = f'visitors:{page_id}:{self._get_date_key()}'
        return self.visitors.members(key)
    
    def get_visitor_count(self, page_id: str) -> int:
        """Get count of unique visitors."""
        key = f'visitors:{page_id}:{self._get_date_key()}'
        return self.visitors.size(key)
    
    def _get_date_key(self) -> str:
        """Get current date key."""
        return datetime.now().strftime('%Y-%m-%d')

# Usage
tracker = VisitorTracker()
tracker.track_visitor('homepage', 'user123')
count = tracker.get_visitor_count('homepage')
visitors = tracker.get_unique_visitors('homepage')
```

## Best Practices

1. **Key Management**
   - Use descriptive key names: `set:users`, `set:tags`, etc.
   - Consider implementing key expiration for temporary sets
   - Clear sets that are no longer needed

2. **Error Handling**
   ```python
   try:
       set_ds.add('my_set', item)
   except redis.RedisError as e:
       logger.error(f"Redis error: {e}")
       # Handle error...
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
       # Handle error...
   ```

3. **Memory Management**
   - Monitor set size for large collections
   - Implement size limits if needed
   ```python
   if set_ds.size('my_set') > MAX_SIZE:
       # Handle set size limit...
       pass
   ```

4. **Performance**
   - Use batch operations when possible
   - Consider partitioning large sets
   - Implement cleanup strategies

## Common Patterns

### 1. Set Operations
```python
class SetOperations:
    def __init__(self):
        self.set_ds = Set(host='localhost', port=6379)
    
    def get_common_items(self, set1: str, set2: str) -> set:
        """Get items present in both sets."""
        items1 = self.set_ds.members(set1)
        items2 = self.set_ds.members(set2)
        return items1.intersection(items2)
    
    def get_unique_items(self, set1: str, set2: str) -> set:
        """Get items present in set1 but not in set2."""
        items1 = self.set_ds.members(set1)
        items2 = self.set_ds.members(set2)
        return items1.difference(items2)
    
    def get_all_items(self, set1: str, set2: str) -> set:
        """Get all unique items from both sets."""
        items1 = self.set_ds.members(set1)
        items2 = self.set_ds.members(set2)
        return items1.union(items2)
```

### 2. Time-Based Sets
```python
class TimeBasedSet:
    def __init__(self):
        self.set_ds = Set(host='localhost', port=6379)
    
    def add_item(self, key: str, item: Any):
        """Add item with timestamp."""
        self.set_ds.add(key, {
            'item': item,
            'timestamp': time.time()
        })
    
    def get_recent_items(self, key: str, max_age: int) -> list:
        """Get items newer than max_age seconds."""
        current_time = time.time()
        return [
            item['item'] for item in self.set_ds.members(key)
            if current_time - item['timestamp'] <= max_age
        ]
```

### 3. Hierarchical Sets
```python
class HierarchicalSet:
    def __init__(self):
        self.set_ds = Set(host='localhost', port=6379)
    
    def add_child(self, parent_id: str, child_id: str):
        """Add a child to a parent."""
        self.set_ds.add(f'children:{parent_id}', child_id)
        self.set_ds.add(f'parents:{child_id}', parent_id)
    
    def get_children(self, parent_id: str) -> set:
        """Get all children of a parent."""
        return self.set_ds.members(f'children:{parent_id}')
    
    def get_parents(self, child_id: str) -> set:
        """Get all parents of a child."""
        return self.set_ds.members(f'parents:{child_id}')
```

## Limitations

1. **No Ordering**
   - Elements are not stored in any particular order
   - Cannot retrieve elements by position

2. **Memory Usage**
   - Each element consumes memory
   - Large sets can impact Redis memory usage

3. **No Duplicates**
   - Cannot store duplicate elements
   - Must use other data structures if duplicates needed

## Performance Considerations

1. **Time Complexity**
   - Most operations are O(1)
   - Member retrieval is O(N)

2. **Memory Usage**
   - Each element adds to Redis memory
   - Consider cleanup strategies for old data

3. **Concurrency**
   - Operations are atomic
   - Safe for multi-threaded use

## Troubleshooting

1. **Missing Elements**
   - Check if elements were properly added
   - Verify key names
   - Check for accidental removals

2. **Memory Issues**
   - Monitor set sizes
   - Implement size limits
   - Regular cleanup of unused sets

3. **Performance Issues**
   - Avoid frequent full set retrieval
   - Use appropriate data structures
   - Monitor Redis performance
