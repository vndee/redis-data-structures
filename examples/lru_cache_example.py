from redis_data_structures import LRUCache


def demonstrate_lru_cache():
    """Demonstrate LRU cache functionality with a simulated database cache."""
    # Initialize LRU cache with capacity of 3
    cache = LRUCache(capacity=3, key="user_cache")

    # Clear any existing data
    cache.clear()

    print("=== LRU Cache Example ===")

    # Simulating database queries and caching
    print("\nCaching user data...")
    users = [
        ("user1", {"name": "John Doe", "email": "john@example.com"}),
        ("user2", {"name": "Jane Smith", "email": "jane@example.com"}),
        ("user3", {"name": "Bob Wilson", "email": "bob@example.com"}),
    ]

    # Add users to cache
    for user_id, user_data in users:
        cache.put(user_id, user_data)
        print(f"Cached {user_id}: {user_data}")

    print(f"\nCache size: {cache.size()}")
    print("Current cache order (least to most recently used):", cache.get_lru_order())

    # Simulate accessing user2 (updates access time)
    print("\nAccessing user2's data...")
    user2_data = cache.get("user2")
    print(f"Retrieved user2: {user2_data}")
    print("Updated cache order:", cache.get_lru_order())

    # Add new user, should evict least recently used (user1)
    print("\nAdding new user (should evict least recently used)...")
    new_user = {"name": "Alice Brown", "email": "alice@example.com"}
    cache.put("user4", new_user)
    print(f"Added user4: {new_user}")

    # Try to get evicted user
    print("\nTrying to get evicted user1...")
    user1_data = cache.get("user1")
    print("user1 data:", user1_data)  # Should be None

    # Show current cache state
    print("\nFinal cache state:")
    all_data = cache.get_all()
    for user_id, data in all_data.items():
        print(f"{user_id}: {data}")

    print("\nFinal cache order:", cache.get_lru_order())


if __name__ == "__main__":
    demonstrate_lru_cache()
