from redis_data_structures import Set


def demonstrate_set():
    # Initialize set
    set_ds = Set(host="localhost", port=6379, db=0)
    set_key = "active_users"

    # Clear any existing data
    set_ds.clear(set_key)

    print("=== Set Example ===")

    # Simulating user session tracking
    print("\nTracking user sessions...")
    users = ["user123", "user456", "user789", "user123", "user001"]  # Duplicate user

    for user in users:
        set_ds.add(set_key, user)
        print(f"Added user session: {user}")

    print(f"\nTotal unique active users: {set_ds.size(set_key)}")

    # Check specific user
    test_user = "user123"
    is_active = set_ds.contains(set_key, test_user)
    print(f"\nIs {test_user} active? {is_active}")

    # Get all active users
    active_users = set_ds.members(set_key)
    print("\nAll active users:")
    for user in active_users:
        print(f"- {user}")

    # Remove a user
    remove_user = "user456"
    set_ds.remove(set_key, remove_user)
    print(f"\nRemoved user: {remove_user}")
    print(f"Updated active users count: {set_ds.size(set_key)}")


if __name__ == "__main__":
    demonstrate_set()
