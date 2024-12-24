import logging
from typing import List

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


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
        base_key = self._get_key(key)
        return f"{base_key}{self.delimiter}{prefix}" if prefix else base_key

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
                self.connection_manager.execute("hset", node_key, char, "1")
                current_prefix = current_prefix + char if current_prefix else char

            # Mark the end of the word
            end_key = self._get_node_key(key, current_prefix)
            self.connection_manager.execute("hset", end_key, "*", "1")
            return True
        except Exception:
            logger.exception("Error inserting into trie")
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
                return bool(self.connection_manager.execute("hexists", self._get_key(key), "*"))

            if not isinstance(word, str):
                return False
            word = str(word)  # Convert to string but don't strip

            current_prefix = ""
            for char in word:
                node_key = self._get_node_key(key, current_prefix)
                if not self.connection_manager.execute("hexists", node_key, char):
                    return False
                current_prefix = current_prefix + char if current_prefix else char

            end_key = self._get_node_key(key, current_prefix)
            return bool(self.connection_manager.execute("hexists", end_key, "*"))
        except Exception:
            logger.exception("Error searching trie")
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
                if not self.connection_manager.execute("hexists", node_key, char):
                    return []
                current = current + char if current else char

            # DFS to find all words with the prefix
            words: List[str] = []
            self._collect_words(key, prefix, prefix, words)
            return sorted(words)  # Return sorted list for consistency
        except Exception:
            logger.exception("Error in starts_with")
            return []

    def _get_all_words(self, key: str) -> List[str]:
        """Get all words in the trie.

        Args:
            key (str): The Redis key for this trie

        Returns:
            List[str]: All words in the trie
        """
        words: List[str] = []
        if self.connection_manager.execute("hexists", self._get_key(key), "*"):
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
        if self.connection_manager.execute("hexists", node_key, "*"):
            words.append(current_word)

        # Get and process all children
        try:
            children = self.connection_manager.execute("hkeys", node_key)
            for child in children:
                # Handle both string and bytes responses
                child_str = child.decode("utf-8") if isinstance(child, bytes) else child
                if child_str != "*":
                    next_prefix = prefix + child_str if prefix else child_str
                    self._collect_words(key, next_prefix, current_word + child_str, words)
        except Exception:
            logger.exception("Error collecting words")

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
            self.connection_manager.execute("hdel", end_key, "*")

            # If the node has no other children, we can remove it and continue up
            current = word
            while current:
                node_key = self._get_node_key(key, current)
                children = self.connection_manager.execute("hkeys", node_key)
                if not children:
                    # No children, delete this node and continue up
                    self.connection_manager.execute("delete", node_key)
                    current = current[:-1]  # Remove last character
                else:
                    break  # Node has other children, stop here

            return True
        except Exception:
            logger.exception("Error deleting from trie")
            return False

    def size(self, key: str) -> int:
        """Get the number of words in the trie.

        Args:
            key (str): The Redis key for this trie

        Returns:
            int: Number of words in the trie
        """
        try:
            # Count all nodes with the word marker
            count = 0
            if self.connection_manager.execute("hexists", self._get_key(key), "*"):
                count += 1

            # Use scan to iterate through all keys
            pattern = f"{self._get_key(key)}{self.delimiter}*"
            cursor = 0  # Start with cursor 0
            while True:
                cursor, keys = self.connection_manager.execute(
                    "scan",
                    cursor,
                    match=pattern,
                    count=100,
                )

                if keys:
                    for key_name in keys:
                        if isinstance(key_name, bytes):
                            key_name = key_name.decode("utf-8")
                        if self.connection_manager.execute("hexists", key_name, "*"):
                            count += 1
                if cursor == 0:  # End of iteration
                    break

            return count
        except Exception:
            logger.exception("Error getting trie size")
            return 0

    def clear(self, key: str) -> bool:
        """Remove all words from the trie.

        Args:
            key (str): The Redis key for this trie

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Delete all keys with the prefix
            pattern = f"{self._get_key(key)}{self.delimiter}*"
            cursor = 0  # Start with cursor 0
            while True:
                cursor, keys = self.connection_manager.execute(
                    "scan",
                    cursor,
                    match=pattern,
                    count=100,
                )

                if keys:
                    # Delete keys in batches
                    for i in range(0, len(keys), 100):
                        batch = keys[i : i + 100]
                        if batch:
                            self.connection_manager.execute("delete", *batch)
                if cursor == 0:  # End of iteration
                    break

            # Delete the root key
            self.connection_manager.execute("delete", self._get_key(key))
            return True
        except Exception:
            logger.exception("Error clearing trie")
            return False
