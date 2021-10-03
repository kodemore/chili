from typing import List, Optional

from chili import registry
from chili.hydration import DummyStrategy, ListStrategy, OptionalTypeStrategy


def test_use_dummy_strategy_for_unknown_type() -> None:
    # given
    class SomeUnknownType:
        def __init__(self, value: str):
            self.value = value

    obj = SomeUnknownType("test")

    # when
    unknown_strategy = registry.get_for(SomeUnknownType)

    # then
    assert isinstance(unknown_strategy, DummyStrategy)
    assert obj == unknown_strategy.hydrate(obj)
    assert obj == unknown_strategy.extract(obj)


def test_use_dummy_strategy_for_list_of_unknown_type() -> None:
    # given
    class SomeUnknownType:
        def __init__(self, value: str):
            self.value = value

    obj = SomeUnknownType("test")

    # when
    unknown_strategy = registry.get_for(List[SomeUnknownType])

    # then
    assert isinstance(unknown_strategy, ListStrategy)
    assert [obj] == unknown_strategy.hydrate([obj])
    assert [obj] == unknown_strategy.extract([obj])


def test_use_dummy_strategy_for_optional_of_unknown_type() -> None:
    # given
    class SomeUnknownType:
        def __init__(self, value: str):
            self.value = value

    obj = SomeUnknownType("test")

    # when
    unknown_strategy = registry.get_for(Optional[SomeUnknownType])

    # then
    assert isinstance(unknown_strategy, OptionalTypeStrategy)
    assert obj == unknown_strategy.hydrate(obj)
    assert obj == unknown_strategy.extract(obj)
    assert None is unknown_strategy.hydrate(None)
    assert None is unknown_strategy.extract(None)
