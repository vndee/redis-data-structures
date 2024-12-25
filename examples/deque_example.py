from redis_data_structures import Deque


def demonstrate_deque():
    # Initialize deque
    deque = Deque("browser_history", host="localhost", port=6379, db=0)

    # Clear any existing data
    deque.clear()

    print("=== Deque Example (Double-ended Queue) ===")

    # Simulating browser history
    print("\nBrowsing websites...")
    pages = ["homepage.com", "search.com", "blog.com", "news.com", "shop.com"]

    # Adding pages to history (at the back)
    for page in pages:
        deque.push_back(page)
        print(f"Visited: {page}")

    print(f"\nHistory size: {deque.size()}")

    # Simulating forward/backward navigation
    print("\nNavigating through history...")

    # Go back two pages
    print("\nGoing back two pages:")
    for _ in range(2):
        page = deque.pop_back()
        deque.push_front(page)
        print(f"Moved back to: {page}")

    # Go forward one page
    print("\nGoing forward one page:")
    page = deque.pop_front()
    deque.push_back(page)
    print(f"Moved forward to: {page}")

    # Add a new page (will clear forward history)
    new_page = "newsite.com"
    print(f"\nVisiting new page: {new_page}")
    deque.push_back(new_page)

    print(f"\nFinal history size: {deque.size()}")


if __name__ == "__main__":
    demonstrate_deque()
