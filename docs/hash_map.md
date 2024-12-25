# HashMap

A Redis-backed hash map implementation that provides persistent key-value storage with type preservation. Perfect for storing structured data, managing user profiles, caching complex objects, and maintaining configuration settings.

> **Note:** For more granular control over individual key expiration or when dealing with very large values, consider using [Dict](./dict.md).

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | :---: | :---: | --- | --- |
| `set` | $O(1)$ | $O(n)$ | Set a field's value | `HSET` |
| `get` | $O(1)$ | $O(n)$ | Get a field's value | `HGET` |
| `delete` | $O(1)$ | $O(n)$ | Delete a field | `HDEL` |
| `exists` | $O(1)$ | $O(n)$ | Check if a field exists | `HEXISTS` |
| `get_all` | $O(n)$ | $O(n)$ | Get all field-value pairs | `HGETALL` |
| `get_fields` | $O(n)$ | $O(n)$ | Get all field names | `HKEYS` |
| `size` | $O(1)$ | $O(1)$ | Get number of fields | `HLEN` |
| `clear` | $O(1)$ | $O(1)$ | Remove all fields | `DELETE` |

where:
- $n$ is the number of fields in the hash map

> **Note:** The $O(n)$ worst case for operations like `set`, `get`, `delete`, and `exists` occurs due to potential hash collisions in Redis's internal hash table implementation and the size of the serialized values being stored/retrieved.

## Basic Usage

```python
from redis_data_structures import HashMap

# Initialize hash map
hm = HashMap(key="user_settings")

# Store values
hm.set("theme", "dark")
hm.set("language", "en")
hm.set("notifications", True)

# Retrieve values
theme = hm.get("theme")  # Returns "dark"
exists = hm.exists("language")  # Returns True

# Get multiple values
all_settings = hm.get_all()  # Returns dict of all settings
field_names = hm.get_fields()  # Returns list of field names

# Remove values
hm.delete("notifications")
hm.clear()  # Remove all fields
```

## Advanced Usage

```python
from redis_data_structures import HashMap
from typing import Dict, Any, Optional
from datetime import datetime
import json

class UserProfileManager:
    def __init__(self):
        self.hash_map = HashMap(key="user_profiles")
    
    def create_profile(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Create a new user profile."""
        if self.hash_map.exists(user_id):
            return False
            
        profile_data = {
            **data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        return self.hash_map.set(user_id, profile_data)
    
    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing profile."""
        current_profile = self.get_profile(user_id)
        if not current_profile:
            return False
        
        updated_profile = {
            **current_profile,
            **updates,
            "updated_at": datetime.now().isoformat(),
        }
        return self.hash_map.set(user_id, updated_profile)
    
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile."""
        return self.hash_map.get(user_id)
    
    def delete_profile(self, user_id: str) -> bool:
        """Delete user profile."""
        return self.hash_map.delete(user_id)
    
    def list_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all user profiles."""
        return self.hash_map.get_all()

# Usage
manager = UserProfileManager()

# Create profile
manager.create_profile(
    "user123",
    {
        "name": "John Doe",
        "email": "john@example.com",
        "preferences": {
            "theme": "dark",
            "notifications": True
        }
    }
)

# Update profile
manager.update_profile(
    "user123",
    {"preferences": {"theme": "light"}}
)

# Get profile
profile = manager.get_profile("user123")
```

## Example Use Cases

### 1. Configuration Management System

```python
from redis_data_structures import HashMap
from typing import Any, Dict, Optional
from datetime import datetime
import json

class ConfigurationManager:
    def __init__(self):
        self.hash_map = HashMap(key="app_config")
        self.history_key = "config_history"
    
    def set_config(self, component: str, config: Dict[str, Any]) -> bool:
        """Set configuration for a component."""
        # Store current config in history
        current = self.get_config(component)
        if current:
            timestamp = datetime.now().isoformat()
            history_entry = {
                "config": current,
                "timestamp": timestamp,
                "type": "update"
            }
            self.hash_map.set(f"{component}_{timestamp}", history_entry)
        
        # Set new config
        config_data = {
            "data": config,
            "updated_at": datetime.now().isoformat(),
            "version": (current.get("version", 0) + 1) if current else 1
        }
        return self.hash_map.set(component, config_data)
    
    def get_config(self, component: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a component."""
        return self.hash_map.get(component)
    
    def list_components(self) -> list[str]:
        """List all configured components."""
        return self.hash_map.get_fields()
    
    def get_component_history(self, component: str) -> list[Dict[str, Any]]:
        """Get configuration history for a component."""
        all_history = self.hash_map.get_all()
        return [
            entry for key, entry in all_history.items()
            if key.startswith(component)
        ]

# Usage
config_manager = ConfigurationManager()

# Set database configuration
config_manager.set_config("database", {
    "host": "localhost",
    "port": 5432,
    "max_connections": 100
})

# Update configuration
config_manager.set_config("database", {
    "host": "localhost",
    "port": 5432,
    "max_connections": 200  # Increased
})

# Get current config
db_config = config_manager.get_config("database")

# View history
history = config_manager.get_component_history("database")
```

