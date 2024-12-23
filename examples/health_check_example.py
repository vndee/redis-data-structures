"""Example demonstrating Redis health check functionality."""

from redis_data_structures.health import check_redis_connection, get_redis_metrics
from redis_data_structures.logging import setup_logging

# Set up logging
logger = setup_logging()


def demonstrate_health_check():
    print("=== Redis Health Check Example ===\n")

    # Check connection health
    print("Checking Redis connection...")
    is_healthy, message = check_redis_connection()
    print(f"Health status: {'✓' if is_healthy else '✗'}")
    print(f"Message: {message}\n")

    if is_healthy:
        # Get Redis metrics
        print("Fetching Redis metrics...")
        metrics = get_redis_metrics()

        print("\nRedis Server Information:")
        print("-" * 30)
        for key, value in metrics.items():
            print(f"{key.replace('_', ' ').title()}: {value}")


if __name__ == "__main__":
    demonstrate_health_check()
