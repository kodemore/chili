from dataclasses import dataclass
from typing import Union, Any, Optional

from chili import registry, HydrationStrategy


def test_union_strategy_for_primitives() -> None:
    union_strategy = registry.get_for(Union[int, float])

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

    union_strategy = registry.get_for(Union[Pet, Tag])

    assert isinstance(union_strategy.hydrate({"tag": "aa"}), Tag)
    assert isinstance(union_strategy.hydrate({"name": "Bob", "id": 1}), Pet)


def test_union_strategy_for_mixed_values() -> None:
    @dataclass()
    class Tag:
        tag: str

    union_strategy = registry.get_for(Union[str, Tag])

    assert isinstance(union_strategy.hydrate("tag"), str)
    assert isinstance(union_strategy.hydrate({"tag": 1}), Tag)


def test_hydrate_optional_custom() -> None:
    # given
    class Custom:
        def __init__(self, value: str):
            self.value = value

    class CustomStrategy(HydrationStrategy):
        def hydrate(self, value: Any) -> Any:
            return Custom(value)

        def extract(self, value: Any) -> Any:
            return value.value

    registry.add(Custom, CustomStrategy())
    strategy = registry.get_for(Optional[Custom])

    # when
    result = strategy.hydrate("hello")

    # then
    assert isinstance(result, Custom)