### 2. Cache Management System

```python
from redis_data_structures import HashMap
from typing import Any, Optional
from datetime import datetime, timedelta
import time

class CacheManager:
    def __init__(self, default_ttl: int = 3600):
        self.hash_map = HashMap(key="cache_data")
        self.metadata_key = "cache_metadata"
        self.default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a cached value with optional TTL."""
        # Store the value
        success = self.hash_map.set(key, value)
        if not success:
            return False
        
        # Store metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "expires_at": (
                datetime.now() + timedelta(seconds=ttl or self.default_ttl)
            ).isoformat()
        }
        return self.hash_map.set(key, metadata)
    
    def get(self, key: str) -> Optional[Any]:
        """Get a cached value if not expired."""
        # Check metadata first
        metadata = self.hash_map.get(key)
        if not metadata:
            return None
        
        # Check expiration
        expires_at = datetime.fromisoformat(metadata["expires_at"])
        if expires_at < datetime.now():
            # Clean up expired data
            self.hash_map.delete(key)
            self.hash_map.delete(key)
            return None
        
        return self.hash_map.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete a cached value and its metadata."""
        return all([
            self.hash_map.delete(key),
            self.hash_map.delete(key)
        ])
    
    def clear_expired(self) -> int:
        """Clear all expired cache entries."""
        cleared = 0
        metadata = self.hash_map.get_all()
        
        for key, data in metadata.items():
            expires_at = datetime.fromisoformat(data["expires_at"])
            if expires_at < datetime.now():
                self.delete(key)
                cleared += 1
        
        return cleared

# Usage
cache = CacheManager(default_ttl=60)  # 1 minute default TTL

# Cache some data
cache.set("user_123", {"name": "John", "age": 30})
cache.set("temp_data", [1, 2, 3], ttl=10)  # Short TTL

# Get cached data
user_data = cache.get("user_123")
time.sleep(11)
temp_data = cache.get("temp_data")  # Returns None (expired)

# Clear expired entries
cleared = cache.clear_expired()
```

### 3. Session Management System

```python
from redis_data_structures import HashMap
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import secrets
import json

class SessionManager:
    def __init__(self, session_timeout: int = 3600):
        self.hash_map = HashMap(key="active_sessions")
        self.session_timeout = session_timeout
    
    def create_session(self, user_id: str, data: Dict[str, Any]) -> str:
        """Create a new session."""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "user_id": user_id,
            "data": data,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=self.session_timeout)).isoformat()
        }
        
        if self.hash_map.set(session_id, session_data):
            return session_id
        return ""
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data if valid."""
        session = self.hash_map.get(session_id)
        if not session:
            return None
        
        # Check expiration
        expires_at = datetime.fromisoformat(session["expires_at"])
        if expires_at < datetime.now():
            self.end_session(session_id)
            return None
        
        # Update last accessed time and expiration
        session.update({
            "last_accessed": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=self.session_timeout)).isoformat()
        })
        self.hash_map.set(session_id, session)
        
        return session["data"]
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data."""
        session = self.hash_map.get(session_id)
        if not session:
            return False
        
        session.update({
            "data": data,
            "last_accessed": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=self.session_timeout)).isoformat()
        })
        return self.hash_map.set(session_id, session)
    
    def end_session(self, session_id: str) -> bool:
        """End a session."""
        return self.hash_map.delete(session_id)
    
    def cleanup_expired(self) -> int:
        """Remove expired sessions."""
        cleaned = 0
        all_sessions = self.hash_map.get_all()
        
        for session_id, session in all_sessions.items():
            expires_at = datetime.fromisoformat(session["expires_at"])
            if expires_at < datetime.now():
                self.end_session(session_id)
                cleaned += 1
        
        return cleaned

# Usage
session_manager = SessionManager(session_timeout=1800)  # 30 minute timeout

# Create session
session_id = session_manager.create_session(
    "user123",
    {
        "username": "john_doe",
        "role": "admin",
        "preferences": {"theme": "dark"}
    }
)

# Get session data
session_data = session_manager.get_session(session_id)

# Update session
session_manager.update_session(session_id, {
    "username": "john_doe",
    "role": "admin",
    "preferences": {"theme": "light"}  # Updated preference
})

# End session
session_manager.end_session(session_id)

# Cleanup expired sessions
cleaned = session_manager.cleanup_expired()
```