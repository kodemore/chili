from dataclasses import dataclass
from typing import List

from chili import encode


def test_can_encode_typed_list() -> None:
    # when
    values = encode([1, "2", 3.1], List[int])

    # then
    assert values == [1, 2, 3]


def test_can_encode_typed_list_of_dataclasses() -> None:
    # given
    @dataclass
    class Pet:
        age: int
        name: str

    # when
    values = encode([Pet(1, "Bob"), Pet(2, "Alice")], List[Pet])

    # then
    assert values == [{"age": 1, "name": "Bob"}, {"age": 2, "name": "Alice"}]

