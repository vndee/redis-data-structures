# Trie (Prefix Tree)

A Redis-backed trie (prefix tree) implementation that provides efficient string operations and prefix-based lookups. Perfect for implementing autocomplete, spell checking, prefix matching, and other string-based search functionalities.

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | :---: | :---: | --- | --- |
| `insert` | $O(m)$ | $O(m)$ | Insert a word into trie | `HSET` |
| `search` | $O(m)$ | $O(m)$ | Check if word exists | `HEXISTS` |
| `starts_with` | $O(p + n)$ | $O(p + n)$ | Find all words with prefix | `HKEYS` |
| `delete` | $O(m)$ | $O(m)$ | Remove a word | `HDEL` |
| `size` | $O(n)$ | $O(n)$ | Get number of words | `SCAN` |
| `clear` | $O(n)$ | $O(n)$ | Remove all words | `DELETE` |

where:
- $m$ is the length of the word
- $p$ is the length of the prefix
- $n$ is the number of words in the trie

## Basic Usage

```python
from redis_data_structures import Trie

# Initialize trie
trie = Trie()
trie_key = "my_trie"

# Insert words
trie.insert(trie_key, "hello")
trie.insert(trie_key, "help")
trie.insert(trie_key, "world")

# Search for words
exists = trie.search(trie_key, "hello")  # Returns True
not_exists = trie.search(trie_key, "hell")  # Returns False

# Find words with prefix
matches = trie.starts_with(trie_key, "hel")  # Returns ["hello", "help"]

# Delete words
trie.delete(trie_key, "hello")

# Get size
size = trie.size(trie_key)  # Returns 2

# Clear trie
trie.clear(trie_key)
```

## Advanced Usage

```python
from redis_data_structures import Trie
from typing import List, Set, Optional
from datetime import datetime
import json

class AutocompleteSystem:
    def __init__(self):
        self.trie = Trie()
        self.suggestions_key = "autocomplete"
    
    def add_phrase(self, phrase: str, metadata: Optional[dict] = None) -> bool:
        """Add a phrase to the autocomplete system."""
        success = self.trie.insert(self.suggestions_key, phrase.lower())
        if success and metadata:
            # Store metadata in a separate hash if needed
            meta_key = f"{self.suggestions_key}:meta:{phrase.lower()}"
            self.trie.connection_manager.execute(
                "hset",
                meta_key,
                "data",
                json.dumps({
                    **metadata,
                    "added_at": datetime.now().isoformat()
                })
            )
        return success
    
    def get_suggestions(
        self, 
        prefix: str, 
        max_results: int = 10
    ) -> List[dict]:
        """Get autocomplete suggestions for a prefix."""
        matches = self.trie.starts_with(self.suggestions_key, prefix.lower())
        suggestions = []
        
        for phrase in matches[:max_results]:
            suggestion = {"phrase": phrase}
            
            # Get metadata if exists
            meta_key = f"{self.suggestions_key}:meta:{phrase}"
            meta_data = self.trie.connection_manager.execute(
                "hget",
                meta_key,
                "data"
            )
            if meta_data:
                if isinstance(meta_data, bytes):
                    meta_data = meta_data.decode('utf-8')
                suggestion["metadata"] = json.loads(meta_data)
            
            suggestions.append(suggestion)
        
        return suggestions
    
    def remove_phrase(self, phrase: str) -> bool:
        """Remove a phrase from autocomplete."""
        success = self.trie.delete(self.suggestions_key, phrase.lower())
        if success:
            # Remove metadata
            meta_key = f"{self.suggestions_key}:meta:{phrase.lower()}"
            self.trie.connection_manager.execute("delete", meta_key)
        return success
    
    def clear_suggestions(self) -> bool:
        """Clear all suggestions."""
        # Clear metadata
        pattern = f"{self.suggestions_key}:meta:*"
        cursor = 0
        while True:
            cursor, keys = self.trie.connection_manager.execute(
                "scan",
                cursor,
                match=pattern
            )
            if keys:
                self.trie.connection_manager.execute("delete", *keys)
            if cursor == 0:
                break
                
        # Clear trie
        return self.trie.clear(self.suggestions_key)

# Usage
ac = AutocompleteSystem()

# Add phrases with metadata
ac.add_phrase("python programming", {
    "category": "programming",
    "popularity": 100
})
ac.add_phrase("python web development", {
    "category": "web",
    "popularity": 90
})

# Get suggestions
results = ac.get_suggestions("python")
```

## Example Use Cases

### 1. Spell Checker System

```python
from redis_data_structures import Trie
from typing import List, Set, Dict
import re

class SpellChecker:
    def __init__(self):
        self.trie = Trie()
        self.dictionary_key = "dictionary"
    
    def add_words(self, words: List[str]):
        """Add words to dictionary."""
        for word in words:
            self.trie.insert(self.dictionary_key, word.lower())
    
    def check_word(self, word: str) -> bool:
        """Check if word is spelled correctly."""
        return self.trie.search(self.dictionary_key, word.lower())
    
    def get_suggestions(self, word: str, max_distance: int = 2) -> List[str]:
        """Get spelling suggestions for a word."""
        word = word.lower()
        suggestions = set()
        
        # Check exact match
        if self.check_word(word):
            return [word]
            
        # Generate possible corrections
        for candidate in self._generate_candidates(word):
            if self.check_word(candidate):
                suggestions.add(candidate)
            
            # Check similar words with prefix
            if len(suggestions) < 5:  # Limit prefix search
                prefix = candidate[:3]  # Use first 3 chars as prefix
                similar = self.trie.starts_with(self.dictionary_key, prefix)
                for s in similar:
                    if self._edit_distance(word, s) <= max_distance:
                        suggestions.add(s)
        
        return sorted(list(suggestions))
    
    def _generate_candidates(self, word: str) -> Set[str]:
        """Generate possible corrections for a word."""
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        
        # Various possible corrections
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        
        return set(deletes + transposes + replaces + inserts)
    
    def _edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between strings."""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

# Usage
checker = SpellChecker()

# Add dictionary words
checker.add_words([
    "python", "programming", "computer", "algorithm",
    "development", "software", "engineer"
])

# Check spelling
is_correct = checker.check_word("python")  # True
suggestions = checker.get_suggestions("progam")  # ["program"]
```

