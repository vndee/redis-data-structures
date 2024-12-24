from enum import IntEnum

from redis_data_structures import PriorityQueue


class Priority(IntEnum):
    """Priority levels for tasks."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


def demonstrate_priority_queue():
    """Demonstrate priority queue functionality with a task scheduling system."""
    # Initialize priority queue
    pq = PriorityQueue(host="localhost", port=6379, db=0)
    queue_key = "task_scheduler"

    # Clear any existing data
    pq.clear(queue_key)

    print("=== Priority Queue Example ===")

    # Simulating a task scheduling system
    print("\nAdding tasks with different priorities...")
    tasks = [
        ("Deploy critical security patch", Priority.CRITICAL),
        ("Optimize database queries", Priority.HIGH),
        ("Update documentation", Priority.LOW),
        ("Fix UI bug", Priority.MEDIUM),
        ("Backup database", Priority.HIGH),
    ]

    # Add tasks to queue
    for task, priority in tasks:
        if pq.push(queue_key, task, priority):
            print(f"Added task: {task} (Priority: {Priority(priority).name})")
        else:
            print(f"Failed to add task: {task}")

    print(f"\nTotal tasks in queue: {pq.size(queue_key)}")

    # Peek at highest priority task
    print("\nPeeking at highest priority task...")
    peek_result = pq.peek(queue_key)
    if peek_result:
        task, priority = peek_result
        print(f"Next task to process: {task} (Priority: {Priority(priority).name})")
    else:
        print("No tasks in queue")

    # Get all tasks in priority order
    print("\nAll tasks in priority order:")
    all_tasks = pq.get_all(queue_key)
    for task, priority in all_tasks:
        print(f"- {task} (Priority: {Priority(priority).name})")

    # Process tasks by priority
    print("\nProcessing tasks in priority order...")
    while pq.size(queue_key) > 0:
        result = pq.pop(queue_key)
        if result:
            task, priority = result
            print(f"Processing: {task} (Priority: {Priority(priority).name})")
        else:
            print("Error processing task")

    # Verify queue is empty
    print(f"\nRemaining tasks in queue: {pq.size(queue_key)}")


if __name__ == "__main__":
    demonstrate_priority_queue()
