import unittest

from redis_data_structures import PriorityQueue


class TestPriorityQueue(unittest.TestCase):
    def setUp(self):
        self.pq = PriorityQueue(host="localhost", port=6379, db=0)
        self.test_key = "test_priority_queue"
        self.pq.clear(self.test_key)

    def tearDown(self):
        self.pq.clear(self.test_key)

    def test_push_and_pop(self):
        # Test basic push and pop operations
        self.pq.push(self.test_key, "low_priority", 3)
        self.pq.push(self.test_key, "high_priority", 1)

        assert self.pq.size(self.test_key) == 2
        item, priority = self.pq.pop(self.test_key)
        assert item == "high_priority"
        assert priority == 1

    def test_pop_empty_queue(self):
        # Test popping from empty queue
        assert self.pq.pop(self.test_key) is None

    def test_size(self):
        # Test size operations
        assert self.pq.size(self.test_key) == 0

        self.pq.push(self.test_key, "item1", 1)
        assert self.pq.size(self.test_key) == 1

        self.pq.push(self.test_key, "item2", 2)
        assert self.pq.size(self.test_key) == 2

        self.pq.pop(self.test_key)
        assert self.pq.size(self.test_key) == 1

    def test_clear(self):
        # Test clear operation
        self.pq.push(self.test_key, "item1", 1)
        self.pq.push(self.test_key, "item2", 2)

        self.pq.clear(self.test_key)
        assert self.pq.size(self.test_key) == 0

    def test_priority_order(self):
        # Test priority ordering (lower number = higher priority)
        items = [("lowest", 3), ("highest", 1), ("medium", 2)]

        for item, priority in items:
            self.pq.push(self.test_key, item, priority)

        # Should pop in order: highest (1), medium (2), lowest (3)
        expected_order = ["highest", "medium", "lowest"]
        for expected_item in expected_order:
            item, _ = self.pq.pop(self.test_key)
            assert item == expected_item

    def test_same_priority(self):
        # Test items with same priority
        self.pq.push(self.test_key, "first", 1)
        self.pq.push(self.test_key, "second", 1)

        # Should maintain order for same priority
        item1, _ = self.pq.pop(self.test_key)
        item2, _ = self.pq.pop(self.test_key)
        assert item1 == "first"
        assert item2 == "second"


if __name__ == "__main__":
    unittest.main()
