import argparse
import time
from typing import Any

from redis_data_structures import PriorityQueue


class TaskProducer:
    """Producer of tasks for the priority queue."""

    def __init__(self, queue: PriorityQueue):
        """Initialize the TaskProducer."""
        self.queue = queue

    def produce(self, task_type: str, data: Any, priority: int):
        """Produce a new task and add it to the priority queue."""
        task = {"type": task_type, "data": data}
        self.queue.push(task, priority=priority)
        print(f"Produced task: {task} with priority {priority}")


class TaskConsumer:
    """Consumer of tasks from the priority queue."""

    def __init__(self, queue: PriorityQueue):
        """Initialize the TaskConsumer."""
        self.queue = queue

    def consume(self):
        """Consume tasks from the priority queue."""
        print("Consuming tasks...")
        while True:
            task = self.queue.pop()
            if task:
                data, priority = task
                print(f"Consumed task: {data['type']} with priority {priority}")

            time.sleep(0.25)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Priority Queue Producer-Consumer Example")
    parser.add_argument("--producer", action="store_true", help="Run the producer")
    parser.add_argument("--consumer", action="store_true", help="Run the consumer")
    args = parser.parse_args()

    if not args.producer and not args.consumer:
        print("Please specify either --producer or --consumer")
        parser.print_help()
        exit(1)

    pq = PriorityQueue("task_queue")

    if args.producer:
        # Create producer and consumer
        producer = TaskProducer(pq)

        # Produce some tasks
        producer.produce("task1", {"info": "data1"}, priority=2)
        producer.produce("task2", {"info": "data2"}, priority=1)
        producer.produce("task3", {"info": "data3"}, priority=3)

    if args.consumer:
        consumer = TaskConsumer(pq)
        consumer.consume()
