from redis_data_structures import Dict
from redis_data_structures.connection import ConnectionManager


def main():
    # Initialize connection manager
    connection_manager = ConnectionManager(host="localhost", port=6379, db=0)

    # Create a Dict instance
    my_dict = Dict("example_dict", connection_manager)

    # Example: Setting values
    my_dict.set("name", "Alice")
    my_dict.set("age", 30)
    my_dict.set("is_student", False)

    # Example: Getting values
    print("Name:", my_dict.get("name"))  # Output: Alice
    print("Age:", my_dict.get("age"))  # Output: 30
    print("Is Student:", my_dict.get("is_student"))  # Output: False

    # Example: Updating a value
    my_dict.set("age", 31)
    print("Updated Age:", my_dict.get("age"))  # Output: 31

    # Example: Deleting a value
    my_dict.delete("is_student")
    print("Is Student after deletion:", my_dict.get("is_student"))  # Output: None

    # Example: Working with complex data types
    complex_data = {
        "address": {"street": "123 Main St", "city": "Wonderland", "zip": "12345"},
        "hobbies": ["reading", "hiking", "coding"],
    }
    my_dict.set("profile", complex_data)

    # Retrieve and print complex data
    retrieved_data = my_dict.get("profile")
    print("Profile:", retrieved_data)

    # Clean up
    my_dict.clear()
    connection_manager.close()

    print("Size:", my_dict.size())


if __name__ == "__main__":
    main()
