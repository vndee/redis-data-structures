import unittest

from redis_data_structures import Queue


class TestQueue(unittest.TestCase):
    def setUp(self):
        self.queue = Queue(host="localhost", port=6379, db=0)
        self.test_key = "test_queue"
        self.queue.clear(self.test_key)

    def tearDown(self):
        self.queue.clear(self.test_key)

    def test_push_and_pop(self):
        # Test basic push and pop operations
        self.queue.push(self.test_key, "item1")
        self.queue.push(self.test_key, "item2")

        assert self.queue.size(self.test_key) == 2
        assert self.queue.pop(self.test_key) == "item1"
        assert self.queue.pop(self.test_key) == "item2"

    def test_pop_empty_queue(self):
        # Test popping from empty queue
        assert self.queue.pop(self.test_key) is None

    def test_size(self):
        # Test size operations
        assert self.queue.size(self.test_key) == 0

        self.queue.push(self.test_key, "item1")
        assert self.queue.size(self.test_key) == 1

        self.queue.push(self.test_key, "item2")
        assert self.queue.size(self.test_key) == 2

        self.queue.pop(self.test_key)
        assert self.queue.size(self.test_key) == 1

    def test_clear(self):
        # Test clear operation
        self.queue.push(self.test_key, "item1")
        self.queue.push(self.test_key, "item2")

        self.queue.clear(self.test_key)
        assert self.queue.size(self.test_key) == 0

    def test_fifo_order(self):
        # Test FIFO ordering
        items = ["first", "second", "third"]
        for item in items:
            self.queue.push(self.test_key, item)

        for expected_item in items:
            assert self.queue.pop(self.test_key) == expected_item


if __name__ == "__main__":
    unittest.main()
