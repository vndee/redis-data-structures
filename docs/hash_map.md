# Hash Map

A Redis-backed Hash Map implementation that stores field-value pairs under a single key. Perfect for storing object attributes, configuration settings, and structured data.

## Features

- Field-value pair storage
- Thread-safe operations
- Persistent storage with Redis
- JSON serialization for complex data types
- Atomic operations
- Size tracking
- Field-level operations

## Operations

| Operation    | Time Complexity | Description |
|-------------|----------------|-------------|
| `set`       | O(1)          | Set a field-value pair |
| `get`       | O(1)          | Get value of a field |
| `get_all`   | O(N)          | Get all field-value pairs |
| `remove`    | O(1)          | Remove a field |
| `size`      | O(1)          | Get number of fields |
| `clear`     | O(1)          | Remove all fields |

## Basic Usage

```python
from redis_data_structures import HashMap

# Initialize hash map
hm = HashMap(
    host='localhost',
    port=6379,
    db=0,
    username=None,  # Optional
    password=None   # Optional
)

# Basic operations
hm.set('user:123', 'name', 'John Doe')
hm.set('user:123', 'email', 'john@example.com')
name = hm.get('user:123', 'name')  # Returns 'John Doe'
all_fields = hm.get_all('user:123')  # Returns {'name': 'John Doe', 'email': 'john@example.com'}
size = hm.size('user:123')
hm.remove('user:123', 'email')
hm.clear('user:123')
```

## Example Use Cases

### 1. User Profile System

Perfect for managing user profiles with multiple attributes.

```python
class UserProfile:
    def __init__(self):
        self.profiles = HashMap(host='localhost', port=6379)
    
    def create_profile(self, user_id: str, data: dict) -> bool:
        """Create a new user profile."""
        key = f'user:{user_id}'
        try:
            # Add basic info
            self.profiles.set(key, 'id', user_id)
            self.profiles.set(key, 'created_at', str(time.time()))
            
            # Add all provided data
            for field, value in data.items():
                self.profiles.set(key, field, json.dumps(value))
            return True
        except Exception as e:
            print(f"Error creating profile: {e}")
            return False
    
    def update_profile(self, user_id: str, updates: dict) -> bool:
        """Update specific fields in a user profile."""
        key = f'user:{user_id}'
        try:
            for field, value in updates.items():
                self.profiles.set(key, field, json.dumps(value))
            self.profiles.set(key, 'updated_at', str(time.time()))
            return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False
    
    def get_profile(self, user_id: str) -> dict:
        """Get complete user profile."""
        key = f'user:{user_id}'
        profile = self.profiles.get_all(key)
        return {
            field: json.loads(value) if field not in ['id', 'created_at', 'updated_at']
            else value
            for field, value in profile.items()
        }
    
    def get_field(self, user_id: str, field: str) -> Any:
        """Get specific field from user profile."""
        key = f'user:{user_id}'
        value = self.profiles.get(key, field)
        return json.loads(value) if value else None

# Usage
profiles = UserProfile()
profiles.create_profile('123', {
    'name': 'John Doe',
    'email': 'john@example.com',
    'preferences': {'theme': 'dark', 'notifications': True}
})
profile = profiles.get_profile('123')
theme = profiles.get_field('123', 'preferences')['theme']
```

### 2. Configuration Management

Ideal for managing application configuration with multiple components.

```python
class ConfigManager:
    def __init__(self):
        self.config = HashMap(host='localhost', port=6379)
        self.default_ttl = 3600  # 1 hour
    
    def set_config(self, component: str, settings: dict):
        """Set configuration for a component."""
        key = f'config:{component}'
        for setting, value in settings.items():
            self.config.set(key, setting, json.dumps({
                'value': value,
                'updated_at': time.time()
            }))
    
    def get_config(self, component: str, setting: str = None) -> Any:
        """Get configuration value(s)."""
        key = f'config:{component}'
        if setting:
            value = self.config.get(key, setting)
            return json.loads(value)['value'] if value else None
        
        all_settings = self.config.get_all(key)
        return {
            k: json.loads(v)['value']
            for k, v in all_settings.items()
        }
    
    def update_config(self, component: str, updates: dict):
        """Update specific configuration settings."""
        current = self.get_config(component)
        current.update(updates)
        self.set_config(component, current)
    
    def remove_config(self, component: str, setting: str = None):
        """Remove configuration setting(s)."""
        key = f'config:{component}'
        if setting:
            self.config.remove(key, setting)
        else:
            self.config.clear(key)

# Usage
config = ConfigManager()
config.set_config('database', {
    'host': 'localhost',
    'port': 5432,
    'max_connections': 100
})
db_config = config.get_config('database')
max_conn = config.get_config('database', 'max_connections')
```

### 3. Shopping Cart

Perfect for managing shopping cart items with quantities.

