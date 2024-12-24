"""Tests for BloomFilter implementation."""

import math
from typing import List

import pytest

from redis_data_structures import BloomFilter


@pytest.fixture
def bloom_filter(connection_manager) -> BloomFilter:
    """Create a BloomFilter instance for testing."""
    return BloomFilter(
        expected_elements=1000,
        false_positive_rate=0.01,
        connection_manager=connection_manager,
    )


@pytest.fixture
def test_key() -> str:
    """Get test key for BloomFilter."""
    return "test_bloom_filter"


@pytest.fixture
def sample_items() -> List:
    """Get sample items of different types for testing."""
    return [
        42,
        3.14,
        "string",
        True,
        (1, 2, 3),
        ["list", "items"],
        {"key": "value"},
    ]


@pytest.mark.integration
class TestBloomFilter:
    """Test cases for BloomFilter implementation."""

    def test_add_and_contains(self, bloom_filter: BloomFilter, test_key: str):
        """Test adding items and checking membership."""
        # Test adding single item
        assert bloom_filter.add(test_key, "test1")
        assert bloom_filter.contains(test_key, "test1")

        # Test item that wasn't added
        assert not bloom_filter.contains(test_key, "test2")

    def test_multiple_items(self, bloom_filter: BloomFilter, test_key: str):
        """Test adding and checking multiple items."""
        items = ["test1", "test2", "test3", "test4", "test5"]

        # Add all items
        for item in items:
            assert bloom_filter.add(test_key, item)

        # Check all items exist
        for item in items:
            assert bloom_filter.contains(test_key, item)

    def test_different_types(self, bloom_filter: BloomFilter, test_key: str, sample_items: List):
        """Test adding items of different types."""
        # Add all items
        for item in sample_items:
            assert bloom_filter.add(test_key, item)

        # Check all items exist
        for item in sample_items:
            assert bloom_filter.contains(test_key, item)

    def test_clear(self, bloom_filter: BloomFilter, test_key: str):
        """Test clearing the Bloom filter."""
        # Add some items
        items = ["test1", "test2", "test3"]
        for item in items:
            bloom_filter.add(test_key, item)

        # Clear the filter
        assert bloom_filter.clear(test_key)

        # Check items no longer exist
        for item in items:
            assert not bloom_filter.contains(test_key, item)

    @pytest.mark.slow
    def test_false_positive_rate(self, bloom_filter: BloomFilter, test_key: str):
        """Test false positive rate is within expected bounds."""
        n = 1000  # number of elements
        p = 0.01  # false positive rate

        # Add n elements
        for i in range(n):
            bloom_filter.add(test_key, f"element_{i}")

        # Test false positives with elements we didn't add
        false_positives = 0
        test_size = 1000

        for i in range(test_size):
            if bloom_filter.contains(test_key, f"not_added_{i}"):
                false_positives += 1

        actual_rate = false_positives / test_size
        # The actual rate should be close to the expected rate
        assert actual_rate < p * 2  # Allow some margin

    def test_size_calculation(self, bloom_filter: BloomFilter):
        """Test that size calculation is reasonable."""
        n = 1000
        p = 0.01

        # Optimal size should be greater than number of elements
        assert bloom_filter.size() > n

        # Size should be reasonable (not too large)
        expected_size = int(
            -n
            * bloom_filter.get_optimal_num_hashes(n, bloom_filter.size())
            / math.log(1 - p ** (1 / bloom_filter.get_optimal_num_hashes(n, bloom_filter.size()))),
        )
        assert abs(bloom_filter.size() - expected_size) / expected_size < 0.5
