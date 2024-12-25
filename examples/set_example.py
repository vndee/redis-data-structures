from datetime import datetime, timezone

from redis_data_structures import Set


def demonstrate_user_sessions():
    """Demonstrate set functionality with user session tracking."""
    # Initialize set
    set_ds = Set("example:active_users")

    # Clear any existing data
    set_ds.clear()

    print("=== User Session Tracking Example ===")

    # Simulating user session tracking
    print("\nTracking user sessions...")
    users = ["user123", "user456", "user789", "user123", "user001"]  # Note: user123 is duplicate

    for user in users:
        if set_ds.add(user):
            print(f"Added new user session: {user}")
        else:
            print(f"User {user} already active")

    print(f"\nTotal unique active users: {set_ds.size()}")

    # Check specific user
    test_user = "user123"
    is_active = set_ds.contains(test_user)
    print(f"\nIs {test_user} active? {is_active}")

    # Get all active users
    active_users = set_ds.members()
    print("\nAll active users:")
    for user in sorted(active_users):  # Sort for consistent output
        print(f"- {user}")

    # Remove a user
    remove_user = "user456"
    if set_ds.remove(remove_user):
        print(f"\nRemoved user: {remove_user}")
    else:
        print(f"\nUser {remove_user} was not active")
    print(f"Updated active users count: {set_ds.size()}")


def demonstrate_complex_data():
    """Demonstrate set functionality with complex data types."""
    # Initialize set
    set_ds = Set("example:user_profiles")

    # Clear any existing data
    set_ds.clear()

    print("\n=== Complex Data Example ===")

    # Add user profiles (dictionaries)
    profiles = [
        {"id": 1, "name": "Alice", "roles": ["admin", "user"]},
        {"id": 2, "name": "Bob", "roles": ["user"]},
        {"id": 3, "name": "Charlie", "roles": ["moderator", "user"]},
        {"id": 1, "name": "Alice", "roles": ["admin", "user"]},  # Duplicate
    ]

    print("\nAdding user profiles...")
    for profile in profiles:
        if set_ds.add(profile):
            print(f"Added profile: {profile['name']} (ID: {profile['id']})")
        else:
            print(f"Profile already exists: {profile['name']} (ID: {profile['id']})")

    # Get all profiles
    all_profiles = set_ds.members()
    print("\nAll user profiles:")
    for profile in sorted(all_profiles, key=lambda x: x["id"]):  # Sort by ID
        print(f"- {profile['name']} (ID: {profile['id']}, Roles: {', '.join(profile['roles'])})")

    # Store any JSON-serializable Python object
    user = {
        "id": "user1",
        "name": "Alice",
        "joined": datetime.now(timezone.utc).isoformat(),
        "metadata": {"role": "admin", "preferences": {"theme": "dark"}},
    }

    # The object will be automatically serialized/deserialized
    set_ds.add(user)
    stored_user = set_ds.members()[0]
    print("\nStored user:")
    print(stored_user)


def demonstrate_set_operations():
    """Demonstrate set functionality with tag management."""
    # Initialize set
    set_ds = Set("example:post1:tags")

    # Clear any existing data
    set_ds.clear()

    print("\n=== Tag Management Example ===")

    # Add tags for two posts
    post1_tags = ["python", "redis", "database", "programming"]
    post2_tags = ["redis", "database", "nosql", "performance"]

    print("\nAdding tags for Post 1...")
    for tag in post1_tags:
        if set_ds.add(tag):
            print(f"Added tag: {tag}")

    print("\nAdding tags for Post 2...")
    for tag in post2_tags:
        if set_ds.add(tag):
            print(f"Added tag: {tag}")

    # Get all tags for each post
    print("\nPost 1 tags:")
    for tag in sorted(set_ds.members()):
        print(f"- {tag}")

    print("\nPost 2 tags:")
    for tag in sorted(set_ds.members()):
        print(f"- {tag}")

    # Convert Redis sets to Python sets for set operations
    post1_set = set(set_ds.members())
    post2_set = set(set_ds.members())

    # Find common tags
    common_tags = post1_set & post2_set
    print("\nCommon tags between posts:")
    for tag in sorted(common_tags):
        print(f"- {tag}")

    # Find all unique tags
    all_tags = post1_set | post2_set
    print("\nAll unique tags:")
    for tag in sorted(all_tags):
        print(f"- {tag}")

    # Find tags unique to Post 1
    unique_tags = post1_set - post2_set
    print("\nTags unique to Post 1:")
    for tag in sorted(unique_tags):
        print(f"- {tag}")


if __name__ == "__main__":
    demonstrate_user_sessions()
    demonstrate_complex_data()
    demonstrate_set_operations()
