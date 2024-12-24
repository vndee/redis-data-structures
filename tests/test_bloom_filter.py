"""Tests for BloomFilter implementation."""

import math
import importlib
import sys
from typing import List

import pytest
from unittest.mock import patch
from redis.exceptions import RedisError

from redis_data_structures.bloom_filter import BloomFilter


@pytest.fixture
def bloom_filter(connection_manager) -> 'BloomFilter':
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

    def test_bloom_filter_import_error(self, monkeypatch):
        """Test that BloomFilter raises an ImportError if mmh3 is not installed."""
        
        # Remove the module if it's already imported
        if 'mmh3' in sys.modules:
            del sys.modules['mmh3']
        if 'redis_data_structures.bloom_filter' in sys.modules:
            del sys.modules['redis_data_structures.bloom_filter']
            
        # Patch __import__ to raise ImportError for mmh3
        def mock_import(name, *args, **kwargs):
            if name == 'mmh3':
                raise ImportError("No module named 'mmh3'")
            return importlib.__import__(name, *args, **kwargs)
            
        monkeypatch.setattr('builtins.__import__', mock_import)
        
        with pytest.raises(ImportError, match="mmh3 is required for BloomFilter"):
            from redis_data_structures.bloom_filter import BloomFilter

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

    def test_add_error_handling(self, bloom_filter):
        """Test error handling during add operation."""
        # Simulate an error in getting hash values
        with patch.object(bloom_filter, "get_hash_values", side_effect=Exception("Hashing error")):
            assert not bloom_filter.add("test_bloom_filter", "test1")

        # Simulate an error in the pipeline execution
        with patch.object(bloom_filter.connection_manager, "pipeline") as mock_pipeline:
            mock_pipeline.return_value.execute.side_effect = Exception("Pipeline execution error")
            assert not bloom_filter.add("test_bloom_filter", "test1")

    def test_contains_error_handling(self, bloom_filter):
        """Test error handling during contains operation."""
        with patch.object(bloom_filter.connection_manager, "execute", side_effect=RedisError):
            assert not bloom_filter.contains("test_bloom_filter", "test1")
