from typing import Set

from chili import registry


def test_hydrate_generic_set() -> None:
    # given
    strategy = registry.get_for(set)
    items = ["a", 1, 2.1, True]

    # when
    hydrated_items = strategy.hydrate(items)

    # then
    assert hydrated_items == {"a", 1, 2.1}


def test_hydrate_annotated_set() -> None:
    # given
    strategy = registry.get_for(Set[str])
    items = ["a", 1, 2.1, True]

    # when
    hydrated_items = strategy.hydrate(items)

    # then
    assert hydrated_items == {"a", "1", "2.1", "True"}


def test_extract_generic_set() -> None:
    # given
    strategy = registry.get_for(set)
    items = {"a", 1, 2.1}

    # when
    result = strategy.extract(items)

    # then
    assert isinstance(result, list)
    assert set(result) == set(["a", 1, 2.1])


def test_extract_annotated_set() -> None:
    # given
    strategy = registry.get_for(Set[str])
    items = {"a", 1, 2.1}

    # when
    result = strategy.extract(items)

    # then
    assert isinstance(result, list)
    assert set(result) == set(["a", "1", "2.1"])
