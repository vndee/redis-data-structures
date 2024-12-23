import unittest

from redis_data_structures import Stack


class TestStack(unittest.TestCase):
    EXPECTED_SIZE_TWO = 2  # Constant for size comparisons

    def setUp(self):
        self.stack = Stack(host="localhost", port=6379, db=0)
        self.test_key = "test_stack"
        self.stack.clear(self.test_key)

    def tearDown(self):
        self.stack.clear(self.test_key)

    def test_push_and_pop(self):
        # Test basic push and pop operations
        self.stack.push(self.test_key, "item1")
        self.stack.push(self.test_key, "item2")

        assert self.stack.size(self.test_key) == self.EXPECTED_SIZE_TWO
        assert self.stack.pop(self.test_key) == "item2"
        assert self.stack.pop(self.test_key) == "item1"

    def test_pop_empty_stack(self):
        # Test popping from empty stack
        assert self.stack.pop(self.test_key) is None

    def test_size(self):
        # Test size operations
        assert self.stack.size(self.test_key) == 0

        self.stack.push(self.test_key, "item1")
        assert self.stack.size(self.test_key) == 1

        self.stack.push(self.test_key, "item2")
        assert self.stack.size(self.test_key) == self.EXPECTED_SIZE_TWO

        self.stack.pop(self.test_key)
        assert self.stack.size(self.test_key) == 1

    def test_clear(self):
        # Test clear operation
        self.stack.push(self.test_key, "item1")
        self.stack.push(self.test_key, "item2")

        self.stack.clear(self.test_key)
        assert self.stack.size(self.test_key) == 0

    def test_lifo_order(self):
        # Test LIFO ordering
        items = ["first", "second", "third"]
        for item in items:
            self.stack.push(self.test_key, item)

        for expected_item in reversed(items):
            assert self.stack.pop(self.test_key) == expected_item


if __name__ == "__main__":
    unittest.main()
