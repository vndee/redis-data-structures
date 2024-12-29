from pydantic import BaseModel

from redis_data_structures import (
    BloomFilter,
    Deque,
    Dict,
    Graph,
    HashMap,
    LRUCache,
    PriorityQueue,
    Queue,
    RingBuffer,
    Set,
    Stack,
    Trie,
)


class TestModel(BaseModel):
    id: int
    name: str

    def __hash__(self) -> int:
        """Hash the object."""
        return hash((self.id, self.name))


def test_queue():
    queue = Queue[TestModel]("test_queue")
    queue.push(TestModel(id=1, name="one"))
    queue.push(TestModel(id=2, name="two"))
    assert queue.pop() == TestModel(id=1, name="one")
    assert queue.pop() == TestModel(id=2, name="two")


def test_deque():
    deque = Deque[int]("test_deque")
    deque.push_back(1)
    deque.push_back(2)
    assert deque.pop_front() == 1
    assert deque.pop_front() == 2


def test_lru_cache():
    cache = LRUCache[bool, str]("test_cache", max_size=10)
    cache.put(True, "one")
    cache.put(False, "two")
    assert cache.get(True) == "one"
    assert cache.get(False) == "two"
    cache.clear()

    cache = LRUCache[TestModel, str]("test_cache", max_size=10)
    cache.put(TestModel(id=1, name="one"), "one")
    cache.put(TestModel(id=2, name="two"), "two")
    assert cache.get(TestModel(id=1, name="one")) == "one"
    assert cache.get(TestModel(id=2, name="two")) == "two"


def test_bloom_filter():
    bloom_filter = BloomFilter[int](
        "test_bloom_filter",
        expected_elements=10000,
        false_positive_rate=0.01,
    )
    bloom_filter.add(1)
    bloom_filter.add(2)
    assert bloom_filter.contains(1)
    assert bloom_filter.contains(2)


def test_trie():
    trie = Trie[str]("test_trie")
    trie.insert("hello")
    trie.insert("world")
    assert trie.search("hello")
    assert trie.search("world")


def test_dict():
    dict = Dict[TestModel, str]("test_dict")  # noqa: A001
    dict[TestModel(id=1, name="one")] = "one"
    dict[TestModel(id=2, name="two")] = "two"
    assert dict[TestModel(id=1, name="one")] == "one"
    assert dict[TestModel(id=2, name="two")] == "two"

    assert set(dict.keys()) == {TestModel(id=1, name="one"), TestModel(id=2, name="two")}

    new_dict = Dict("dict_2")
    new_dict[1] = "one"
    assert new_dict.keys() == [1]


def test_graph():
    graph = Graph[int]("test_graph")
    graph.add_vertex(1)
    graph.add_vertex(2)
    assert graph.vertex_exists(1)
    assert graph.vertex_exists(2)


def test_ring_buffer():
    ring_buffer = RingBuffer[int]("test_ring_buffer", capacity=10)
    ring_buffer.push(1)
    ring_buffer.push(2)


def test_set():
    set = Set[int]("test_set")  # noqa: A001
    set.add(1)
    set.add(2)
    assert 1 in set
    assert 2 in set


def test_stack():
    stack = Stack[int]("test_stack")
    stack.push(1)
    stack.push(2)
    assert stack.pop() == 2
    assert stack.pop() == 1


def test_priority_queue():
    priority_queue = PriorityQueue[int]("test_priority_queue")
    priority_queue.push(1, priority=1)
    priority_queue.push(2, priority=2)
    assert priority_queue.pop() == (1, 1)
    assert priority_queue.pop() == (2, 2)


def test_hash_map():
    hash_map: HashMap = HashMap("test_hash_map")
    hash_map[1] = "one"
    hash_map[2] = "two"
    assert hash_map[1] == "one"
    assert hash_map[2] == "two"

    assert sorted(hash_map.keys()) == [1, 2]
    assert sorted(hash_map.values()) == ["one", "two"]
    assert sorted(hash_map.items()) == [(1, "one"), (2, "two")]

    assert 1 in hash_map
    assert 2 in hash_map
    assert 3 not in hash_map

    new_hash_map = HashMap("test_hash_map_2")
    new_hash_map[TestModel(id=1, name="one")] = "one"
    assert new_hash_map.keys() == [TestModel(id=1, name="one")]
