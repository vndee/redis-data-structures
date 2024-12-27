import uuid
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import BaseModel

from redis_data_structures.serializer import Serializer


@pytest.fixture
def serializer():
    return Serializer()


def test_serialize_int(serializer):
    assert serializer.deserialize(serializer.serialize(1)) == 1


def test_serialize_float(serializer):
    assert serializer.deserialize(serializer.serialize(1.5)) == 1.5


def test_serialize_str(serializer):
    assert serializer.deserialize(serializer.serialize("test")) == "test"
    assert serializer.deserialize(serializer.serialize("{'key':'value'}")) == "{'key':'value'}"
    assert serializer.deserialize(serializer.serialize("{'key':'value'}")) == "{'key':'value'}"


def test_serialize_bool(serializer):
    assert serializer.deserialize(serializer.serialize(True))
    assert not serializer.deserialize(serializer.serialize(False))


def test_serialize_list(serializer):
    assert serializer.deserialize(serializer.serialize([1, 2, 3])) == [1, 2, 3]
    assert serializer.deserialize(serializer.serialize([1, 2, 3])) != [2, 1, 3]
    assert serializer.deserialize(
        serializer.serialize([1, 2, {"key": "value", "a": [2, {1, 2}]}, {1, "2"}]),
    ) == [1, 2, {"key": "value", "a": [2, {1, 2}]}, {1, "2"}]


def test_serialize_dict(serializer):
    assert serializer.deserialize(serializer.serialize({"key": "value"})) == {"key": "value"}


def test_serialize_tuple(serializer):
    assert serializer.deserialize(serializer.serialize((1, 2, 3))) == (1, 2, 3)


def test_serialize_set(serializer):
    assert serializer.deserialize(serializer.serialize({1, 2, 3})) == {1, 2, 3}


def test_serialize_datetime(serializer):
    now = datetime.now(timezone.utc)
    assert serializer.deserialize(serializer.serialize(now)) == now


def test_serialize_timedelta(serializer):
    delta = timedelta(seconds=10)
    assert serializer.deserialize(serializer.serialize(delta)) == delta


def test_serialize_uuid(serializer):
    _uuid = uuid.uuid4()
    assert serializer.deserialize(serializer.serialize(_uuid)) == _uuid


def test_unsupported_type(serializer):
    with pytest.raises(ValueError, match="Unsupported type: <class 'object'>"):
        serializer.serialize(object())


def test_custom_type_with_pydantic(serializer):
    class Location(BaseModel):
        latitude: float
        longitude: float

    class Address(BaseModel):
        street: str
        city: str
        state: str
        zip: str
        location: Location

    class User(BaseModel):
        name: str
        age: int
        joined: datetime
        address: Address

    user = User(
        name="John",
        age=30,
        joined=datetime.now(timezone.utc),
        address=Address(
            street="123 Main St",
            city="Anytown",
            state="CA",
            zip="12345",
            location=Location(latitude=1.0, longitude=2.0),
        ),
    )
    assert isinstance(serializer.deserialize(serializer.serialize(user)), User)
    assert isinstance(serializer.deserialize(serializer.serialize(user)).address, Address)
    assert isinstance(serializer.deserialize(serializer.serialize(user)).address.location, Location)
    assert serializer.deserialize(serializer.serialize(user)) == user
    assert serializer.deserialize(serializer.serialize(user)).joined == user.joined
    assert (
        serializer.deserialize(serializer.serialize(user)).address.location.latitude
        == user.address.location.latitude
    )
    assert (
        serializer.deserialize(serializer.serialize(user)).address.location.longitude
        == user.address.location.longitude
    )


def test_serializer_none_value(serializer):
    assert serializer.deserialize(serializer.serialize(None)) is None
