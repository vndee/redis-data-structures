import math
from typing import Any, Optional

import mmh3  # MurmurHash3 for efficient hashing

from .base import RedisDataStructure


class BloomFilter(RedisDataStructure):
    """Redis-backed Bloom Filter implementation.

    A Bloom filter is a space-efficient probabilistic data structure used
    to test whether an element is a member of a set. False positives are
    possible, but false negatives are not.
    """

    def __init__(
        self,
        expected_elements: int = 10000,
        false_positive_rate: float = 0.01,
        host: str = "localhost",
        port: int = 6379,
        username: Optional[str] = None,
        password: Optional[str] = None,
        db: int = 0,
    ):
        """Initialize Bloom Filter.

        Args:
            expected_elements: Expected number of elements to be added
            false_positive_rate: Desired false positive probability
            host: Redis host address
            port: Redis port number
            username: Redis username for authentication
            password: Redis password for authentication
            db: Redis database number
        """
        super().__init__(host=host, port=port, username=username, password=password, db=db)

        # Calculate optimal filter size and number of hash functions
        self.size = self._get_optimal_size(expected_elements, false_positive_rate)
        self.num_hashes = self._get_optimal_num_hashes(expected_elements, self.size)

    def _get_optimal_size(self, n: int, p: float) -> int:
        """Calculate optimal bit array size.

        Args:
            n: Expected number of elements
            p: Desired false positive probability

        Returns:
            Optimal size of bit array
        """
        return int(-n * math.log(p) / (math.log(2) ** 2))

    def _get_optimal_num_hashes(self, n: int, m: int) -> int:
        """Calculate optimal number of hash functions.

        Args:
            n: Expected number of elements
            m: Size of bit array

        Returns:
            Optimal number of hash functions
        """
        return max(1, int(m / n * math.log(2)))

    def _get_hash_values(self, item: Any) -> list[int]:
        """Generate hash values for an item.

        Args:
            item: Item to hash

        Returns:
            List of hash values
        """
        # Convert item to string for hashing
        value = str(item).encode("utf-8")

        # Generate hash values using MurmurHash3
        hash_values = []
        for seed in range(self.num_hashes):
            hash_val = mmh3.hash(value, seed) % self.size
            hash_values.append(abs(hash_val))
        return hash_values

    def add(self, key: str, item: Any) -> bool:
        """Add an item to the Bloom filter.

        Args:
            key: The Redis key for this Bloom filter
            item: Item to add

        Returns:
            bool: True if successful
        """
        try:
            hash_values = self._get_hash_values(item)
            pipe = self.redis_client.pipeline()

            for hash_val in hash_values:
                pipe.setbit(key, hash_val, 1)

            pipe.execute()
            return True
        except Exception as e:
            print(f"Error adding item to Bloom filter: {e}")
            return False

    def contains(self, key: str, item: Any) -> bool:
        """Check if an item might exist in the Bloom filter.

        Args:
            key: The Redis key for this Bloom filter
            item: Item to check

        Returns:
            bool: True if item might exist, False if definitely doesn't exist
        """
        try:
            hash_values = self._get_hash_values(item)

            # Check if all bits are set
            for hash_val in hash_values:
                if not self.redis_client.getbit(key, hash_val):
                    return False
            return True
        except Exception as e:
            print(f"Error checking item in Bloom filter: {e}")
            return False

    def clear(self, key: str) -> bool:
        """Clear the Bloom filter.

        Args:
            key: The Redis key for this Bloom filter

        Returns:
            bool: True if successful
        """
        return super().clear(key)

    def size(self, key: str) -> int:
        """Get the size of the Bloom filter in bits.

        Args:
            key: The Redis key for this Bloom filter

        Returns:
            int: Size of the Bloom filter in bits
        """
        return self.size
