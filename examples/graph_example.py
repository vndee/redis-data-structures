from redis_data_structures import Graph


def demonstrate_graph():
    # Initialize graph
    graph = Graph("social_network", host="localhost", port=6379, db=0)

    # Clear any existing data
    graph.clear()

    print("=== Graph Example (Social Network) ===")

    # Add users as vertices with profile data
    users = {
        "alice": {"name": "Alice Smith", "age": 28},
        "bob": {"name": "Bob Johnson", "age": 32},
        "carol": {"name": "Carol Williams", "age": 25},
        "david": {"name": "David Brown", "age": 35},
    }

    print("\nAdding users to the network...")
    for user_id, profile in users.items():
        graph.add_vertex(user_id, profile)
        print(f"Added user: {profile['name']}")

    # Create friendships (edges)
    print("\nCreating friendships...")
    friendships = [
        ("alice", "bob", 0.8),  # Alice and Bob are close friends
        ("bob", "alice", 0.8),  # Friendship is mutual
        ("alice", "carol", 0.6),  # Alice and Carol are friends
        ("carol", "alice", 0.6),  # Friendship is mutual
        ("bob", "david", 0.4),  # Bob and David are acquaintances
        ("david", "bob", 0.4),  # Friendship is mutual
    ]

    for from_user, to_user, strength in friendships:
        graph.add_edge(from_user, to_user, strength)
        print(f"Added friendship: {from_user} -> {to_user} (strength: {strength})")

    # Display network information
    print("\nNetwork Information:")
    print(f"Total users: {len(graph.get_vertices())}")

    # Display user profiles and their friends
    print("\nUser Profiles and Friends:")
    for user_id in graph.get_vertices():
        profile = graph.get_vertex_data(user_id)
        friends = graph.get_neighbors(user_id)

        print(f"\n{profile['name']} ({user_id}):")
        print("Friends:")
        for friend_id, strength in friends.items():
            friend_profile = graph.get_vertex_data(friend_id)
            print(f"- {friend_profile['name']} (friendship strength: {strength})")

    # Remove a user
    print("\nRemoving David from the network...")
    graph.remove_vertex("david")

    # Show updated network
    print("\nUpdated Network Information:")
    print(f"Total users: {len(graph.get_vertices())}")

    # Clean up
    graph.clear()
    print("\nNetwork cleared!")


if __name__ == "__main__":
    demonstrate_graph()
