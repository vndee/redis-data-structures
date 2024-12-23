from typing import Tuple

from redis_data_structures.base import RedisDataStructure


def test_serialization():
    # Create a test instance
    rds = RedisDataStructure()

    # Test basic tuple serialization
    tuple_data: Tuple[int, str, list] = (1, "two", [3, 4])
    serialized_tuple = rds._serialize(tuple_data)
    print("Serialized tuple:", serialized_tuple)

    # Test deserialization
    deserialized_tuple = rds._deserialize(serialized_tuple)
    print("Deserialized tuple:", deserialized_tuple)

    # Test that the deserialized data matches the original
    assert deserialized_tuple["value"] == tuple_data, "Deserialized data doesn't match original"
    print("Test passed: Deserialized data matches original")


if __name__ == "__main__":
    test_serialization()
