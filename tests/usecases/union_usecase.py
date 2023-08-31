from dataclasses import dataclass
from typing import List, Union

from chili import decode, encode


def test_union_with_dataclasses() -> None:
    @dataclass
    class Parent:
        foo: int

    @dataclass
    class Child(Parent):
        bar: str

    before: List[Parent] = [Parent(3), Child(5, "hi")]
    encoded = encode(before, List[Union[Parent, Child]])
    after = decode(encoded, List[Union[Parent, Child]])

    assert isinstance(after[0], Parent)
    assert isinstance(after[1], Child)
