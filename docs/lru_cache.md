# LRU Cache (Least Recently Used)

A Redis-backed LRU (Least Recently Used) cache implementation that maintains a fixed-size cache and automatically evicts the least recently used items when capacity is reached. Perfect for caching database queries, expensive computations, session data, and frequently accessed resources.

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | --- | --- | --- | --- |
| `put` | $O(1)$ | $O(1)$ | Add or update an item | `LPUSH`, `HSET` |
| `get` | $O(1)$ | $O(1)$ | Get an item and update access time | `HGET`, `LPUSH` |
| `peek` | $O(1)$ | $O(1)$ | Get item without updating access time | `HGET` |
| `remove` | $O(1)$ | $O(1)$ | Remove an item | `HDEL`, `LREM` |
| `get_all` | $O(n)$ | $O(n)$ | Get all items | `HGETALL` |
| `size` | $O(1)$ | $O(1)$ | Get number of items | `HLEN` |
| `clear` | $O(1)$ | $O(1)$ | Remove all items | `DELETE` |
| `get_lru_order` | $O(n)$ | $O(n)$ | Get items in LRU order | `LRANGE` |

where:
- n is the number of items in the cache

## Basic Usage

```python
from redis_data_structures import LRUCache

# Initialize cache with capacity
cache = LRUCache(capacity=1000)
cache_key = "my_cache"

# Add items
cache.put(cache_key, "user:1", {"name": "John", "age": 30})
cache.put(cache_key, "user:2", {"name": "Jane", "age": 25})

# Get items (updates access time)
user = cache.get(cache_key, "user:1")

# Peek at items (doesn't update access time)
user = cache.peek(cache_key, "user:1")

# Get all items
all_items = cache.get_all(cache_key)

# Get LRU order
lru_order = cache.get_lru_order(cache_key)  # Least to most recently used

# Remove items
cache.remove(cache_key, "user:1")

# Clear cache
cache.clear(cache_key)
```

## Advanced Usage

```python
from redis_data_structures import LRUCache
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class QueryCache:
    def __init__(self, capacity: int = 1000):
        self.cache = LRUCache(capacity=capacity)
        self.queries_key = "db_queries"
    
    def get_result(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached query result."""
        result = self.cache.get(self.queries_key, query)
        if result:
            # Check if result is still valid
            if datetime.fromisoformat(result["cached_at"]) + \
               timedelta(seconds=result["ttl"]) > datetime.now():
                return result["data"]
            # Result expired, remove it
            self.cache.remove(self.queries_key, query)
        return None
    
    def cache_result(
        self, 
        query: str, 
        data: Dict[str, Any], 
        ttl: int = 3600
    ) -> bool:
        """Cache a query result with TTL."""
        cache_data = {
            "data": data,
            "cached_at": datetime.now().isoformat(),
            "ttl": ttl
        }
        return self.cache.put(self.queries_key, query, cache_data)
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries."""
        if pattern:
            # Get all entries and remove matching ones
            entries = self.cache.get_all(self.queries_key)
            for query in entries:
                if pattern in query:
                    self.cache.remove(self.queries_key, query)
        else:
            # Clear entire cache
            self.cache.clear(self.queries_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        entries = self.cache.get_all(self.queries_key)
        current_time = datetime.now()
        
        stats = {
            "total_entries": len(entries),
            "expired_entries": 0,
            "active_entries": 0,
            "avg_age": timedelta(0)
        }
        
        ages = []
        for _, result in entries.items():
            cached_at = datetime.fromisoformat(result["cached_at"])
            age = current_time - cached_at
            is_expired = age > timedelta(seconds=result["ttl"])
            
            if is_expired:
                stats["expired_entries"] += 1
            else:
                stats["active_entries"] += 1
                ages.append(age)
        
        if ages:
            stats["avg_age"] = sum(ages, timedelta(0)) / len(ages)
        
        return stats

# Usage
query_cache = QueryCache(capacity=1000)

# Cache query result
query_cache.cache_result(
    "SELECT * FROM users WHERE id = 1",
    {"id": 1, "name": "John"},
    ttl=3600
)

# Get cached result
result = query_cache.get_result("SELECT * FROM users WHERE id = 1")

# Get cache stats
stats = query_cache.get_stats()
```

## Example Use Cases

### 1. User Session Cache

