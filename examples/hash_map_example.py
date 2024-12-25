from redis_data_structures import HashMap


def demonstrate_hash_map():
    # Initialize hash map
    hash_map = HashMap("user_profiles")

    # Clear any existing data
    hash_map.clear()

    print("=== Hash Map Example ===")

    # Simulating user profile management
    print("\nCreating user profiles...")
    users = {
        "user123": {"name": "John Doe", "email": "john@example.com", "age": 30},
        "user456": {"name": "Jane Smith", "email": "jane@example.com", "age": 25},
    }

    # Adding user profiles
    for user_id, profile in users.items():
        hash_map.set(user_id, profile)
        print(f"Added profile for user: {user_id}")

    print(f"\nTotal profiles stored: {hash_map.size()}")

    # Retrieving a specific profile
    user_id = "user123"
    profile = hash_map.get(user_id)
    if profile:
        print(f"\nProfile for {user_id}:")
        for key, value in profile.items():
            print(f"- {key}: {value}")

    # Getting all profiles
    print("\nAll profiles:")
    all_profiles = hash_map.get_all()
    for user_id, profile in all_profiles.items():
        print(f"\nUser ID: {user_id}")
        for key, value in profile.items():
            print(f"- {key}: {value}")

    # Updating a profile
    user_id = "user456"
    updated_profile = {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",  # Updated email
        "age": 26,  # Updated age
    }
    hash_map.set(user_id, updated_profile)
    print(f"\nUpdated profile for user: {user_id}")

    # Verify the update
    updated = hash_map.get(user_id)
    if updated:
        print(f"\nUpdated profile for {user_id}:")
        for key, value in updated.items():
            print(f"- {key}: {value}")

    # Clean up
    hash_map.clear()
    hash_map.close()


if __name__ == "__main__":
    demonstrate_hash_map()
