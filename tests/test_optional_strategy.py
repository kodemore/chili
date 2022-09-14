from dataclasses import dataclass
from typing import Any, Optional, Type

import pytest

from chili import registry


@dataclass
class Pet:
    name: str
    age: int


@pytest.mark.parametrize(
    "typedef, passed_input, expected_output",
    [
        [Optional[Pet], {"name": "Bobek", "age": 12}, Pet("Bobek", 12)],
        [Optional[Pet], None, None],
        [Optional[int], None, None],
        [Optional[int], 0, 0],
        [Optional[int], 1, 1],
        [Optional[bool], None, None],
        [Optional[bool], True, True],
    ],
)
def test_hydrate_optional_types(typedef: Type, passed_input: Any, expected_output: Any) -> None:
    # given
    strategy = registry.get_for(typedef)

    # when
    result = strategy.hydrate(passed_input)

    # then
    assert result == expected_output
