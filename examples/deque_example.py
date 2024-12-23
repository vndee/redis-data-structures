from redis_data_structures import Deque


def demonstrate_deque():
    # Initialize deque
    deque = Deque(host="localhost", port=6379, db=0)
    deque_key = "browser_history"

    # Clear any existing data
    deque.clear(deque_key)

    print("=== Deque Example (Double-ended Queue) ===")

    # Simulating browser history
    print("\nBrowsing websites...")
    pages = ["homepage.com", "search.com", "blog.com", "news.com", "shop.com"]

    # Adding pages to history (at the back)
    for page in pages:
        deque.push_back(deque_key, page)
        print(f"Visited: {page}")

    print(f"\nHistory size: {deque.size(deque_key)}")

    # Simulating forward/backward navigation
    print("\nNavigating through history...")

    # Go back two pages
    print("\nGoing back two pages:")
    for _ in range(2):
        page = deque.pop_back(deque_key)
        deque.push_front(deque_key, page)
        print(f"Moved back to: {page}")

    # Go forward one page
    print("\nGoing forward one page:")
    page = deque.pop_front(deque_key)
    deque.push_back(deque_key, page)
    print(f"Moved forward to: {page}")

    # Add a new page (will clear forward history)
    new_page = "newsite.com"
    print(f"\nVisiting new page: {new_page}")
    deque.push_back(deque_key, new_page)

    print(f"\nFinal history size: {deque.size(deque_key)}")


if __name__ == "__main__":
    demonstrate_deque()
