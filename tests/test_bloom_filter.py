import math
import unittest

from redis_data_structures import BloomFilter


class TestBloomFilter(unittest.TestCase):
    """Test cases for BloomFilter implementation."""

    def setUp(self):
        """Set up test cases."""
        self.bloom = BloomFilter(expected_elements=1000, false_positive_rate=0.01)
        self.test_key = "test_bloom_filter"

    def tearDown(self):
        """Clean up after tests."""
        self.bloom.clear(self.test_key)

    def test_add_and_contains(self):
        """Test adding items and checking membership."""
        # Test adding single item
        self.assertTrue(self.bloom.add(self.test_key, "test1"))
        self.assertTrue(self.bloom.contains(self.test_key, "test1"))

        # Test item that wasn't added
        self.assertFalse(self.bloom.contains(self.test_key, "test2"))

    def test_multiple_items(self):
        """Test adding and checking multiple items."""
        items = ["test1", "test2", "test3", "test4", "test5"]

        # Add all items
        for item in items:
            self.assertTrue(self.bloom.add(self.test_key, item))

        # Check all items exist
        for item in items:
            self.assertTrue(self.bloom.contains(self.test_key, item))

    def test_different_types(self):
        """Test adding items of different types."""
        items = [
            42,
            3.14,
            "string",
            True,
            (1, 2, 3),
            ["list", "items"],
            {"key": "value"},
        ]

        # Add all items
        for item in items:
            self.assertTrue(self.bloom.add(self.test_key, item))

        # Check all items exist
        for item in items:
            self.assertTrue(self.bloom.contains(self.test_key, item))

    def test_clear(self):
        """Test clearing the Bloom filter."""
        # Add some items
        items = ["test1", "test2", "test3"]
        for item in items:
            self.bloom.add(self.test_key, item)

        # Clear the filter
        self.assertTrue(self.bloom.clear(self.test_key))

        # Check items no longer exist
        for item in items:
            self.assertFalse(self.bloom.contains(self.test_key, item))

    def test_false_positive_rate(self):
        """Test false positive rate is within expected bounds."""
        # Create a new filter with known parameters
        n = 1000  # number of elements
        p = 0.01  # false positive rate
        bloom = BloomFilter(expected_elements=n, false_positive_rate=p)

        # Add n elements
        for i in range(n):
            bloom.add(self.test_key, f"element_{i}")

        # Test false positives with elements we didn't add
        false_positives = 0
        test_size = 1000

        for i in range(test_size):
            if bloom.contains(self.test_key, f"not_added_{i}"):
                false_positives += 1

        actual_rate = false_positives / test_size
        # The actual rate should be close to the expected rate
        self.assertLess(actual_rate, p * 2)  # Allow some margin

    def test_size_calculation(self):
        """Test that size calculation is reasonable."""
        n = 1000
        p = 0.01
        bloom = BloomFilter(expected_elements=n, false_positive_rate=p)

        # Optimal size should be greater than number of elements
        self.assertGreater(bloom.size, n)

        # Size should be reasonable (not too large)
        expected_size = int(
            -n
            * bloom._get_optimal_num_hashes(n, bloom.size)
            / math.log(1 - p ** (1 / bloom._get_optimal_num_hashes(n, bloom.size))),
        )
        self.assertLess(abs(bloom.size - expected_size) / expected_size, 0.5)


if __name__ == "__main__":
    unittest.main()
