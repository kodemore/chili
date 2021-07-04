from collections import namedtuple
from typing import List, NamedTuple, Tuple

from chili.dataclasses import get_strategy_for


def test_hydrate_named_tuple() -> None:
    # given
    Pet = namedtuple("Pet", ["age", "name"])
    strategy = get_strategy_for(Pet)

    # when
    pet = strategy.hydrate([12, "Bobek"])

    # then
    assert isinstance(pet, Pet)
    assert pet.age == 12
    assert pet.name == "Bobek"


def test_hydrate_named_tuple_with_defaults() -> None:
    # given
    Pet = namedtuple("Pet", ["age", "name", "tags"], defaults=[0, None, []])
    strategy = get_strategy_for(Pet)

    # when
    pet = strategy.hydrate([12])

    # then
    assert pet.age == 12
    assert pet.name is None
    assert pet.tags == []


def test_hydrate_class_based_named_tuple() -> None:
    # given
    class Pet(NamedTuple):
        age: int
        name: str
        tags: list = []

    strategy = get_strategy_for(Pet)

    # when
    pet = strategy.hydrate(["10", "Bobek"])

    # then
    assert pet.age == 10
    assert pet.name == "Bobek"
    assert pet.tags == []


def test_extract_named_tuple() -> None:
    # given
    Pet = namedtuple("Pet", ["age", "name"])
    strategy = get_strategy_for(Pet)

    # when
    result = strategy.extract(Pet(12, "Bobek"))

    # then
    assert result[0] == 12
    assert result[1] == "Bobek"


def test_extract_class_based_tuple() -> None:
    # given
    class Pet(NamedTuple):
        age: int
        name: str
        tags: List[int] = []

    strategy = get_strategy_for(Pet)

    # when
    result = strategy.extract(Pet("10", "Bobek", ["0"]))

    # then
    assert result[0] == 10
    assert result[1] == "Bobek"
    assert result[2] == [0]
