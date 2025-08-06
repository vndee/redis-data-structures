from pydantic import BaseModel
from typing import List
from redis_data_structures import LRUCache


class Child(BaseModel):
    name: str
    age: int

list_of_children = [Child(name="child1", age=10), Child(name="child2", age=20)]

cache: LRUCache[str, List[Child]] = LRUCache(capacity=2, key="list_of_children")

# Register the Child type so deserialization works properly
cache.register_types(Child)

cache.put("list_of_children", list_of_children)

print(cache.get("list_of_children"))