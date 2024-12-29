import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue as PyQueue
from typing import Any, Dict, List, Set

import pytest

from redis_data_structures import Queue


@pytest.fixture
def queue() -> Queue:
    """Create a Queue instance for testing."""
    q = Queue(key="test_queue")
    q.clear()
    yield q
    q.clear()


def test_concurrent_push(queue):
    """Test concurrent push operations."""
    num_threads = 4
    items_per_thread = 25
    expected_total = num_threads * items_per_thread

    def push_items(thread_id: int):
        for i in range(items_per_thread):
            data = f"item_{thread_id}_{i}"
            assert queue.push(data)

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=push_items, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert queue.size() == expected_total


def test_concurrent_push_pop(queue):
    """Test concurrent push and pop operations."""
    results = PyQueue()  # Thread-safe queue to collect results
    num_items = 100

    def producer():
        for i in range(num_items):
            assert queue.push(f"item_{i}")
            time.sleep(0.001)  # Small delay to ensure interleaving

    def consumer():
        items_consumed = 0
        while items_consumed < num_items:
            item = queue.pop()
            if item is not None:
                results.put(item)
                items_consumed += 1
            time.sleep(0.001)  # Small delay to ensure interleaving

    producer_thread = threading.Thread(target=producer)
    consumer_thread = threading.Thread(target=consumer)

    producer_thread.start()
    consumer_thread.start()

    producer_thread.join()
    consumer_thread.join()

    # Verify all items were processed
    assert results.qsize() == num_items
    assert queue.size() == 0


def test_concurrent_peek(queue):
    """Test concurrent peek operations."""
    queue.push("stable_item")

    def peek_operation() -> str:
        return queue.peek()

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(peek_operation) for _ in range(10)]
        results = [f.result() for f in as_completed(futures)]

    # All peeks should return the same value
    assert all(result == "stable_item" for result in results)
    assert queue.size() == 1  # Size should remain unchanged


def test_concurrent_size_check(queue):
    """Test concurrent size operations with modifications."""

    def size_and_modify():
        initial_size = queue.size()
        queue.push(f"item_{threading.get_ident()}")
        after_push_size = queue.size()
        assert after_push_size == initial_size + 1

    threads = []
    for _ in range(4):
        t = threading.Thread(target=size_and_modify)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert queue.size() == 4


def test_concurrent_clear(queue):
    """Test concurrent clear operations."""
    # Fill queue with some items
    for i in range(10):
        queue.push(f"item_{i}")

    def clear_and_check():
        queue.clear()
        assert queue.size() >= 0  # Size should always be valid

    threads = []
    for _ in range(4):
        t = threading.Thread(target=clear_and_check)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert queue.size() == 0


def test_concurrent_mixed_operations(queue):
    """Test mixed operations happening concurrently."""
    operation_count = 100
    results: Set[str] = set()

    def mixed_operations(thread_id: int):
        local_results = []
        for i in range(operation_count):
            # Push operation
            queue.push(f"item_{thread_id}_{i}")

            # Peek operation
            peeked = queue.peek()
            if peeked:
                local_results.append(f"peeked_{peeked}")

            # Pop operation
            popped = queue.pop()
            if popped:
                local_results.append(f"popped_{popped}")

            # Size check
            size = queue.size()
            assert size >= 0

        return local_results

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(mixed_operations, i) for i in range(4)]
        for future in as_completed(futures):
            results.update(future.result())

    # Verify we got results from our operations
    assert len(results) > 0
    assert queue.size() >= 0


def test_concurrent_error_handling(queue):
    """Test error handling during concurrent operations."""

    def push_invalid_data():
        try:
            queue.push(lambda x: x)  # Functions can't be serialized
            pytest.fail("Should have raised an exception")
        except Exception:
            pass

    threads = []
    for _ in range(4):
        t = threading.Thread(target=push_invalid_data)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Queue should still be usable
    assert queue.push("valid_item")
    assert queue.pop() == "valid_item"


def test_pop_from_empty_queue(queue):
    """Test pop from an empty queue."""
    assert queue.pop() is None


def test_generic_type_inference(queue):
    """Test generic type inference."""
    queue = Queue[Dict[str, Any]]("task_queue")
    assert queue.push({"key": "value"})
    assert queue.pop() == {"key": "value"}

    queue = Queue[List[int]]("number_queue")
    assert queue.push([1, 2, 3])
    assert queue.pop() == [1, 2, 3]