### 2. Command Line Autocompletion

```python
from redis_data_structures import Trie
from typing import List, Dict, Optional
from datetime import datetime
import json

class CommandCompleter:
    def __init__(self):
        self.trie = Trie()
        self.commands_key = "cli_commands"
    
    def add_command(
        self, 
        command: str, 
        description: str, 
        usage: str,
        aliases: Optional[List[str]] = None
    ):
        """Add a command with metadata."""
        self.trie.insert(self.commands_key, command)
        
        # Store command metadata
        meta_key = f"{self.commands_key}:meta:{command}"
        metadata = {
            "description": description,
            "usage": usage,
            "added_at": datetime.now().isoformat(),
            "aliases": aliases or []
        }
        self.trie.connection_manager.execute(
            "set",
            meta_key,
            json.dumps(metadata)
        )
        
        # Add aliases
        if aliases:
            for alias in aliases:
                self.trie.insert(self.commands_key, alias)
                alias_key = f"{self.commands_key}:meta:{alias}"
                self.trie.connection_manager.execute(
                    "set",
                    alias_key,
                    json.dumps({**metadata, "is_alias": True})
                )
    
    def get_completions(
        self, 
        partial: str
    ) -> List[Dict[str, str]]:
        """Get command completions with metadata."""
        matches = self.trie.starts_with(self.commands_key, partial)
        completions = []
        
        for command in matches:
            meta_key = f"{self.commands_key}:meta:{command}"
            meta_data = self.trie.connection_manager.execute("get", meta_key)
            
            if meta_data:
                if isinstance(meta_data, bytes):
                    meta_data = meta_data.decode('utf-8')
                metadata = json.loads(meta_data)
                completions.append({
                    "command": command,
                    **metadata
                })
        
        return completions
    
    def get_command_help(self, command: str) -> Optional[Dict[str, str]]:
        """Get detailed help for a command."""
        if not self.trie.search(self.commands_key, command):
            return None
            
        meta_key = f"{self.commands_key}:meta:{command}"
        meta_data = self.trie.connection_manager.execute("get", meta_key)
        
        if meta_data:
            if isinstance(meta_data, bytes):
                meta_data = meta_data.decode('utf-8')
            return json.loads(meta_data)
        return None

# Usage
cli = CommandCompleter()

# Add commands
cli.add_command(
    "git-clone",
    "Clone a repository into a new directory",
    "git clone <repository> [<directory>]",
    aliases=["clone"]
)
cli.add_command(
    "git-commit",
    "Record changes to the repository",
    "git commit -m <message>",
    aliases=["commit"]
)

# Get completions
completions = cli.get_completions("git-")

# Get help
help_info = cli.get_command_help("git-clone")
```

### 3. URL Router System

```python
from redis_data_structures import Trie
from typing import Dict, Any, Optional, Callable
import re
from datetime import datetime
import json

class URLRouter:
    def __init__(self):
        self.trie = Trie()
        self.routes_key = "url_routes"
    
    def add_route(
        self, 
        path: str, 
        handler_name: str,
        methods: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a URL route with metadata."""
        # Normalize path
        path = self._normalize_path(path)
        self.trie.insert(self.routes_key, path)
        
        # Store route metadata
        meta_key = f"{self.routes_key}:meta:{path}"
        route_data = {
            "handler": handler_name,
            "methods": methods or ["GET"],
            "pattern": self._path_to_pattern(path),
            "added_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.trie.connection_manager.execute(
            "set",
            meta_key,
            json.dumps(route_data)
        )
    
    def match_route(self, path: str, method: str = "GET") -> Optional[Dict[str, Any]]:
        """Match a URL path to a route."""
        path = self._normalize_path(path)
        
        # Check exact match first
        if self.trie.search(self.routes_key, path):
            return self._get_route_data(path, method)
        
        # Check pattern matches
        possible_routes = self.trie.get_all_words(self.routes_key)
        for route in possible_routes:
            route_data = self._get_route_data(route, method)
            if route_data and "pattern" in route_data:
                pattern = route_data["pattern"]
                if re.match(pattern, path):
                    params = self._extract_params(pattern, path)
                    return {
                        **route_data,
                        "params": params
                    }
        
        return None
    
    def _normalize_path(self, path: str) -> str:
        """Normalize URL path."""
        path = path.strip().lower()
        return path if path.startswith("/") else f"/{path}"
    
    def _path_to_pattern(self, path: str) -> str:
        """Convert URL path to regex pattern."""
        # Convert path params to regex groups
        pattern = re.sub(r":(\w+)", r"(?P<\1>[^/]+)", path)
        # Convert wildcards
        pattern = pattern.replace("*", r"[^/]+")
        return f"^{pattern}$"
    
    def _get_route_data(
        self, 
        path: str, 
        method: str
    ) -> Optional[Dict[str, Any]]:
        """Get route data if method is allowed."""
        meta_key = f"{self.routes_key}:meta:{path}"
        data = self.trie.connection_manager.execute