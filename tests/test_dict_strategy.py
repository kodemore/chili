from typing import Dict

from chili.dataclasses import get_strategy_for


def test_hydrate_generic_dict() -> None:
    # given
    strategy = get_strategy_for(Dict)
    input_data = {"int": 1, "float": 2.2, "bool": True, "string": "Hello"}

    # when
    result = strategy.hydrate(input_data)

    # then
    assert result == {"int": 1, "float": 2.2, "bool": True, "string": "Hello"}


def test_hydrate_built_in_dict() -> None:
    # given
    strategy = get_strategy_for(dict)
    input_data = {"int": 1, "float": 2.2, "bool": True, "string": "Hello"}

    # when
    result = strategy.hydrate(input_data)

    # then
    assert result == {"int": 1, "float": 2.2, "bool": True, "string": "Hello"}


def test_hydrate_annotated_dict() -> None:
    # given
    strategy = get_strategy_for(Dict[str, str])
    input_data = {"int": 1, "float": 2.2, "bool": True, "string": "Hello"}

    # when
    result = strategy.hydrate(input_data)

    # then
    assert result == {"int": "1", "float": "2.2", "bool": "True", "string": "Hello"}


def test_extract_annotated_dict() -> None:
    # given
    strategy = get_strategy_for(Dict[str, str])
    input_data = {"int": 1, "float": 2.2, "bool": True, "string": "Hello"}

    # when
    hydrated_data = strategy.extract(input_data)

    # then
    assert hydrated_data == {
        "int": "1",
        "float": "2.2",
        "bool": "True",
        "string": "Hello",
    }
