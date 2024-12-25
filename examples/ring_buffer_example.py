import time

from redis_data_structures import RingBuffer


def demonstrate_log_rotation():
    """Demonstrate ring buffer functionality with log rotation."""
    # Initialize buffer for log rotation
    buffer = RingBuffer("logs", capacity=5)

    # Clear any existing data
    buffer.clear()

    print("=== Log Rotation Example ===")

    # Add some log entries
    print("\nAdding log entries...")
    logs = [
        {"level": "INFO", "message": "Application started", "timestamp": "2024-01-01T10:00:00"},
        {"level": "DEBUG", "message": "Processing request", "timestamp": "2024-01-01T10:00:01"},
        {"level": "ERROR", "message": "Connection failed", "timestamp": "2024-01-01T10:00:02"},
        {"level": "INFO", "message": "Retrying connection", "timestamp": "2024-01-01T10:00:03"},
        {"level": "INFO", "message": "Connection restored", "timestamp": "2024-01-01T10:00:04"},
    ]

    for log in logs:
        if buffer.push(log):
            print(f"Added log: [{log['level']}] {log['message']}")
        else:
            print(f"Failed to add log: [{log['level']}] {log['message']}")

    # Show all logs
    print("\nAll logs in buffer:")
    all_logs = buffer.get_all()
    for log in all_logs:
        print(f"[{log['level']}] {log['message']} at {log['timestamp']}")

    # Add one more log (should cause rotation)
    new_log = {"level": "WARN", "message": "High memory usage", "timestamp": "2024-01-01T10:00:05"}
    print("\nAdding one more log (should rotate out oldest)...")
    if buffer.push(new_log):
        print(f"Added log: [{new_log['level']}] {new_log['message']}")
    else:
        print(f"Failed to add log: [{new_log['level']}] {new_log['message']}")

    # Show latest logs
    print("\nLatest 3 logs:")
    latest = buffer.get_latest(3)
    for log in latest:
        print(f"[{log['level']}] {log['message']} at {log['timestamp']}")


def demonstrate_metrics_collection():
    """Demonstrate ring buffer functionality with system metrics collection."""
    # Initialize buffer for system metrics
    buffer = RingBuffer("metrics", capacity=10)

    # Clear any existing data
    buffer.clear()

    print("\n=== System Metrics Example ===")

    # Simulate collecting metrics over time
    print("\nCollecting system metrics...")
    for i in range(12):  # Collect more than capacity to show rotation
        metrics = {
            "timestamp": time.time(),
            "cpu_usage": 40 + i * 5,  # Simulated increasing CPU usage
            "memory_usage": 60 + i * 2,  # Simulated increasing memory usage
            "io_usage": 30 + i * 3,  # Simulated increasing I/O usage
        }
        if buffer.push(metrics):
            print(
                f"Recorded metrics: CPU: {metrics['cpu_usage']}%, "
                f"Memory: {metrics['memory_usage']}%, "
                f"I/O: {metrics['io_usage']}%",
            )
        else:
            print("Failed to record metrics")
        time.sleep(0.5)  # Simulate time passing

    # Show latest metrics
    print("\nLatest 5 metrics readings:")
    latest = buffer.get_latest(5)
    for metrics in latest:
        print(
            f"CPU: {metrics['cpu_usage']}%, "
            f"Memory: {metrics['memory_usage']}%, "
            f"I/O: {metrics['io_usage']}%",
        )


def demonstrate_sliding_window():
    """Demonstrate ring buffer functionality with price tracking."""
    # Initialize buffer for price tracking
    buffer = RingBuffer("prices", capacity=5)

    # Clear any existing data
    buffer.clear()

    print("\n=== Price Tracking Example ===")

    # Simulate price updates
    print("\nTracking price updates...")
    prices = [
        {"timestamp": "2024-01-01T10:00:00", "price": 100.00},
        {"timestamp": "2024-01-01T10:00:01", "price": 101.50},
        {"timestamp": "2024-01-01T10:00:02", "price": 99.75},
        {"timestamp": "2024-01-01T10:00:03", "price": 102.25},
        {"timestamp": "2024-01-01T10:00:04", "price": 103.00},
    ]

    for update in prices:
        if buffer.push(update):
            print(f"Price update: ${update['price']} at {update['timestamp']}")
        else:
            print(f"Failed to update price: ${update['price']}")

    # Calculate average over window
    all_prices = buffer.get_all()
    avg_price = sum(update["price"] for update in all_prices) / len(all_prices)
    print(f"\nAverage price over window: ${avg_price:.2f}")

    # Add new price (should rotate out oldest)
    new_price = {"timestamp": "2024-01-01T10:00:05", "price": 104.50}
    print(f"\nNew price update: ${new_price['price']}")
    if buffer.push(new_price):
        print("Price update successful")
    else:
        print("Failed to update price")

    # Show latest prices
    print("\nLatest 3 prices:")
    latest = buffer.get_latest(3)
    for update in latest:
        print(f"${update['price']} at {update['timestamp']}")


if __name__ == "__main__":
    demonstrate_log_rotation()
    demonstrate_metrics_collection()
    demonstrate_sliding_window()
