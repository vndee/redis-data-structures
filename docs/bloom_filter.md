# Bloom Filter

A Redis-backed Bloom filter implementation that provides probabilistic set membership testing with a configurable false positive rate. Perfect for blacklists, content filtering, and deduplication scenarios where space efficiency is crucial and false positives are acceptable.

## Features

| Feature | Average Cost | Worst Case | Description | Implementation |
| --- | --- | --- | --- | --- |
| `add` | $O(k)$ | $O(k)$ | Add an item to the filter | `SETBIT` (k times) |
| `contains` | $O(k)$ | $O(k)$ | Check if an item might exist in the filter | `GETBIT` (k times) |
| `clear` | $O(1)$ | $O(1)$ | Remove all items from the filter | `DELETE` |
| `size` | $O(1)$ | $O(1)$ | Return the size of the filter in bits | Calculated |

where k is the number of hash functions used (automatically optimized based on the expected number of elements and desired false positive rate)

## Basic Usage

```python
from redis_data_structures import BloomFilter

# Initialize Bloom filter with custom parameters
bf = BloomFilter(
    expected_elements=1000,  # Expect to store ~1000 elements
    false_positive_rate=0.01  # 1% false positive rate
)

filter_key = "email_blacklist"

# Add items to the filter
bf.add(filter_key, "spam@example.com")
bf.add(filter_key, "malicious@example.com")

# Check if items exist
is_spam = bf.contains(filter_key, "spam@example.com")  # Returns True
is_safe = bf.contains(filter_key, "legitimate@example.com")  # Likely returns False

# Clear the filter
bf.clear(filter_key)

# Get filter size in bits
size = bf.size()
```

## Advanced Usage

```python
from redis_data_structures import BloomFilter
from typing import List, Set
import json

class DuplicateDetector:
    def __init__(self, expected_items: int = 10000):
        self.bloom = BloomFilter(
            expected_elements=expected_items,
            false_positive_rate=0.001  # 0.1% false positive rate for higher accuracy
        )
        self.filter_key = "seen_items"
    
    def is_duplicate(self, item: any) -> bool:
        """Check if item might be a duplicate."""
        # Convert complex objects to JSON for consistent hashing
        if not isinstance(item, (str, int, float, bool)):
            item = json.dumps(item, sort_keys=True)
            
        return self.bloom.contains(self.filter_key, item)
    
    def mark_seen(self, item: any) -> None:
        """Mark item as seen."""
        if not isinstance(item, (str, int, float, bool)):
            item = json.dumps(item, sort_keys=True)
            
        self.bloom.add(self.filter_key, item)
    
    def process_items(self, items: List[any]) -> Set[any]:
        """Process items and return unique ones."""
        unique_items = set()
        
        for item in items:
            if not self.is_duplicate(item):
                unique_items.add(item)
                self.mark_seen(item)
                
        return unique_items
```

## Example Use Cases

### 1. URL Deduplication in Web Crawler

```python
from redis_data_structures import BloomFilter
from urllib.parse import urlparse
from typing import Set

class URLDeduplicator:
    def __init__(self, expected_urls: int = 1000000):
        self.bloom = BloomFilter(
            expected_elements=expected_urls,
            false_positive_rate=0.001
        )
        self.filter_key = "crawled_urls"
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for consistent checking."""
        parsed = urlparse(url.lower())
        return f"{parsed.netloc}{parsed.path}"
    
    def is_crawled(self, url: str) -> bool:
        """Check if URL has been crawled."""
        normalized = self.normalize_url(url)
        return self.bloom.contains(self.filter_key, normalized)
    
    def mark_crawled(self, url: str) -> None:
        """Mark URL as crawled."""
        normalized = self.normalize_url(url)
        self.bloom.add(self.filter_key, normalized)
    
    def filter_urls(self, urls: Set[str]) -> Set[str]:
        """Filter out previously crawled URLs."""
        return {url for url in urls if not self.is_crawled(url)}

# Usage
deduplicator = URLDeduplicator()
urls_to_crawl = {
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page1"  # Duplicate
}

new_urls = deduplicator.filter_urls(urls_to_crawl)
for url in new_urls:
    # Crawl the URL
    deduplicator.mark_crawled(url)
```

### 2. User Activity Tracker

```python
from redis_data_structures import BloomFilter
from datetime import datetime, timedelta

class UserActivityTracker:
    def __init__(self, expected_users: int = 100000):
        self.bloom = BloomFilter(
            expected_elements=expected_users,
            false_positive_rate=0.01
        )
    
    def get_daily_key(self, date: datetime) -> str:
        """Get Redis key for specific date."""
        return f"user_activity:{date.strftime('%Y-%m-%d')}"
    
    def record_activity(self, user_id: str, activity_type: str):
        """Record user activity for today."""
        key = self.get_daily_key(datetime.now())
        activity_signature = f"{user_id}:{activity_type}"
        self.bloom.add(key, activity_signature)
    
    def has_activity_today(self, user_id: str, activity_type: str) -> bool:
        """Check if user has performed activity today."""
        key = self.get_daily_key(datetime.now())
        activity_signature = f"{user_id}:{activity_type}"
        return self.bloom.contains(key, activity_signature)
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up activity data older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        current = cutoff_date
        
        while current < datetime.now():
            key = self.get_daily_key(current)
            self.bloom.clear(key)
            current += timedelta(days=1)

# Usage
tracker = UserActivityTracker()

# Record user activities
tracker.record_activity("user123", "login")
tracker.record_activity("user123", "search")

# Check activities
has_logged_in = tracker.has_activity_today("user123", "login")  # True
has_purchased = tracker.has_activity_today("user123", "purchase")  # False

# Clean up old data
tracker.cleanup_old_data(days_to_keep=7)
```

### 3. Content Filtering System

```python
from redis_data_structures import BloomFilter
import hashlib
from typing import List, Set

class ContentFilter:
    def __init__(self, expected_patterns: int = 10000):
        self.bloom = BloomFilter(
            expected_elements=expected_patterns,
            false_positive_rate=0.0001  # Very low false positive rate for content filtering
        )
        self.filter_key = "content_patterns"
    
    def generate_patterns(self, content: str, pattern_length: int = 4) -> Set[str]:
        """Generate n-gram patterns from content."""
        content = content.lower()
        return {
            content[i:i+pattern_length] 
            for i in range(len(content) - pattern_length + 1)
        }
    
    def add_inappropriate_content(self, content: str):
        """Add inappropriate content patterns to filter."""
        patterns = self.generate_patterns(content)
        for pattern in patterns:
            self.bloom.add(self.filter_key, pattern)
    
    def is_inappropriate(self, content: str, threshold: float = 0.1) -> bool:
        """Check if content might be inappropriate."""
        patterns = self.generate_patterns(content)
        if not patterns:
            return False
            
        matches = sum(1 for p in patterns if self.bloom.contains(self.filter_key, p))
        return (matches / len(patterns)) > threshold
    
    def add_batch_content(self, content_list: List[str]):
        """Add multiple pieces of inappropriate content."""
        for content in content_list:
            self.add_inappropriate_content(content)

# Usage
content_filter = ContentFilter()

# Add inappropriate patterns
inappropriate_content = [
    "inappropriate_word1",
    "inappropriate_word2",
    "bad_pattern"
]
content_filter.add_batch_content(inappropriate_content)

# Check content
text = "This is some user-generated content"
if content_filter.is_inappropriate(text):
    print("Content flagged for review")
else:
    print("Content appears safe")
```