from redis_data_structures import Stack


def demonstrate_stack():
    # Initialize stack
    stack = Stack(key="undo_stack")

    # Clear any existing data
    stack.clear()

    print("=== Stack Example (LIFO) ===")

    # Simulating undo operations in a text editor
    print("\nPerforming text editor operations...")
    operations = ["Add paragraph 1", "Add paragraph 2", "Delete paragraph 1", "Add paragraph 3"]

    for operation in operations:
        stack.push(operation)
        print(f"Performed operation: {operation}")

    print(f"\nStack size: {stack.size()}")

    # Performing undo operations
    print("\nPerforming undo operations...")
    undo_count = 3
    for _i in range(undo_count):
        if stack.size() > 0:
            operation = stack.pop()
            print(f"Undoing: {operation}")

    print(f"\nRemaining operations in stack: {stack.size()}")


if __name__ == "__main__":
    demonstrate_stack()
