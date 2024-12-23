# Trie (Prefix Tree)

A Redis-backed trie (prefix tree) implementation perfect for building features like autocomplete, spell checking, and prefix matching. This implementation provides efficient string operations with persistent storage.

## Features

- Prefix-based word lookup
- Efficient string search operations
- Thread-safe operations
- Persistent storage with Redis
- JSON serialization for data
- Atomic operations
- Size tracking
- Clear operation
- Empty string support

## Operations

| Operation    | Time Complexity | Description |
|-------------|----------------|-------------|
| `insert`    | O(m)          | Insert a word of length m |
| `search`    | O(m)          | Search for a word of length m |
| `starts_with`| O(p + n)      | Find words with prefix p (n = number of matches) |
| `delete`    | O(m)          | Delete a word of length m |
| `size`      | O(n)          | Get number of words (n = number of words) |
| `clear`     | O(n)          | Remove all words (n = number of nodes) |

## Basic Usage

```python
from redis_data_structures import Trie

# Initialize trie
trie = Trie(
    host='localhost',
    port=6379,
    db=0,
    username=None,  # Optional
    password=None   # Optional
)

# Basic operations
trie.insert('my_trie', 'hello')
trie.insert('my_trie', 'help')
trie.insert('my_trie', 'world')

# Search for words
exists = trie.search('my_trie', 'hello')  # Returns True
exists = trie.search('my_trie', 'help')   # Returns True
exists = trie.search('my_trie', 'hell')   # Returns False

# Find words with prefix
words = trie.starts_with('my_trie', 'hel')  # Returns ['hello', 'help']

# Delete a word
trie.delete('my_trie', 'hello')

# Get size and clear
size = trie.size('my_trie')
trie.clear('my_trie')

# Empty string handling
trie.insert('my_trie', '')  # Insert empty string
exists = trie.search('my_trie', '')  # Returns True
size = trie.size('my_trie')  # Returns 1 (counts empty string)
trie.delete('my_trie', '')  # Delete empty string
```

## Example Use Cases

### 1. Autocomplete System

Perfect for implementing real-time search suggestions.

```python
def get_suggestions(prefix: str) -> List[str]:
    trie = Trie(host='localhost', port=6379)
    return trie.starts_with('autocomplete', prefix)

# Add common search terms
trie.insert('autocomplete', 'python')
trie.insert('autocomplete', 'programming')
trie.insert('autocomplete', 'project')

# Get suggestions as user types
suggestions = get_suggestions('pro')  # Returns ['programming', 'project']
```

### 2. Spell Checker

Useful for implementing basic spell checking functionality.

```python
def is_word_valid(word: str) -> bool:
    trie = Trie(host='localhost', port=6379)
    return trie.search('dictionary', word.lower())

# Add dictionary words
trie.insert('dictionary', 'apple')
trie.insert('dictionary', 'banana')

# Check spelling
is_valid = is_word_valid('apple')  # Returns True
is_valid = is_word_valid('appel')  # Returns False
```

### 3. Domain Name System

Efficient for storing and searching domain names.

```python
def register_domain(domain: str) -> bool:
    trie = Trie(host='localhost', port=6379)
    if trie.search('domains', domain):
        return False  # Domain already exists
    return trie.insert('domains', domain)

# Register domains
register_domain('example.com')
register_domain('example.org')

# Check availability
is_taken = trie.search('domains', 'example.com')  # Returns True
```

## Implementation Details

The trie implementation uses Redis hashes to store nodes, where:
- Each node is a Redis hash containing its children
- Special marker '*' indicates end of word
- Keys are structured as `{trie_key}:{prefix}`
- Empty strings are stored in the root node
- Thread-safe operations using Redis atomic commands

## Best Practices

1. **Memory Management**
   - Monitor trie size for large datasets
   - Implement cleanup strategies for unused words
   - Consider TTL for temporary data

2. **Performance**
   ```python
   # Use batch operations when possible
   words = ['word1', 'word2', 'word3']
   for word in words:
       trie.insert('my_trie', word)
   ```

3. **Error Handling**
   ```python
   try:
       trie.insert('my_trie', word)
   except Exception as e:
       logger.error(f"Error inserting word: {e}")
       # Handle error...
   ```

## Common Issues

1. **Memory Usage**
   - Large datasets can consume significant memory
   - Consider implementing size limits
   - Regular cleanup of unused words

2. **Performance**
   - Long prefixes can slow down searches
   - Large result sets may impact response time
   - Consider implementing result limits

3. **Concurrency**
   - Operations are atomic
   - Safe for multi-reader/writer scenarios
   - Consider using connection pooling

## Troubleshooting

1. **Slow Searches**
   - Check prefix length
   - Monitor result set size
   - Verify Redis connection

2. **Memory Issues**
   - Monitor trie size
   - Implement word limits
   - Regular cleanup

3. **Connection Issues**
   - Check Redis connection
   - Verify credentials
   - Monitor network latency