from dataclasses import InitVar
from typing import ClassVar

from chili import encodable, encode


def test_can_encode_and_ignore_classvar_attributes() -> None:

    # given
    @encodable
    class Pet:
        name: str
        age: int
        value: ClassVar[str] = "ignored"

        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

    example_obj = Pet("Bob", 11)

    # when
    state = encode(example_obj)

    # then
    assert state == {
        "name": "Bob",
        "age": 11,
    }


def test_can_encode_and_ignore_initvar_attributes() -> None:

    # given
    @encodable
    class Pet:
        name: str
        age: int
        value: InitVar[str]

        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age
            self.value = "ignored"

    example_obj = Pet("Bob", 11)

    # when
    state = encode(example_obj)

    # then
    assert state == {
        "name": "Bob",
        "age": 11,
    }
