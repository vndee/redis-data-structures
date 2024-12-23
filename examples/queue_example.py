import time

from redis_data_structures import Queue


def demonstrate_queue():
    # Initialize queue
    queue = Queue(host="localhost", port=6379, db=0)
    queue_key = "task_queue"

    # Clear any existing data
    queue.clear(queue_key)

    print("=== Queue Example (FIFO) ===")

    # Simulating task queue
    print("\nAdding tasks to queue...")
    tasks = ["Process user registration", "Send welcome email", "Generate user report"]

    for task in tasks:
        queue.push(queue_key, task)
        print(f"Added task: {task}")

    print(f"\nQueue size: {queue.size(queue_key)}")

    # Processing tasks
    print("\nProcessing tasks...")
    while queue.size(queue_key) > 0:
        task = queue.pop(queue_key)
        print(f"Processing task: {task}")
        time.sleep(1)  # Simulate processing time

    print("\nAll tasks processed!")


if __name__ == "__main__":
    demonstrate_queue()
