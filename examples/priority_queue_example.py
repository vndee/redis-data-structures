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
    pq = PriorityQueue("task_scheduler", host="localhost", port=6379, db=0)

    # Clear any existing data
    pq.clear()

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
        if pq.push(task, priority):
            print(f"Added task: {task} (Priority: {Priority(priority).name})")
        else:
            print(f"Failed to add task: {task}")

    print(f"\nTotal tasks in queue: {pq.size()}")

    # Peek at highest priority task
    print("\nPeeking at highest priority task...")
    peek_result = pq.peek()
    if peek_result:
        task, priority = peek_result
        print(f"Next task to process: {task} (Priority: {Priority(priority).name})")
    else:
        print("No tasks in queue")

    # Get all tasks in priority order
    print("\nAll tasks in priority order:")
    all_tasks = pq.get_all()
    for task, priority in all_tasks:
        print(f"- {task} (Priority: {Priority(priority).name})")

    # Process tasks by priority
    print("\nProcessing tasks in priority order...")
    while pq.size() > 0:
        result = pq.pop()
        if result:
            task, priority = result
            print(f"Processing: {task} (Priority: {Priority(priority).name})")
        else:
            print("Error processing task")

    # Verify queue is empty
    print(f"\nRemaining tasks in queue: {pq.size()}")


if __name__ == "__main__":
    demonstrate_priority_queue()
