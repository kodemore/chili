from chili.dataclasses import get_strategy_for
from typing import Union
from dataclasses import dataclass


def test_union_strategy_for_primitives() -> None:
    union_strategy = get_strategy_for(Union[int, float])

    hydrated_int = union_strategy.hydrate("12")
    hydrated_float = union_strategy.hydrate("12.21")

    assert isinstance(hydrated_int, int)
    assert isinstance(hydrated_float, float)

    union_strategy.extract(12)


def test_union_strategy_for_dataclasses() -> None:
    @dataclass()
    class Pet:
        id: str
        name: str

    @dataclass()
    class Tag:
        tag: str

    union_strategy = get_strategy_for(Union[Pet, Tag])

    assert isinstance(union_strategy.hydrate({"tag": "aa"}), Tag)
    assert isinstance(union_strategy.hydrate({"name": "Bob", "id": 1}), Pet)


def test_union_strategy_for_mixed_values() -> None:
    @dataclass()
    class Tag:
        tag: str

    union_strategy = get_strategy_for(Union[str, Tag])

    assert isinstance(union_strategy.hydrate("tag"), str)
    assert isinstance(union_strategy.hydrate({"tag": 1}), Tag)
