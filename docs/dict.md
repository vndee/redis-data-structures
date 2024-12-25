# Dict

A Redis-backed python-likedictionary implementation that provides persistent key-value storage with type preservation. Unlike [HashMap](./hashmap.md) which uses Redis `HSET`/`HGET` commands, this implementation uses separate Redis keys for each dictionary entry, making it suitable for cases where you need more granular control over individual key expiration or when dealing with very large values.

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | :---: | :---: | --- | --- |
| `set` | $O(1)$ | $O(1)$ | Set a key's value | `SET` |
| `get` | $O(1)$ | $O(1)$ | Get a key's value | `GET` |
| `delete` | $O(1)$ | $O(1)$ | Delete a key | `DELETE` |
| `exists` | $O(1)$ | $O(1)$ | Check if a key exists | `EXISTS` |
| `keys` | $O(n)$ | $O(n)$ | Get all keys | `KEYS` |
| `values` | $O(n)$ | $O(n)$ | Get all values | Multiple `GET` |
| `items` | $O(n)$ | $O(n)$ | Get all key-value pairs | `KEYS` + Multiple `GET` |
| `size` | $O(n)$ | $O(n)$ | Get number of keys | `KEYS` |
| `clear` | $O(n)$ | $O(n)$ | Remove all keys | Multiple `DELETE` |

where:
- $n$ is the number of keys in the dictionary

> **Note:** While most operations have constant time complexity, operations that need to scan all keys (`keys`, `values`, `items`, `size`, `clear`) have linear complexity as they need to process all entries.

## Basic Usage

```python
from redis_data_structures import Dict

# Initialize dictionary
d = Dict(key="user_settings")

# Store values
d.set("theme", "dark")
d.set("language", "en")
d.set("notifications", True)

# Alternative syntax using subscript operator
d["theme"] = "dark"
d["language"] = "en"
d["notifications"] = True

# Retrieve values
theme = d.get("theme")  # Returns "dark"
exists = "language" in d  # Returns True

# Alternative syntax for retrieval
theme = d["theme"]  # Returns "dark"

# Get collection views
all_keys = d.keys()  # Returns list of all keys
all_values = d.values()  # Returns list of all values
all_items = d.items()  # Returns list of (key, value) tuples

# Remove values
d.delete("notifications")
del d["notifications"]  # Alternative syntax
d.clear()  # Remove all keys
```

## Advanced Usage

```python
from redis_data_structures import Dict
from typing import Dict as TypeDict, Any, Optional
from datetime import datetime
import json

class CacheManager:
    def __init__(self):
        self.dict = Dict(key="cache_data")
    
    def set_with_timestamp(self, key: str, value: Any) -> bool:
        """Store value with timestamp."""
        data = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        return self.dict.set(key, data)
    
    def get_with_timestamp(self, key: str) -> Optional[TypeDict[str, Any]]:
        """Retrieve value with its timestamp."""
        data = self.dict.get(key)
        if data is None:
            return None
        return {
            "value": data["value"],
            "stored_at": datetime.fromisoformat(data["timestamp"])
        }
    
    def get_all_cached_data(self) -> TypeDict[str, Any]:
        """Get all cached data with timestamps."""
        return dict(self.dict.items())
    
    def remove_old_entries(self, max_age_seconds: int) -> int:
        """Remove entries older than specified age."""
        now = datetime.now()
        removed = 0
        
        for key, data in self.dict.items():
            stored_at = datetime.fromisoformat(data["timestamp"])
            age = (now - stored_at).total_seconds()
            
            if age > max_age_seconds:
                self.dict.delete(key)
                removed += 1
        
        return removed

# Usage
cache = CacheManager()

# Store some data
cache.set_with_timestamp("user_123", {
    "name": "John Doe",
    "last_login": "2024-01-01"
})

# Retrieve data with timestamp
data = cache.get_with_timestamp("user_123")
print(f"Value: {data['value']}")
print(f"Stored at: {data['stored_at']}")

# Clean up old entries
removed = cache.remove_old_entries(3600)  # Remove entries older than 1 hour
```

## Example Use Cases

### 1. Session Store

```python
from redis_data_structures import Dict
from typing import Optional, Dict as TypeDict
from datetime import datetime, timedelta
import secrets

class SessionStore:
    def __init__(self, expiry_minutes: int = 30):
        self.sessions = Dict(key="sessions")
        self.expiry_minutes = expiry_minutes
    
    def create_session(self, user_id: str, data: TypeDict) -> str:
        """Create a new session."""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "user_id": user_id,
            "data": data,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=self.expiry_minutes)).isoformat()
        }
        self.sessions.set(session_id, session_data)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[TypeDict]:
        """Get session if valid."""
        session = self.sessions.get(session_id)
        if not session:
            return None
            
        expires_at = datetime.fromisoformat(session["expires_at"])
        if expires_at < datetime.now():
            self.sessions.delete(session_id)
            return None
            
        return session["data"]
    
    def extend_session(self, session_id: str) -> bool:
        """Extend session expiry."""
        session = self.sessions.get(session_id)
        if not session:
            return False
            
        session["expires_at"] = (
            datetime.now() + timedelta(minutes=self.expiry_minutes)
        ).isoformat()
        return self.sessions.set(session_id, session)
    
    def end_session(self, session_id: str) -> bool:
        """End a session."""
        return self.sessions.delete(session_id)

# Usage
store = SessionStore(expiry_minutes=60)

# Create session
session_id = store.create_session(
    "user_123",
    {
        "username": "john_doe",
        "role": "admin",
        "login_time": datetime.now().isoformat()
    }
)

# Get session data
session = store.get_session(session_id)

# Extend session
store.extend_session(session_id)

# End session
store.end_session(session_id)
```

