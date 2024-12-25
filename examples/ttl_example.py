"""Example demonstrating TTL (Time To Live) functionality."""

import time
from datetime import datetime, timedelta, timezone

from redis_data_structures.base import RedisDataStructure
from redis_data_structures.logging import setup_logging

# Set up logging
logger = setup_logging()


def demonstrate_ttl():
    print("=== TTL (Time To Live) Example ===\n")

    # Initialize Redis structure
    redis_ds = RedisDataStructure(key="test_ttl")

    # Example 1: Basic TTL with seconds
    print("1. Setting key with 5-second TTL...")
    key = "temp_key"
    redis_ds.connection_manager.execute("set", key, "temporary value")
    redis_ds.set_ttl(key, 5)

    # Check TTL
    ttl = redis_ds.get_ttl(key)
    print(f"TTL remaining: {ttl} seconds")

    # Wait and check if key exists
    print("Waiting 6 seconds...")
    time.sleep(6)
    exists = redis_ds.connection_manager.execute("exists", key)
    print(f"Key exists after TTL: {exists}\n")

    # Example 2: Using timedelta
    print("2. Setting key with timedelta TTL...")
    key = "delta_key"
    redis_ds.connection_manager.execute("set", key, "delta value")
    redis_ds.set_ttl(key, timedelta(seconds=10))

    ttl = redis_ds.get_ttl(key)
    print(f"TTL remaining: {ttl} seconds")
    print("Key will expire in 10 seconds\n")

    # Example 3: Setting expiration at specific time
    print("3. Setting key with future timestamp...")
    key = "future_key"
    redis_ds.connection_manager.execute("set", key, "future value")

    # Set to expire in 15 seconds from now
    future_time = datetime.now(timezone.utc) + timedelta(seconds=15)
    redis_ds.set_ttl(key, future_time)

    ttl = redis_ds.get_ttl(key)
    print(f"TTL remaining: {ttl} seconds")
    print(f"Key will expire at: {future_time}\n")

    # Example 4: Making a temporary key persistent
    print("4. Making temporary key persistent...")
    key = "persist_key"
    redis_ds.connection_manager.execute("set", key, "temporary value")
    redis_ds.set_ttl(key, 30)

    print("Before persist:")
    ttl = redis_ds.get_ttl(key)
    print(f"TTL remaining: {ttl} seconds")

    # Remove TTL
    redis_ds.persist(key)

    print("\nAfter persist:")
    ttl = redis_ds.get_ttl(key)
    print(f"TTL remaining: {ttl} (-1 means no expiration)\n")

    # Example 5: Checking non-existent key
    print("5. Checking non-existent key...")
    key = "nonexistent_key"
    ttl = redis_ds.get_ttl(key)
    print(f"TTL for non-existent key: {ttl} (-2 means key doesn't exist)")


def demonstrate_ttl_with_data_structures():
    print("\n=== TTL with Different Data Structures ===\n")

    redis_ds = RedisDataStructure(key="test_ttl")

    # Example with Hash
    print("1. Hash with TTL...")
    hash_key = "user:123"
    redis_ds.connection_manager.execute(
        "hset",
        hash_key,
        mapping={"name": "John Doe", "email": "john@example.com"},
    )
    redis_ds.set_ttl(hash_key, 5)

    print("Hash TTL:", redis_ds.get_ttl(hash_key))
    print("Waiting for expiration...")
    time.sleep(6)
    print(f"Hash exists: {redis_ds.connection_manager.execute('exists', hash_key)}\n")

    # Example with Set
    print("2. Set with TTL...")
    set_key = "active_users"
    redis_ds.connection_manager.execute("sadd", set_key, "user1", "user2", "user3")
    future_time = datetime.now(timezone.utc) + timedelta(seconds=8)
    redis_ds.set_ttl(set_key, 8)

    print("Set TTL:", redis_ds.get_ttl(set_key))
    print(f"Set will expire at: {future_time}")


if __name__ == "__main__":
    demonstrate_ttl()
    demonstrate_ttl_with_data_structures()
