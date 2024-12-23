from redis_data_structures import Stack


def demonstrate_stack():
    # Initialize stack
    stack = Stack(host="localhost", port=6379, db=0)
    stack_key = "undo_stack"

    # Clear any existing data
    stack.clear(stack_key)

    print("=== Stack Example (LIFO) ===")

    # Simulating undo operations in a text editor
    print("\nPerforming text editor operations...")
    operations = ["Add paragraph 1", "Add paragraph 2", "Delete paragraph 1", "Add paragraph 3"]

    for operation in operations:
        stack.push(stack_key, operation)
        print(f"Performed operation: {operation}")

    print(f"\nStack size: {stack.size(stack_key)}")

    # Performing undo operations
    print("\nPerforming undo operations...")
    undo_count = 3
    for _i in range(undo_count):
        if stack.size(stack_key) > 0:
            operation = stack.pop(stack_key)
            print(f"Undoing: {operation}")

    print(f"\nRemaining operations in stack: {stack.size(stack_key)}")


if __name__ == "__main__":
    demonstrate_stack()
