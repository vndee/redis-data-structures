# Set

A Redis-backed set implementation that maintains a collection of unique elements with automatic type preservation. Perfect for tracking unique items, implementing session management, handling member relationships, and performing set operations.

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | :---: | :---: | --- | --- |
| `add` | $O(1)$ | $O(n)$ | Add an item to the set | `SADD` |
| `remove` | $O(1)$ | $O(n)$ | Remove an item from the set | `SREM` |
| `contains` | $O(1)$ | $O(n)$ | Check if an item exists in the set | `SISMEMBER` |
| `members` | $O(n)$ | $O(n)$ | Get all items in the set | `SMEMBERS` |
| `pop` | $O(1)$ | $O(n)$ | Remove and return a random item | `SPOP` |
| `size` | $O(1)$ | $O(1)$ | Get the number of items | `SCARD` |
| `clear` | $O(1)$ | $O(1)$ | Remove all items | `DELETE` |

where:
- $n$ is the number of items in the set

## Basic Usage

```python
from redis_data_structures import Set

# Initialize set
set_ds = Set(key="my_set")

# Add items
set_ds.add("item1")
set_ds.add("item2")

# Check membership
exists = set_ds.contains("item1")  # Returns True

# Get all members
items = set_ds.members()  # Returns {"item1", "item2"}

# Remove items
set_ds.remove("item1")

# Get size
size = set_ds.size()  # Returns 1

# Get random item
item = set_ds.pop()

# Clear set
set_ds.clear()
```

## Advanced Usage

```python
from redis_data_structures import Set
from typing import Any, Dict, Set as PySet
from datetime import datetime
import json

class UserSessionManager:
    def __init__(self):
        self.premium_set = Set(key="premium_sessions")
        self.active_set = Set(key="active_sessions")
    
    def start_session(self, user_id: str, metadata: Dict[str, Any] = None):
        """Start a new user session."""
        session_data = {
            "user_id": user_id,
            "started_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        return self.active_set.add(session_data)
    
    def end_session(self, user_id: str):
        """End a user session."""
        sessions = self.active_set.members()
        for session in sessions:
            if session["user_id"] == user_id:
                return self.active_set.remove(session)
        return False
    
    def upgrade_to_premium(self, user_id: str):
        """Upgrade user to premium."""
        sessions = self.active_set.members()
        for session in sessions:
            if session["user_id"] == user_id:
                session["metadata"]["account_type"] = "premium"
                self.premium_set.add(session)
                return True
        return False
    
    def get_active_sessions(self) -> PySet[Dict[str, Any]]:
        """Get all active sessions."""
        return self.active_set.members()
    
    def get_premium_sessions(self) -> PySet[Dict[str, Any]]:
        """Get premium sessions."""
        return self.premium_set.members()

# Usage
session_manager = UserSessionManager()

# Start sessions
session_manager.start_session("user1", {"device": "mobile"})
session_manager.start_session("user2", {"device": "desktop"})

# Upgrade user
session_manager.upgrade_to_premium("user1")

# Get sessions
active = session_manager.get_active_sessions()
premium = session_manager.get_premium_sessions()
```

## Example Use Cases

### 1. Activity Tracking System

```python
from redis_data_structures import Set
from typing import Dict, Any, Set as PySet
from datetime import datetime, timedelta
import json

class ActivityTracker:
    def __init__(self):
        self.set_ds = Set(key="activity_tracker")
    
    def get_daily_key(self, date: datetime) -> str:
        """Get Redis key for specific date."""
        return f"activity:{date.strftime('%Y-%m-%d')}"
    
    def track_activity(self, user_id: str, activity_type: str, metadata: Dict[str, Any] = None):
        """Track user activity."""
        activity = {
            "user_id": user_id,
            "type": activity_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        key = self.get_daily_key(datetime.now())
        return self.set_ds.add(activity)
    
    def get_user_activities(self, user_id: str, days: int = 7) -> PySet[Dict[str, Any]]:
        """Get user activities for the past n days."""
        activities = set()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        current = start_date
        while current <= end_date:
            key = self.get_daily_key(current)
            daily_activities = self.set_ds.members()
            user_activities = {
                activity for activity in daily_activities 
                if activity["user_id"] == user_id
            }
            activities.update(user_activities)
            current += timedelta(days=1)
        
        return activities
    
    def get_activity_summary(self, activity_type: str, date: datetime) -> PySet[Dict[str, Any]]:
        """Get all activities of a specific type for a date."""
        key = self.get_daily_key(date)
        activities = self.set_ds.members()
        return {
            activity for activity in activities 
            if activity["type"] == activity_type
        }

# Usage
tracker = ActivityTracker()

# Track activities
tracker.track_activity(
    "user1",
    "login",
    {"device": "mobile", "location": "New York"}
)

tracker.track_activity(
    "user1",
    "purchase",
    {"product_id": "123", "amount": 49.99}
)

# Get user activities
activities = tracker.get_user_activities("user1", days=7)

# Get activity summary
logins = tracker.get_activity_summary("login", datetime.now())
```

