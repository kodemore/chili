import re
from dataclasses import dataclass
from enum import Enum
from typing import Generic, List, Optional, Pattern, TypeVar, Union

import pytest

from chili import decodable, decode
from chili.decoder import decode_regex_from_string
from chili.error import DecoderError


def test_can_decode_dataclass() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int
        favourite_food: List[str]

    data = {"name": "Fido", "age": 3, "favourite_food": [7, "bones"]}

    # when
    result = decode(data, Pet)

    # then
    assert isinstance(result, Pet)
    assert result.name == "Fido"
    assert result.age == 3
    assert result.favourite_food == ["7", "bones"]


def test_can_decode_dataclass_with_optional() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int
        favourite_food: List[str]
        owner: str = None

    data = {"name": "Fido", "age": 3, "favourite_food": [7, "bones"]}

    # when
    result = decode(data, Pet)

    # then
    assert isinstance(result, Pet)
    assert result.name == "Fido"
    assert result.age == 3
    assert result.favourite_food == ["7", "bones"]
    assert result.owner is None


def test_can_decode_optional_str() -> None:
    # given
    data = None

    # when
    result = decode(data, Optional[str])

    # then
    assert result is None


def test_can_decode_generic_dataclass() -> None:
    # given
    T = TypeVar("T")

    @dataclass
    class Pet(Generic[T]):
        name: str
        age: int
        favourites: List[T]

    data = {"name": "Fido", "age": 3, "favourites": [7, "8"]}

    # when
    result = decode(data, Pet[int])

    # then
    assert isinstance(result, Pet)
    assert all(isinstance(favourite, int) for favourite in result.favourites)

    # when
    result = decode(data, Pet[str])

    # then
    assert isinstance(result, Pet)
    assert all(isinstance(favourite, str) for favourite in result.favourites)


def test_can_decode_union_dataclass_types() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int

    @dataclass
    class Person:
        name: str
        age: int
        address: str

    pet_data = {"name": "Fido", "age": 3}
    person_data = {"name": "Fido", "age": 3, "address": "123 Fake Street"}

    # when
    person = decode(person_data, Union[Pet, Person])
    pet = decode(pet_data, Union[Pet, Person])

    # then
    assert isinstance(person, Person)
    assert isinstance(pet, Pet)


def test_decode_union_decodables() -> None:
    # given
    @decodable
    class Pet:
        name: str
        age: int

    @decodable
    class Person:
        name: str
        age: int
        address: str

    person_data = {"name": "Bobik", "age": 3, "address": "123 Fake Street"}
    pet_data = {"name": "Bobik", "age": 3}

    # when
    person = decode(person_data, Union[Pet, Person])
    pet = decode(pet_data, Union[Pet, Person])

    assert isinstance(person, Person)
    assert isinstance(pet, Pet)


def test_can_decode_str_enum() -> None:
    # given
    class PetType(str, Enum):
        DOG = "dog"
        CAT = "cat"

    data = "dog"

    # when
    result = decode(data, PetType)

    # then
    assert result == PetType.DOG


def test_fail_decode_str_enum() -> None:
    # given
    class PetType(str, Enum):
        DOG = "dog"
        CAT = "cat"

    data = "fish"

    # when
    with pytest.raises(ValueError):
        decode(data, PetType)


def test_fail_decode_int_enum() -> None:
    # given
    class PetType(int, Enum):
        DOG = 1
        CAT = 2

    data = 3

    # when
    with pytest.raises(ValueError):
        decode(data, PetType)


def test_decode_regex_from_str() -> None:
    # given
    value = r"\d+"

    # when
    result = decode_regex_from_string(value)

    # then
    assert isinstance(result, Pattern)


def test_decode_regex_with_flags_from_str() -> None:
    # given
    value = r"/\d+/ismx"

    # when
    result = decode_regex_from_string(value)

    # then
    assert isinstance(result, Pattern)
    assert result.pattern == "\d+"
    assert result.flags & re.I
    assert result.flags & re.M
    assert result.flags & re.S
    assert result.flags & re.X


def test_can_decode_incomplete_object_with_optional_property() -> None:
    # given
    @decodable
    class Tag:
        value: Optional[str]

        def __init__(self, value: str):
            self.value = value

    @decodable
    class Pet:
        name: str
        age: int
        tags: List[Tag]

    pet_data = {"name": "Bobik", "age": 3, "tags": [{"_": "value"}]}

    # when
    pet = decode(pet_data, Pet)

    # then
    assert isinstance(pet, Pet)
    assert isinstance(pet.tags[0], Tag)
    assert pet.tags[0].value is None


def test_fail_to_decode_incomplete_object() -> None:
    # given
    @decodable
    class Tag:
        value: str

        def __init__(self, value: str):
            self.value = value

    @decodable
    class Pet:
        name: str
        age: int
        tags: List[Tag]

    pet_data = {"name": "Bobik", "age": 3, "tags": [{"_": "invalid_tag"}]}

    # when
    with pytest.raises(DecoderError.missing_property):
        decode(pet_data, Pet)
