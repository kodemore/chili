from dataclasses import dataclass
from typing import List, Sequence, Type

import pytest

from chili import registry


@pytest.mark.parametrize("list_type", [list, List, Sequence])
def test_hydrate_generic_list(list_type: Type) -> None:
    # given
    strategy = registry.get_for(list_type)
    list_items = ["a", 1, 2.1, True]

    # when
    mixed_list = strategy.hydrate(list_items)

    # then
    assert mixed_list == list_items


def test_hydrate_typed_list() -> None:
    # given
    strategy = registry.get_for(List[str])
    list_items = ["a", 1, 2.1, True]

    # when
    mixed_list = strategy.hydrate(list_items)

    # then
    assert mixed_list == ["a", "1", "2.1", "True"]


def test_hydrate_list_of_dataclasses() -> None:
    # given
    @dataclass
    class Point:
        x: int
        y: int

    strategy = registry.get_for(List[Point])

    # when
    hydrated = strategy.hydrate([{"x": 1, "y": 1}, {"x": 2, "y": 1}, {"x": 2, "y": 2}])

    # then
    for item in hydrated:
        assert isinstance(item, Point)

    assert hydrated[0].x == 1
    assert hydrated[0].y == 1
    assert hydrated[1].x == 2
    assert hydrated[1].y == 1


def test_extract_list() -> None:
    # given
    @dataclass
    class Point:
        x: int
        y: int

    strategy = registry.get_for(List[Point])
    list_of_points = [Point(1, 1), Point(1, 2), Point(2, 2)]

    # when
    extracted_list = strategy.extract(list_of_points)

    # then
    assert len(extracted_list) == 3
    for item in extracted_list:
        assert isinstance(item, dict)

    assert extracted_list[0]["x"] == 1
    assert extracted_list[0]["y"] == 1
    assert extracted_list[1]["x"] == 1
    assert extracted_list[1]["y"] == 2