### 2. Tag Management System

```python
from redis_data_structures import Set
from typing import Set as PySet
from datetime import datetime

class TagManager:
    def __init__(self):
        self.set_ds = Set(key="tag_manager")
    
    def get_entity_key(self, entity_type: str, entity_id: str) -> str:
        """Get Redis key for entity tags."""
        return f"tags:{entity_type}:{entity_id}"
    
    def add_tags(self, entity_type: str, entity_id: str, tags: PySet[str]):
        """Add tags to an entity."""
        key = self.get_entity_key(entity_type, entity_id)
        for tag in tags:
            tag_data = {
                "name": tag.lower(),
                "added_at": datetime.now().isoformat()
            }
            self.set_ds.add(tag_data)
    
    def remove_tags(self, entity_type: str, entity_id: str, tags: PySet[str]):
        """Remove tags from an entity."""
        key = self.get_entity_key(entity_type, entity_id)
        current_tags = self.get_tags(entity_type, entity_id)
        
        for current in current_tags:
            if current["name"] in tags:
                self.set_ds.remove(current)
    
    def get_tags(self, entity_type: str, entity_id: str) -> PySet[dict]:
        """Get all tags for an entity."""
        key = self.get_entity_key(entity_type, entity_id)
        return self.set_ds.members()
    
    def find_common_tags(self, entity_type: str, id1: str, id2: str) -> PySet[str]:
        """Find common tags between two entities."""
        tags1 = {t["name"] for t in self.get_tags(entity_type, id1)}
        tags2 = {t["name"] for t in self.get_tags(entity_type, id2)}
        return tags1 & tags2

# Usage
tag_manager = TagManager()

# Add tags to posts
tag_manager.add_tags("post", "post1", {"python", "redis", "database"})
tag_manager.add_tags("post", "post2", {"redis", "database", "nosql"})

# Get tags
post1_tags = tag_manager.get_tags("post", "post1")

# Find common tags
common = tag_manager.find_common_tags("post", "post1", "post2")
```

### 3. Real-time Analytics Tracker

```python
from redis_data_structures import Set
from typing import Dict, Any, Set as PySet
from datetime import datetime, timedelta
import json

class AnalyticsTracker:
    def __init__(self):
        self.daily_set = Set(key="daily_events")
        self.hourly_set = Set(key="hourly_events")
    
    def track_event(self, event_type: str, user_id: str, metadata: Dict[str, Any] = None):
        """Track an analytics event."""
        now = datetime.now()
        hourly_key = f"events:{event_type}:{now.strftime('%Y-%m-%d-%H')}"
        daily_key = f"events:{event_type}:{now.strftime('%Y-%m-%d')}"
        
        event_data = {
            "user_id": user_id,
            "timestamp": now.isoformat(),
            "metadata": metadata or {}
        }
        
        # Store in both hourly and daily sets
        self.hourly_set.add(event_data)
        self.daily_set.add(event_data)
    
    def get_unique_users(self, event_type: str, hours: int = 24) -> int:
        """Get unique users for an event type in the last n hours."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        unique_users = set()
        current = start_time
        
        while current <= end_time:
            key = f"events:{event_type}:{current.strftime('%Y-%m-%d-%H')}"
            events = self.hourly_set.members()
            users = {event["user_id"] for event in events}
            unique_users.update(users)
            current += timedelta(hours=1)
        
        return len(unique_users)
    
    def get_event_data(self, event_type: str, date: datetime) -> PySet[Dict[str, Any]]:
        """Get all event data for a specific day."""
        key = f"events:{event_type}:{date.strftime('%Y-%m-%d')}"
        return self.daily_set.members()
    
    def get_user_events(
        self, 
        user_id: str, 
        event_type: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> PySet[Dict[str, Any]]:
        """Get all events for a user in a date range."""
        events = set()
        current = start_date
        
        while current <= end_date:
            key = f"events:{event_type}:{current.strftime('%Y-%m-%d')}"
            daily_events = self.daily_set.members()
            user_events = {
                event for event in daily_events 
                if event["user_id"] == user_id
            }
            events.update(user_events)
            current += timedelta(days=1)
        
        return events

# Usage
analytics = AnalyticsTracker()

# Track events
analytics.track_event(
    "page_view",
    "user1",
    {"page": "/home", "source": "direct"}
)

analytics.track_event(
    "click",
    "user1",
    {"element": "signup_button"}
)

# Get analytics
unique_users = analytics.get_unique_users("page_view", hours=24)
daily_views = analytics.get_event_data("page_view", datetime.now())
user_clicks = analytics.get_user_events(
    "user1",
    "click",
    datetime.now() - timedelta(days=7),
    datetime.now()
)
```