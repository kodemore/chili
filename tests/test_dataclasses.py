from dataclasses import dataclass, field
from typing import Generic, List, TypeVar
from unittest.mock import patch, MagicMock

import pytest

import chili.dataclasses
from chili import asdict, init_dataclass


def test_can_make_simple_dataclass() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int
        tags: List[str]

    # when
    pet = init_dataclass({"name": "Bobek", "age": 4, "tags": ["1", "a", "True"]}, Pet)

    # then
    assert isinstance(pet, Pet)
    assert pet.name == "Bobek"
    assert pet.age == 4
    assert len(pet.tags) == 3
    for tag in pet.tags:
        assert isinstance(tag, str)


def test_can_make_nested_dataclasses() -> None:
    # given
    @dataclass
    class Tag:
        name: str

    @dataclass
    class Pet:
        name: str
        age: int
        tags: List[Tag]

    # when
    pet = init_dataclass(
        {"name": "Bobek", "age": 4, "tags": [{"name": "Cat"}, {"name": "Brown"}]}, Pet
    )

    # then
    assert isinstance(pet, Pet)
    assert pet.name == "Bobek"
    assert pet.age == 4
    assert len(pet.tags) == 2
    assert isinstance(pet.tags[0], Tag)
    assert pet.tags[0].name == "Cat"
    assert pet.tags[1].name == "Brown"


def test_can_extract_nested_dataclasses() -> None:
    # given
    @dataclass
    class Tag:
        name: str

    @dataclass
    class Pet:
        name: str
        age: int
        tags: List[Tag]

    json = {"name": "Bobek", "age": 4, "tags": [{"name": "Cat"}, {"name": "Brown"}]}
    pet = init_dataclass(json, Pet)

    # when
    data = asdict(pet)

    # then
    assert data == {
        "name": "Bobek",
        "age": 4,
        "tags": [
            {"name": "Cat"},
            {"name": "Brown"},
        ],
    }


def test_fail_make_with_missing_property() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int

    # when
    with pytest.raises(AttributeError) as error:
        init_dataclass({"name": "Bobek"}, Pet)

    # then
    assert str(error.value) == "Property `age` is required."


def test_make_with_default_values() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int = 10
        tags: list = field(default_factory=list)

    # when
    pet = init_dataclass({"name": "Bobek"}, Pet)

    # then
    assert pet.name == "Bobek"
    assert pet.age == 10
    assert isinstance(pet.tags, list)


def test_can_make_nested_dataclasses_from_generic_parent() -> None:
    # given
    T = TypeVar("T")

    @dataclass
    class Item:
        id: int

    @dataclass
    class Parent(Generic[T]):
        items: List[T]

    @dataclass
    class Child(Parent, Generic[T]):
        name: str

    # when
    example = init_dataclass(
        {
            "name": "Example One",
            "items": [
                {
                    "id": 1,
                },
                {
                    "id": 2,
                },
            ],
        },
        Child[Item],
    )

    # then
    assert isinstance(example, Child)
    assert example.name == "Example One"
    assert len(example.items) == 2
    item1 = example.items[0]
    item2 = example.items[1]
    assert isinstance(item1, Item)
    assert item1.id == 1
    assert isinstance(item2, Item)
    assert item2.id == 2


def test_init_dataclass_supports_init_false_fields() -> None:
    # given
    @dataclass
    class Collection:
        items: List[int]
        total: int = field(init=False)

        def __post_init__(self):
            self.total = len(self.items)

    # when
    collection = init_dataclass({"items": [1, 2, 3]}, Collection)
    extracted_data = asdict(collection)

    # then
    assert isinstance(collection, Collection)
    assert len(collection.items) == 3
    assert collection.total == 3

    assert extracted_data["total"] == 3
    assert extracted_data["items"] == [1, 2, 3]


def test_init_dataclass_supports_repr_false_fields() -> None:
    # given
    @dataclass
    class Collection:
        items: List[int]
        total: int = field(init=False, repr=False)

        def __post_init__(self):
            self.total = len(self.items)

    # when
    collection = Collection(items=[1, 2, 3])
    extracted_data = asdict(collection)

    # then
    assert isinstance(extracted_data, dict)
    assert extracted_data["items"] == [1, 2, 3]
    assert "total" not in extracted_data


def test_fails_hydration_on_non_dataclass() -> None:
    # given
    data = {"a": 1}

    # then
    with pytest.raises(TypeError):
        init_dataclass(data, int)


def test_fails_extraction_on_non_dataclass() -> None:
    # given
    data = {"a": 1}

    # then
    with pytest.raises(TypeError):
        asdict(data)


def test_uses_cache_when_initialising_dataclass() -> None:
    # given
    @dataclass
    class Item:
        id: int
    cache_storage = {}

    # when
    with patch("chili.hydration.registry._cached") as cache:
        cache.__getitem__.side_effect = cache_storage.__getitem__
        cache.__contains__.side_effect = cache_storage.__contains__
        cache.__setitem__.side_effect = cache_storage.__setitem__

        assert Item not in cache

        # then
        init_dataclass({"id": 12}, Item)
        assert Item in cache

        init_dataclass({"id": 12}, Item)  # same init to use cache

        cache.__getitem__.assert_called_with(Item)
        assert cache.__getitem__.call_count == 2


