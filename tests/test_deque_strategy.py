from collections import deque
from typing import Deque

from chili import registry


def test_hydrate_generic_deque() -> None:
    # given
    strategy = registry.get_for(deque)
    items = ["a", 1, 2.1, True]

    # when
    hydrated_items = strategy.hydrate(items)

    # then
    assert isinstance(hydrated_items, deque)
    assert hydrated_items == deque(["a", 1, 2.1, True])


def test_hydrate_annotated_deque() -> None:
    # given
    strategy = registry.get_for(Deque[str])
    items = ["a", 1, 2.1, True]

    # when
    hydrated_items = strategy.hydrate(items)

    # then
    assert isinstance(hydrated_items, deque)
    assert hydrated_items == deque(["a", "1", "2.1", "True"])


def test_extract_generic_deque() -> None:
    # given
    strategy = registry.get_for(deque)
    items = deque(["a", 1, 2.1])

    # when
    result = strategy.extract(items)

    # then
    assert isinstance(result, list)
    assert set(result) == set(["a", 1, 2.1])


def test_extract_annotated_deque() -> None:
    # given
    strategy = registry.get_for(Deque[str])
    items = deque(["a", 1, 2.1])

    # when
    result = strategy.extract(items)

    # then
    assert isinstance(result, list)
    assert set(result) == set(["a", "1", "2.1"])
