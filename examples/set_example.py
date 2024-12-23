from redis_data_structures import Set


def demonstrate_user_sessions():
    """Demonstrate set functionality with user session tracking."""
    # Initialize set
    set_ds = Set()
    set_key = "example:active_users"

    # Clear any existing data
    set_ds.clear(set_key)

    print("=== User Session Tracking Example ===")

    # Simulating user session tracking
    print("\nTracking user sessions...")
    users = ["user123", "user456", "user789", "user123", "user001"]  # Note: user123 is duplicate

    for user in users:
        if set_ds.add(set_key, user):
            print(f"Added new user session: {user}")
        else:
            print(f"User {user} already active")

    print(f"\nTotal unique active users: {set_ds.size(set_key)}")

    # Check specific user
    test_user = "user123"
    is_active = set_ds.contains(set_key, test_user)
    print(f"\nIs {test_user} active? {is_active}")

    # Get all active users
    active_users = set_ds.members(set_key)
    print("\nAll active users:")
    for user in sorted(active_users):  # Sort for consistent output
        print(f"- {user}")

    # Remove a user
    remove_user = "user456"
    if set_ds.remove(set_key, remove_user):
        print(f"\nRemoved user: {remove_user}")
    else:
        print(f"\nUser {remove_user} was not active")
    print(f"Updated active users count: {set_ds.size(set_key)}")


def demonstrate_complex_data():
    """Demonstrate set functionality with complex data types."""
    # Initialize set
    set_ds = Set()
    set_key = "example:user_profiles"

    # Clear any existing data
    set_ds.clear(set_key)

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
        if set_ds.add(set_key, profile):
            print(f"Added profile: {profile['name']} (ID: {profile['id']})")
        else:
            print(f"Profile already exists: {profile['name']} (ID: {profile['id']})")

    # Get all profiles
    all_profiles = set_ds.members(set_key)
    print("\nAll user profiles:")
    for profile in sorted(all_profiles, key=lambda x: x["id"]):  # Sort by ID
        print(f"- {profile['name']} (ID: {profile['id']}, Roles: {', '.join(profile['roles'])})")


def demonstrate_set_operations():
    """Demonstrate set functionality with tag management."""
    # Initialize set
    set_ds = Set()
    post1_tags_key = "example:post1:tags"
    post2_tags_key = "example:post2:tags"

    # Clear any existing data
    set_ds.clear(post1_tags_key)
    set_ds.clear(post2_tags_key)

    print("\n=== Tag Management Example ===")

    # Add tags for two posts
    post1_tags = ["python", "redis", "database", "programming"]
    post2_tags = ["redis", "database", "nosql", "performance"]

    print("\nAdding tags for Post 1...")
    for tag in post1_tags:
        if set_ds.add(post1_tags_key, tag):
            print(f"Added tag: {tag}")

    print("\nAdding tags for Post 2...")
    for tag in post2_tags:
        if set_ds.add(post2_tags_key, tag):
            print(f"Added tag: {tag}")

    # Get all tags for each post
    print("\nPost 1 tags:")
    for tag in sorted(set_ds.members(post1_tags_key)):
        print(f"- {tag}")

    print("\nPost 2 tags:")
    for tag in sorted(set_ds.members(post2_tags_key)):
        print(f"- {tag}")

    # Find common tags (intersection)
    common_tags = set_ds.members(post1_tags_key) & set_ds.members(post2_tags_key)
    print("\nCommon tags between posts:")
    for tag in sorted(common_tags):
        print(f"- {tag}")


if __name__ == "__main__":
    demonstrate_user_sessions()
    demonstrate_complex_data()
    demonstrate_set_operations()
