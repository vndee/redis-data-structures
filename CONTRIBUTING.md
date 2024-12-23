# Contributing to Redis Data Structures

First off, thank you for considering contributing to Redis Data Structures! It's people like you that make Redis Data Structures such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [project maintainers](mailto:maintainers@example.com).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include details about your configuration and environment

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Development Process

1. Clone the repository
   ```bash
   git clone https://github.com/vndee/redis-data-structures.git
   cd redis-data-structures
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Run tests
   ```bash
   pytest
   ```

### Code Style

We use [Black](https://github.com/psf/black) for code formatting and [isort](https://pycqa.github.io/isort/) for import sorting:

```bash
# Format code
black .

# Sort imports
isort .
```

### Type Hints

We use type hints throughout the codebase. Please ensure your code includes appropriate type hints:

```python
from typing import Optional, List

def process_items(items: List[str], count: Optional[int] = None) -> List[str]:
    if count is None:
        return items
    return items[:count]
```

### Documentation

* Use docstrings for all public modules, functions, classes, and methods
* Follow Google style for docstrings
* Include examples in docstrings when appropriate

Example:
```python
def push(self, key: str, value: Any) -> None:
    """Push an item to the queue.

    Args:
        key: The queue identifier
        value: The value to push

    Raises:
        RedisError: If the Redis operation fails
        ValueError: If the key is empty

    Example:
        >>> queue = Queue(host='localhost', port=6379)
        >>> queue.push('my_queue', 'item1')
    """
```

### Testing

* Write tests for all new features
* Maintain or increase test coverage
* Run the full test suite before submitting pull requests

```bash
# Run tests with coverage
pytest --cov=redis_data_structures tests/

# Run specific test file
pytest tests/test_queue.py
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Example:
```
Add TTL support for Queue data structure

- Implement set_ttl and get_ttl methods
- Add tests for TTL functionality
- Update documentation with TTL examples

Fixes #123
```

## Project Structure

```
redis_data_structures/
├── __init__.py
├── base.py           # Base classes and utilities
├── queue.py         # Queue implementation
├── stack.py         # Stack implementation
├── priority_queue.py # Priority Queue implementation
├── set.py           # Set implementation
├── hash_map.py      # Hash Map implementation
├── deque.py         # Deque implementation
├── bloom_filter.py  # Bloom Filter implementation
├── trie.py         # Trie implementation
└── lru_cache.py    # LRU Cache implementation

tests/
├── __init__.py
├── conftest.py      # Test configurations
├── test_queue.py
├── test_stack.py
└── ...
```

## Release Process

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. GitHub Actions will automatically publish to PyPI

## Questions?

Feel free to open an issue with the tag `question` if you have any questions about contributing.

Thank you for your contributions! 🎉 