```python
class ShoppingCart:
    def __init__(self):
        self.carts = HashMap(host='localhost', port=6379)
    
    def add_item(self, cart_id: str, item_id: str, quantity: int = 1):
        """Add item to cart."""
        key = f'cart:{cart_id}'
        current = self.get_item_quantity(cart_id, item_id)
        
        item_data = {
            'quantity': current + quantity,
            'added_at': time.time(),
            'updated_at': time.time()
        }
        self.carts.set(key, item_id, json.dumps(item_data))
    
    def remove_item(self, cart_id: str, item_id: str):
        """Remove item from cart."""
        key = f'cart:{cart_id}'
        self.carts.remove(key, item_id)
    
    def update_quantity(self, cart_id: str, item_id: str, quantity: int):
        """Update item quantity."""
        if quantity <= 0:
            self.remove_item(cart_id, item_id)
            return
        
        key = f'cart:{cart_id}'
        item_data = {
            'quantity': quantity,
            'added_at': time.time(),
            'updated_at': time.time()
        }
        self.carts.set(key, item_id, json.dumps(item_data))
    
    def get_item_quantity(self, cart_id: str, item_id: str) -> int:
        """Get quantity of an item."""
        key = f'cart:{cart_id}'
        item_data = self.carts.get(key, item_id)
        return json.loads(item_data)['quantity'] if item_data else 0
    
    def get_cart(self, cart_id: str) -> dict:
        """Get entire cart contents."""
        key = f'cart:{cart_id}'
        cart = self.carts.get_all(key)
        return {
            item_id: json.loads(data)
            for item_id, data in cart.items()
        }
    
    def clear_cart(self, cart_id: str):
        """Remove all items from cart."""
        key = f'cart:{cart_id}'
        self.carts.clear(key)

# Usage
cart = ShoppingCart()
cart.add_item('cart123', 'product1', 2)
cart.add_item('cart123', 'product2', 1)
cart.update_quantity('cart123', 'product1', 3)
items = cart.get_cart('cart123')
```

## Best Practices

1. **Key Management**
   - Use descriptive key names: `user:profiles`, `app:config`, etc.
   - Consider implementing key expiration for temporary data
   - Clear hash maps that are no longer needed

2. **Error Handling**
   ```python
   try:
       hm.set('my_hash', 'field', value)
   except redis.RedisError as e:
       logger.error(f"Redis error: {e}")
       # Handle error...
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
       # Handle error...
   ```

3. **Memory Management**
   - Monitor field count for large hash maps
   - Implement size limits if needed
   ```python
   if hm.size('my_hash') > MAX_FIELDS:
       # Handle size limit...
       pass
   ```

4. **Performance**
   - Use batch operations when possible
   - Consider field naming conventions
   - Implement cleanup strategies

## Common Patterns

### 1. Caching with TTL
```python
class CacheManager:
    def __init__(self):
        self.cache = HashMap(host='localhost', port=6379)
        self.ttl = 3600  # 1 hour
    
    def set_cached(self, key: str, field: str, value: Any):
        """Cache a value with timestamp."""
        self.cache.set(key, field, json.dumps({
            'value': value,
            'timestamp': time.time()
        }))
    
    def get_cached(self, key: str, field: str) -> Optional[Any]:
        """Get cached value if not expired."""
        data = self.cache.get(key, field)
        if not data:
            return None
        
        cached = json.loads(data)
        if time.time() - cached['timestamp'] > self.ttl:
            self.cache.remove(key, field)
            return None
        
        return cached['value']
```

### 2. Versioned Data
```python
class VersionedData:
    def __init__(self):
        self.data = HashMap(host='localhost', port=6379)
    
    def set_version(self, key: str, field: str, value: Any):
        """Set a new version of data."""
        versions = self.get_versions(key, field)
        versions.append({
            'value': value,
            'version': len(versions) + 1,
            'timestamp': time.time()
        })
        self.data.set(key, field, json.dumps(versions))
    
    def get_latest(self, key: str, field: str) -> Optional[Any]:
        """Get latest version of data."""
        versions = self.get_versions(key, field)
        return versions[-1]['value'] if versions else None
    
    def get_version(self, key: str, field: str, version: int) -> Optional[Any]:
        """Get specific version of data."""
        versions = self.get_versions(key, field)
        for v in versions:
            if v['version'] == version:
                return v['value']
        return None
    
    def get_versions(self, key: str, field: str) -> list:
        """Get all versions of data."""
        data = self.data.get(key, field)
        return json.loads(data) if data else []
```

### 3. Hierarchical Data
```python
class HierarchicalData:
    def __init__(self):
        self.data = HashMap(host='localhost', port=6379)
    
    def set_nested(self, key: str, path: str, value: Any):
        """Set value at nested path."""
        parts = path.split('.')
        current = self.get_all_nested(key) or {}
        target = current
        
        # Navigate to nested location
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        
        # Set value
        target[parts[-1]] = value
        self.data.set(key, 'data', json.dumps(current))
    
    def get_nested(self, key: str, path: str) -> Any:
        """Get value from nested path."""
        parts = path.split('.')
        current = self.get_all_nested(key) or {}
        
        # Navigate to nested location
        for part in parts:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        
        return current
    
    def get_all_nested(self, key: str) -> dict:
        """Get all nested data."""
        data = self.data.get(key, 'data')
        return json.loads(data) if data else {}
```

## Limitations

1. **Field Name Size**
   - Field names consume memory
   - Long field names impact memory usage

2. **No Field Ordering**
   - Fields are not stored in any particular order
   - Cannot retrieve fields by position

3. **Single Key-Space**
   - All fields share same key space
   - Field name collisions possible

## Performance Considerations

1. **Time Complexity**
   - Most operations are O(1)
   - Full hash retrieval is O(N)

2. **Memory Usage**
   - Each field and value consumes memory
   - Consider field name length

3. **Concurrency**
   - Operations are atomic
   - Safe for multi-threaded use

## Troubleshooting

1. **Missing Fields**
   - Check field names
   - Verify key names
   - Check for accidental removals

2. **Memory Issues**
   - Monitor field count
   - Check field name lengths
   - Regular cleanup of unused data

3. **Performance Issues**
   - Avoid frequent full hash retrieval
   - Use appropriate field names
   - Monitor Redis performance