### 2. Feature Flag System

```python
from redis_data_structures import Dict
from typing import Dict as TypeDict, Any, List
from datetime import datetime

class FeatureFlags:
    def __init__(self):
        self.flags = Dict(key="feature_flags")
        self.history = Dict(key="flag_history")
    
    def set_flag(self, name: str, enabled: bool, metadata: TypeDict[str, Any] = None) -> bool:
        """Set a feature flag."""
        flag_data = {
            "enabled": enabled,
            "metadata": metadata or {},
            "updated_at": datetime.now().isoformat()
        }
        
        # Store current state in history
        current = self.flags.get(name)
        if current:
            history_key = f"{name}:{datetime.now().isoformat()}"
            self.history.set(history_key, current)
        
        return self.flags.set(name, flag_data)
    
    def is_enabled(self, name: str) -> bool:
        """Check if a feature is enabled."""
        flag = self.flags.get(name)
        return flag["enabled"] if flag else False
    
    def get_flag_details(self, name: str) -> TypeDict[str, Any]:
        """Get full flag details."""
        return self.flags.get(name)
    
    def list_flags(self) -> List[str]:
        """List all feature flags."""
        return self.flags.keys()
    
    def get_flag_history(self, name: str) -> List[TypeDict[str, Any]]:
        """Get history of a flag's changes."""
        history = []
        for key, value in self.history.items():
            if key.startswith(f"{name}:"):
                history.append(value)
        return sorted(history, key=lambda x: x["updated_at"])

# Usage
flags = FeatureFlags()

# Set feature flags
flags.set_flag("dark_mode", True, {
    "description": "Enable dark mode theme",
    "owner": "UI Team"
})

flags.set_flag("beta_feature", False, {
    "description": "New beta feature",
    "owner": "Product Team",
    "rollout_percentage": 0
})

# Check features
if flags.is_enabled("dark_mode"):
    print("Dark mode is enabled")

# Get flag details
beta_details = flags.get_flag_details("beta_feature")
print(f"Beta feature status: {beta_details}")

# View history
history = flags.get_flag_history("dark_mode")
for change in history:
    print(f"Changed at {change['updated_at']}: {change['enabled']}")
```

### 3. Distributed Counter System

```python
from redis_data_structures import Dict
from typing import Dict as TypeDict
from datetime import datetime, timedelta
import json

class DistributedCounters:
    def __init__(self):
        self.counters = Dict(key="counters")
        self.metadata = Dict(key="counter_metadata")
    
    def increment(self, name: str, amount: int = 1) -> int:
        """Increment a counter."""
        current = self.counters.get(name) or 0
        new_value = current + amount
        self.counters.set(name, new_value)
        
        # Update metadata
        metadata = self.metadata.get(name) or {
            "created_at": datetime.now().isoformat(),
            "min_value": new_value,
            "max_value": new_value,
            "updates": 0
        }
        
        metadata.update({
            "last_updated": datetime.now().isoformat(),
            "min_value": min(metadata["min_value"], new_value),
            "max_value": max(metadata["max_value"], new_value),
            "updates": metadata["updates"] + 1
        })
        
        self.metadata.set(name, metadata)
        return new_value
    
    def decrement(self, name: str, amount: int = 1) -> int:
        """Decrement a counter."""
        return self.increment(name, -amount)
    
    def get_value(self, name: str) -> int:
        """Get current counter value."""
        return self.counters.get(name) or 0
    
    def get_stats(self, name: str) -> TypeDict:
        """Get counter statistics."""
        value = self.get_value(name)
        metadata = self.metadata.get(name)
        
        if not metadata:
            return {"value": value}
        
        return {
            "value": value,
            "min_value": metadata["min_value"],
            "max_value": metadata["max_value"],
            "updates": metadata["updates"],
            "created_at": metadata["created_at"],
            "last_updated": metadata["last_updated"]
        }
    
    def reset(self, name: str) -> bool:
        """Reset a counter to zero."""
        self.counters.delete(name)
        self.metadata.delete(name)
        return True

# Usage
counters = DistributedCounters()

# Track various metrics
counters.increment("daily_visits")
counters.increment("api_calls", 5)
counters.decrement("available_slots")

# Get current values
visits = counters.get_value("daily_visits")
api_calls = counters.get_value("api_calls")

# Get detailed statistics
stats = counters.get_stats("api_calls")
print(f"API Calls Stats: {json.dumps(stats, indent=2)}")

# Reset counters
counters.reset("daily_visits")
``` 