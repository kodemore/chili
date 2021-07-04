from typing import FrozenSet

from chili.dataclasses import get_strategy_for


def test_hydrate_generic_frozenset() -> None:
    # given
    strategy = get_strategy_for(frozenset)
    items = ["a", 1, 2.1, True]

    # when
    hydrated_items = strategy.hydrate(items)

    # then
    assert isinstance(hydrated_items, frozenset)
    assert hydrated_items == {"a", 1, 2.1}


def test_hydrate_annotated_frozenset() -> None:
    # given
    strategy = get_strategy_for(FrozenSet[str])
    items = ["a", 1, 2.1, True]

    # when
    hydrated_items = strategy.hydrate(items)

    # then
    assert isinstance(hydrated_items, frozenset)
    assert hydrated_items == {"a", "1", "2.1", "True"}


def test_extract_generic_frozenset() -> None:
    # given
    strategy = get_strategy_for(set)
    items = frozenset(["a", 1, 2.1])

    # when
    result = strategy.extract(items)

    # then
    assert isinstance(result, list)
    assert set(result) == set(["a", 1, 2.1])


def test_extract_annotated_frozenset() -> None:
    # given
    strategy = get_strategy_for(FrozenSet[str])
    items = frozenset(["a", 1, 2.1])

    # when
    result = strategy.extract(items)

    # then
    assert isinstance(result, list)
    assert set(result) == set(["a", "1", "2.1"])
