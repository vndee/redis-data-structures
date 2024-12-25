import time
from typing import Any, Dict

from redis_data_structures import Queue


def demonstrate_queue():
    """Demonstrate queue functionality with a task processing system."""
    # Initialize queue
    queue = Queue("task_queue")

    # Clear any existing data
    queue.clear()

    print("=== Queue Example (FIFO) ===")

    # Simulating task queue
    print("\nAdding tasks to queue...")
    tasks = [
        {"type": "user", "action": "registration", "data": {"email": "user@example.com"}},
        {"type": "email", "action": "welcome", "data": {"template": "welcome_email"}},
        {"type": "report", "action": "generate", "data": {"format": "pdf"}},
    ]

    for task in tasks:
        if queue.push(task):
            print(f"Added task: {task['type']}_{task['action']}")
        else:
            print(f"Failed to add task: {task['type']}_{task['action']}")

    print(f"\nQueue size: {queue.size()}")

    # Peek at next task
    print("\nPeeking at next task...")
    next_task = queue.peek()
    if next_task:
        print(f"Next task to process: {next_task['type']}_{next_task['action']}")
    else:
        print("No tasks in queue")

    # Processing tasks
    print("\nProcessing tasks...")
    while queue.size() > 0:
        task = queue.pop()
        if task:
            print(f"Processing: {task['type']}_{task['action']}")
            process_task(task)
        else:
            print("Error retrieving task")

    print("\nAll tasks processed!")


def process_task(task: Dict[str, Any]):
    """Simulate task processing."""
    if task["type"] == "user" and task["action"] == "registration":
        print("  - Creating user account...")
        print("  - Setting up user preferences...")
    elif task["type"] == "email" and task["action"] == "welcome":
        print("  - Generating welcome email from template...")
        print("  - Sending email...")
    elif task["type"] == "report" and task["action"] == "generate":
        print("  - Collecting report data...")
        print("  - Generating PDF report...")
    time.sleep(1)  # Simulate processing time


if __name__ == "__main__":
    demonstrate_queue()
