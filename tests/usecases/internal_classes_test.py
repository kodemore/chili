from __future__ import annotations

from typing import List

from chili import decodable, decode, encodable, encode


def test_can_encode_internal_class() -> None:
    # given
    @encodable
    class Pet:
        class Tag:
            name: str
            value: str

            def __init__(self, name: str, value: str) -> None:
                self.name = name
                self.value = value

        name: str
        age: int
        tags: List[Tag]

        def __init__(self, name: str, age: int, tags: List[Tag]):
            self.name = name
            self.age = age
            self.tags = tags

    pet = Pet("Bobek", 11, [Pet.Tag("first", "first_value"), Pet.Tag("second", "second_value")])

    # when
    result = encode(pet)

    # then
    assert result == {
        "name": "Bobek",
        "age": 11,
        "tags": [
            {"name": "first", "value": "first_value"},
            {"name": "second", "value": "second_value"},
        ],
    }


def test_can_decode_with_internal_class() -> None:
    # given
    @decodable
    class Pet:
        class Tag:
            name: str
            value: str

            def __init__(self, name: str, value: str) -> None:
                self.name = name
                self.value = value

        name: str
        age: int
        tags: List[Tag]

        def __init__(self, name: str, age: int, tags: List[Tag]):
            self.name = name
            self.age = age
            self.tags = tags

    pet_data = {
        "name": "Bobek",
        "age": 11,
        "tags": [
            {"name": "first", "value": "first_value"},
            {"name": "second", "value": "second_value"},
        ],
    }

    # when
    pet = decode(pet_data, Pet)

    # then
    assert isinstance(pet, Pet)
    assert pet.name == "Bobek"
    assert pet.age == 11
    assert len(pet.tags) == 2
    assert pet.tags[0].name == "first"
    assert pet.tags[0].value == "first_value"
    assert pet.tags[1].name == "second"
    assert pet.tags[1].value == "second_value"
