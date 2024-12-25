import time

from redis_data_structures import Trie


def demonstrate_trie():
    # Initialize trie
    trie = Trie(key="autocomplete_trie")

    # Clear any existing data
    trie.clear()

    print("=== Trie Example (Prefix Tree) ===")

    # Sample words for autocomplete
    words = [
        "apple",
        "application",
        "apply",
        "banana",
        "band",
        "bandage",
        "cat",
        "catch",
        "category",
    ]

    # Insert words
    print("\nAdding words to trie...")
    for word in words:
        trie.insert(word)
        print(f"Added word: {word}")

    print(f"\nTrie size: {trie.size()}")

    # Demonstrate autocomplete functionality
    prefixes = ["app", "ban", "cat"]
    print("\nDemonstrating autocomplete:")
    for prefix in prefixes:
        suggestions = trie.starts_with(prefix)
        print(f"\nSuggestions for '{prefix}': {suggestions}")
        time.sleep(0.5)  # Simulate typing delay

    # Demonstrate search
    search_words = ["apple", "app", "category", "dog"]
    print("\nDemonstrating search:")
    for word in search_words:
        exists = trie.search(word)
        print(f"'{word}' exists in trie: {exists}")

    # Demonstrate deletion
    delete_word = "apple"
    print(f"\nDeleting word '{delete_word}'...")
    trie.delete(delete_word)
    print(f"'{delete_word}' exists in trie: {trie.search(delete_word)}")
    print(f"Words starting with 'app': {trie.starts_with('app')}")

    print("\nClearing trie...")
    trie.clear()
    print(f"Trie size after clearing: {trie.size()}")


if __name__ == "__main__":
    demonstrate_trie()