```python
from redis_data_structures import LRUCache
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

class SessionCache:
    def __init__(self, max_sessions: int = 10000):
        self.cache = LRUCache(capacity=max_sessions)
        self.sessions_key = "user_sessions"
    
    def create_session(
        self, 
        user_id: str, 
        data: Dict[str, Any], 
        ttl: int = 3600
    ) -> str:
        """Create a new session."""
        import secrets
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            "user_id": user_id,
            "data": data,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "ttl": ttl
        }
        
        if self.cache.put(self.sessions_key, session_id, session_data):
            return session_id
        return ""
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get and validate session."""
        session = self.cache.peek(self.sessions_key, session_id)
        if not session:
            return None
            
        # Check if session is expired
        last_accessed = datetime.fromisoformat(session["last_accessed"])
        if last_accessed + timedelta(seconds=session["ttl"]) < datetime.now():
            self.cache.remove(self.sessions_key, session_id)
            return None
            
        # Update last accessed time
        session["last_accessed"] = datetime.now().isoformat()
        self.cache.put(self.sessions_key, session_id, session)
        
        return session["data"]
    
    def update_session(
        self, 
        session_id: str, 
        data: Dict[str, Any]
    ) -> bool:
        """Update session data."""
        session = self.cache.peek(self.sessions_key, session_id)
        if not session:
            return False
            
        session["data"] = data
        session["last_accessed"] = datetime.now().isoformat()
        return self.cache.put(self.sessions_key, session_id, session)
    
    def end_session(self, session_id: str) -> bool:
        """End a session."""
        return self.cache.remove(self.sessions_key, session_id)
    
    def cleanup_expired(self) -> int:
        """Clean up expired sessions."""
        sessions = self.cache.get_all(self.sessions_key)
        removed = 0
        
        for session_id, session in sessions.items():
            last_accessed = datetime.fromisoformat(session["last_accessed"])
            if last_accessed + timedelta(seconds=session["ttl"]) < datetime.now():
                if self.cache.remove(self.sessions_key, session_id):
                    removed += 1
                    
        return removed

# Usage
session_cache = SessionCache(max_sessions=10000)

# Create session
session_id = session_cache.create_session(
    "user123",
    {"name": "John", "role": "admin"},
    ttl=3600
)

# Get session
session = session_cache.get_session(session_id)

# Update session
session_cache.update_session(
    session_id,
    {"name": "John", "role": "admin", "theme": "dark"}
)

# Clean up
expired = session_cache.cleanup_expired()
```

### 2. API Response Cache

```python
from redis_data_structures import LRUCache
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import json
import hashlib

class APICache:
    def __init__(self, capacity: int = 10000):
        self.cache = LRUCache(capacity=capacity)
        self.responses_key = "api_responses"
    
    def _generate_cache_key(
        self, 
        endpoint: str, 
        params: Dict[str, Any]
    ) -> str:
        """Generate a unique cache key."""
        key_data = {
            "endpoint": endpoint,
            "params": sorted(params.items())
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def get_response(
        self, 
        endpoint: str, 
        params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get cached API response."""
        cache_key = self._generate_cache_key(endpoint, params)
        cached = self.cache.peek(self.responses_key, cache_key)
        
        if not cached:
            return None
            
        # Check if response is still valid
        cached_at = datetime.fromisoformat(cached["cached_at"])
        if cached_at + timedelta(seconds=cached["ttl"]) < datetime.now():
            self.cache.remove(self.responses_key, cache_key)
            return None
            
        return cached["response"]
    
    def cache_response(
        self,
        endpoint: str,
        params: Dict[str, Any],
        response: Dict[str, Any],
        ttl: int = 300  # 5 minutes default TTL
    ) -> bool:
        """Cache an API response."""
        cache_key = self._generate_cache_key(endpoint, params)
        cache_data = {
            "response": response,
            "cached_at": datetime.now().isoformat(),
            "ttl": ttl,
            "endpoint": endpoint,
            "params": params
        }
        return self.cache.put(self.responses_key, cache_key, cache_data)
    
    def invalidate_endpoint(self, endpoint: str):
        """Invalidate all cached responses for an endpoint."""
        all_cached = self.cache.get_all(self.responses_key)
        for cache_key, cached in all_cached.items():
            if cached["endpoint"] == endpoint:
                self.cache.remove(self.responses_key, cache_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        all_cached = self.cache.get_all(self.responses_key)
        stats = {
            "total_cached": len(all_cached),
            "by_endpoint": {},
            "expired": 0,
            "active": 0
        }
        
        now = datetime.now()
        for cached in all_cached.values():
            endpoint = cached["endpoint"]
            stats["by_endpoint"][endpoint] = \
                stats["by_endpoint"].get(endpoint, 0) + 1
                
            cached_at = datetime.fromisoformat(cached["cached_at"])
            if cached_at + timedelta(seconds=cached["ttl"]) < now:
                stats["expired"] += 1
            else:
                stats["active"] += 1
        
        return stats

# Usage
api_cache = APICache(capacity=10000)

# Cache API response
api_cache.cache_response(
    "/api/users",
    {"page": 1, "limit": 10},
    {"users": [...], "total": 100},
    ttl=300
)

# Get cached response
response = api_cache.get_response(
    "/api/users",
    {"page": 1, "limit": 10}
)

# Get cache stats
stats = api_cache.get_cache_stats()
```

