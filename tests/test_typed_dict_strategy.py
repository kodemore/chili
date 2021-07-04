from typing import List
from typing_extensions import TypedDict

from chili.dataclasses import get_strategy_for


def test_hydrate_generic_typed_dict() -> None:
    # given
    strategy = get_strategy_for(TypedDict)  # <- I know this does not make sense
    input_data = {"int": 1, "float": 2.2, "bool": True, "string": "Hello"}

    # when
    result = strategy.hydrate(
        input_data
    )  # <- But we still should be able to handle it gracefully

    # then
    assert result == {"int": 1, "float": 2.2, "bool": True, "string": "Hello"}


def test_hydrate_typed_dict() -> None:
    class Pet(TypedDict):
        age: int
        name: str
        tags: List[str]

    # given
    strategy = get_strategy_for(Pet)

    input_data = {"age": "4", "name": "Bobek", "tags": [True, "dog", "pet"]}

    # when
    result = strategy.hydrate(input_data)

    # then
    assert isinstance(result, dict)
    assert result == {"age": 4, "name": "Bobek", "tags": ["True", "dog", "pet"]}


def test_extract_typed_dict() -> None:
    class Pet(TypedDict):
        age: int
        name: str
        tags: List[str]

    # given
    strategy = get_strategy_for(Pet)

    input_data = {"age": "4", "name": "Bobek", "tags": tuple([True, "dog", "pet"])}

    # when
    result = strategy.extract(input_data)

    # then
    assert isinstance(result, dict)
    assert result == {"age": 4, "name": "Bobek", "tags": ["True", "dog", "pet"]}
