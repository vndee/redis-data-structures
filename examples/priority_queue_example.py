from redis_data_structures import PriorityQueue


def demonstrate_priority_queue():
    # Initialize priority queue
    pq = PriorityQueue(host="localhost", port=6379, db=0)
    pq_key = "support_tickets"

    # Clear any existing data
    pq.clear(pq_key)

    print("=== Priority Queue Example ===")

    # Simulating support ticket system
    print("\nAdding support tickets...")
    tickets = [
        ("System down", 1),  # Critical priority
        ("Feature request", 3),  # Low priority
        ("Bug in payment", 2),  # High priority
        ("UI improvement", 3),  # Low priority
        ("Security issue", 1),  # Critical priority
    ]

    for ticket, priority in tickets:
        pq.push(pq_key, ticket, priority)
        priority_label = {1: "Critical", 2: "High", 3: "Low"}
        print(f"Added ticket: {ticket} (Priority: {priority_label[priority]})")

    print(f"\nQueue size: {pq.size(pq_key)}")

    # Processing tickets by priority
    print("\nProcessing tickets by priority...")
    while pq.size(pq_key) > 0:
        ticket, priority = pq.pop(pq_key)
        priority_label = {1: "Critical", 2: "High", 3: "Low"}
        print(f"Processing {priority_label[priority]} priority ticket: {ticket}")


if __name__ == "__main__":
    demonstrate_priority_queue()