### 3. Computation Cache

```python
from redis_data_structures import LRUCache
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import json
import hashlib

class ComputationCache:
    def __init__(self, capacity: int = 1000):
        self.cache = LRUCache(capacity=capacity)
        self.results_key = "computation_results"
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate a unique cache key for computation."""
        key_data = {
            "func": func_name,
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def memoize(
        self, 
        ttl: int = 3600
    ) -> Callable:
        """Decorator to memoize function results."""
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                cache_key = self._generate_cache_key(
                    func.__name__, 
                    args, 
                    kwargs
                )
                
                # Try to get cached result
                cached = self.cache.peek(self.results_key, cache_key)
                if cached:
                    cached_at = datetime.fromisoformat(cached["cached_at"])
                    if cached_at + timedelta(seconds=cached["ttl"]) > datetime.now():
                        return cached["result"]
                
                # Compute result
                result = func(*args, **kwargs)
                
                # Cache result
                cache_data = {
                    "result": result,
                    "cached_at": datetime.now().isoformat(),
                    "ttl": ttl,
                    "func": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                }
                self.cache.put(self.results_key, cache_key, cache_data)
                
                return result
            return wrapper
        return decorator
    
    def invalidate_function(self, func_name: str):
        """Invalidate all cached results for a function."""
        all_cached = self.cache.get_all(self.results_key)
        for cache_key, cached in all_cached.items():
            if cached["func"] == func_name:
                self.cache.remove(self.results_key, cache_key)
    
    def get_computation_stats(self) -> Dict[str, Any]:
        """Get statistics about cached computations."""
        all_cached = self.cache.get_all(self.results_key)
        stats = {
            "total_cached": len(all_cached),
            "by_function": {},
            "expired": 0,
            "active": 0
        }
        
        now = datetime.now()
        for cached in all_cached.values():
            func_name = cached["func"]
            stats["by_function"][func_name] = \
                stats["by_function"].get(func_name, 0) + 1
                
            cached_at = datetime.fromisoformat(cached["cached_at"])
            if cached_at + timedelta(seconds=cached["ttl"]) < now:
                stats["expired"] += 1
            else:
                stats["active"] += 1
        
        return stats

# Usage
computation_cache = ComputationCache(capacity=1000)

# Use as decorator
@computation_cache.memoize(ttl=3600)
def expensive_computation(n: int) -> int:
    """Simulate expensive computation."""
    import time
    time.sleep(1)  # Simulate work
    return n * n

# First call computes and caches
result = expensive_computation(42)  # Takes ~1 second

# Subsequent calls are instant
result = expensive_computation(42)  # Returns cached result

# Get cache statistics
stats = computation_cache.get_computation_stats()

# Invalidate cache for function
computation_cache.invalidate_function("expensive_computation")
```

The LRU Cache implementation provides efficient caching with automatic eviction of least recently used items. Key features include:

- Constant time operations for most common operations (put, get, remove)
- Configurable cache capacity with automatic eviction
- Ability to peek at values without affecting LRU order
- Support for complex data types through serialization
- Thread-safe operations through Redis transactions
- Built-in support for cache statistics and monitoring

The example use cases demonstrate common scenarios:
1. User session management with TTL and automatic cleanup
2. API response caching with key generation and invalidation
3. Computation memoization with TTL and statistics tracking

The implementation is particularly useful when:
- You need a distributed cache shared between multiple services
- Cache capacity needs to be strictly controlled
- Access patterns benefit from LRU eviction policy
- You want to track and monitor cache usage
