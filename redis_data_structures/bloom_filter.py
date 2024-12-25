import logging
import math
from typing import Any, List, Optional

from .base import RedisDataStructure

logger = logging.getLogger(__name__)


class BloomFilter(RedisDataStructure):
    """Redis-backed Bloom Filter implementation.

    A Bloom filter is a space-efficient probabilistic data structure used
    to test whether an element is a member of a set. False positives are
    possible, but false negatives are not.
    """

    _mmh3: Optional[Any] = None  # Cache for mmh3 module

    @classmethod
    def _get_mmh3(cls) -> Any:
        """Lazily import mmh3 module when needed."""
        if cls._mmh3 is None:
            try:
                import mmh3

                cls._mmh3 = mmh3
            except ImportError:
                raise ImportError(
                    "mmh3 is required for BloomFilter. Please install it using `pip install mmh3`.",
                ) from None
        return cls._mmh3

    def __init__(
        self,
        key: str,
        expected_elements: int = 10000,
        false_positive_rate: float = 0.01,
        **kwargs: Any,
    ) -> None:
        """Initialize Bloom Filter.

        Args:
            key (str): The key for the Bloom filter
            expected_elements (int): Expected number of elements to be added
            false_positive_rate (float): Desired false positive probability
            **kwargs: Additional Redis connection parameters
        """
        # Check for mmh3 availability on initialization
        self._get_mmh3()

        super().__init__(key, **kwargs)

        # Calculate optimal filter size and number of hash functions
        self.bit_size = self.get_optimal_size(expected_elements, false_positive_rate)
        self.num_hashes = self.get_optimal_num_hashes(expected_elements, self.bit_size)

    def get_optimal_size(self, n: int, p: float) -> int:
        """Calculate optimal bit array size.

        Args:
            n: Expected number of elements
            p: Desired false positive probability

        Returns:
            Optimal size of bit array
        """
        return int(-n * math.log(p) / (math.log(2) ** 2))

    def get_optimal_num_hashes(self, n: int, m: int) -> int:
        """Calculate optimal number of hash functions.

        Args:
            n: Expected number of elements
            m: Size of bit array

        Returns:
            Optimal number of hash functions
        """
        return max(1, int(m / n * math.log(2)))

    def get_hash_values(self, item: Any) -> List[int]:
        """Generate hash values for an item.

        Args:
            item: Item to hash

        Returns:
            List of hash values
        """
        # Convert item to string for hashing
        value = str(item).encode("utf-8")
        mmh3 = self._get_mmh3()

        # Generate hash values using MurmurHash3
        hash_values = []
        for seed in range(self.num_hashes):
            hash_val = mmh3.hash(value, seed) % self.bit_size
            hash_values.append(abs(hash_val))
        return hash_values

    def add(self, item: Any) -> bool:
        """Add an item to the Bloom filter.

        Args:
            item: Item to add

        Returns:
            bool: True if successful
        """
        try:
            hash_values = self.get_hash_values(item)
            pipeline = self.connection_manager.pipeline()

            for hash_val in hash_values:
                pipeline.setbit(self.key, hash_val, 1)

            pipeline.execute()
            return True
        except Exception:
            logger.exception("Error adding item to Bloom filter")
            return False

    def contains(self, item: Any) -> bool:
        """Check if an item might exist in the Bloom filter.

        Args:
            item: Item to check

        Returns:
            bool: True if item might exist, False if definitely doesn't exist
        """
        try:
            hash_values = self.get_hash_values(item)

            # Check if all bits are set
            for hash_val in hash_values:
                if not self.connection_manager.execute("getbit", self.key, hash_val):
                    return False
            return True
        except Exception:
            logger.exception("Error checking item in Bloom filter")
            return False

    def clear(self) -> bool:
        """Clear the Bloom filter.

        Returns:
            bool: True if successful
        """
        return super().clear()

    def size(self) -> int:
        """Get the size of the Bloom filter in bits.

        Returns:
            int: Size of the Bloom filter in bits
        """
        return self.bit_size
