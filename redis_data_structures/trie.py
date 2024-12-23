from typing import List

from .base import RedisDataStructure


class Trie(RedisDataStructure):
    """A Redis-backed Trie (prefix tree) implementation.

    This class implements a trie data structure using Redis hashes, where each node
    in the trie is represented as a hash containing its children and a flag indicating
    if it represents the end of a word. Perfect for implementing features like
    autocomplete, spell checking, and prefix matching.
    """

    def __init__(self, **kwargs):
        """Initialize the Trie with Redis connection parameters."""
        super().__init__(**kwargs)
        self.delimiter = ":"  # Used to separate node keys in Redis

    def _get_node_key(self, key: str, prefix: str) -> str:
        """Get the Redis key for a node.

        Args:
            key (str): The Redis key for this trie
            prefix (str): The prefix path to this node

        Returns:
            str: The complete Redis key for the node
        """
        return f"{key}{self.delimiter}{prefix}" if prefix else key

    def insert(self, key: str, word: str) -> bool:
        """Insert a word into the trie.

        Args:
            key (str): The Redis key for this trie
            word (str): The word to insert

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate input
            if not isinstance(word, str):
                return False
            word = str(word)  # Convert to string but don't strip

            current_prefix = ""
            for char in word:
                node_key = self._get_node_key(key, current_prefix)
                self.redis_client.hset(node_key, char, "1")
                current_prefix = current_prefix + char if current_prefix else char

            # Mark the end of the word
            end_key = self._get_node_key(key, current_prefix)
            self.redis_client.hset(end_key, "*", "1")
            return True
        except Exception as e:
            print(f"Error inserting into trie: {e}")
            return False

    def search(self, key: str, word: str) -> bool:
        """Search for a word in the trie.

        Args:
            key (str): The Redis key for this trie
            word (str): The word to search for

        Returns:
            bool: True if the word exists, False otherwise
        """
        try:
            if not word:
                return self.redis_client.hexists(key, "*")

            if not isinstance(word, str):
                return False
            word = str(word)  # Convert to string but don't strip
            if not word:  # Empty string is a special case
                if self.redis_client.hexists(key, "*"):
                    return True  # Already exists
                self.redis_client.hset(key, "*", "1")
                return True

            current_prefix = ""
            for char in word:
                node_key = self._get_node_key(key, current_prefix)
                if not self.redis_client.hexists(node_key, char):
                    return False
                current_prefix = current_prefix + char if current_prefix else char

            end_key = self._get_node_key(key, current_prefix)
            return bool(self.redis_client.hexists(end_key, "*"))
        except Exception as e:
            print(f"Error searching trie: {e}")
            return False

    def starts_with(self, key: str, prefix: str) -> List[str]:
        """Find all words that start with the given prefix.

        Args:
            key (str): The Redis key for this trie
            prefix (str): The prefix to search for

        Returns:
            List[str]: List of words with the given prefix
        """
        try:
            # Validate input
            if not isinstance(prefix, str):
                return []
            prefix = str(prefix).strip()

            # Handle empty prefix - return all words
            if not prefix:
                return self._get_all_words(key)

            # First verify the prefix exists
            current = ""
            for char in prefix:
                node_key = self._get_node_key(key, current)
                if not self.redis_client.hexists(node_key, char):
                    return []
                current = current + char if current else char

            # DFS to find all words with the prefix
            words: List[str] = []
            self._collect_words(key, prefix, prefix, words)
            return sorted(words)  # Return sorted list for consistency
        except Exception as e:
            print(f"Error in starts_with: {e}")
            return []

    def _get_all_words(self, key: str) -> List[str]:
        """Get all words in the trie.

        Args:
            key (str): The Redis key for this trie

        Returns:
            List[str]: All words in the trie
        """
        words: List[str] = []
        if self.redis_client.hexists(key, "*"):
            words.append("")
        self._collect_words(key, "", "", words)
        return sorted(words)

    def _collect_words(self, key: str, prefix: str, current_word: str, words: List[str]) -> None:
        """Helper method to collect all words with a given prefix using DFS.

        Args:
            key (str): The Redis key for this trie
            prefix (str): The current node's prefix in the trie
            current_word (str): The word being built
            words (List[str]): List to store found words
        """
        node_key = self._get_node_key(key, prefix)

        # If this is a word, add it to results
        if self.redis_client.hexists(node_key, "*"):
            words.append(current_word)

        # Get and process all children
        try:
            children = self.redis_client.hkeys(node_key)
            for child in children:
                # Handle both string and bytes responses
                child_str = child.decode("utf-8") if isinstance(child, bytes) else child
                if child_str != "*":
                    next_prefix = prefix + child_str if prefix else child_str
                    self._collect_words(key, next_prefix, current_word + child_str, words)
        except Exception as e:
            print(f"Error collecting words: {e}")

    def delete(self, key: str, word: str) -> bool:
        """Delete a word from the trie.

        Args:
            key (str): The Redis key for this trie
            word (str): The word to delete

        Returns:
            bool: True if the word was deleted, False otherwise
        """
        try:
            # Validate input
            if not isinstance(word, str):
                return False
            word = str(word)  # Convert to string but don't strip

            if not self.search(key, word):
                return False

            # Remove the word marker
            end_key = self._get_node_key(key, word)
            self.redis_client.hdel(end_key, "*")

            # If the node has no other children, we can remove it and continue up
            current = word
            while current:
                node_key = self._get_node_key(key, current)
                if self.redis_client.hlen(node_key) == 0:
                    self.redis_client.delete(node_key)
                    current = current[:-1]
                    parent_key = self._get_node_key(key, current)
                    if current:
                        self.redis_client.hdel(parent_key, current[-1])
                else:
                    break

            return True
        except Exception as e:
            print(f"Error deleting from trie: {e}")
            return False

    def size(self, key: str) -> int:
        """Get the number of words in the trie.

        Args:
            key (str): The Redis key for this trie

        Returns:
            int: Number of complete words in the trie
        """
        try:
            # Check root node for empty string
            count = 1 if self.redis_client.hexists(key, "*") else 0

            # Use scan_iter to efficiently iterate through keys
            pattern = f"{key}{self.delimiter}*"
            for k in self.redis_client.scan_iter(pattern):
                if self.redis_client.hexists(k, "*"):
                    count += 1
            return count
        except Exception as e:
            print(f"Error getting trie size: {e}")
            return 0

    def clear(self, key: str) -> bool:
        """Clear all words from the trie.

        Args:
            key (str): The Redis key for this trie

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            pattern = f"{key}{self.delimiter}*"
            pipeline = self.redis_client.pipeline()
            # Use scan_iter for memory efficiency
            for k in self.redis_client.scan_iter(pattern):
                pipeline.delete(k)
            pipeline.delete(key)
            pipeline.execute()
            return True
        except Exception as e:
            print(f"Error clearing trie: {e}")
            return False
