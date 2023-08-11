from collections import namedtuple
from typing import NamedTuple

from chili import decode, encode


def test_can_encode_namedtuple() -> None:
    # given
    Pet = namedtuple("Pet", ["age", "name"])

    # when
    result = encode(Pet(1, "Bob"))

    # then
    assert result == [1, "Bob"]


def test_can_decode_namedtuple() -> None:
    # given
    Pet = namedtuple("Pet", ["age", "name"])

    # when
    result = decode([1, "Bob"], Pet)

    # then
    assert result == Pet(1, "Bob")


def test_can_encode_namedtuple_as_class() -> None:
    # given
    class Pet(NamedTuple):
        age: int
        name: str

    # when
    result = encode(Pet(1, "Bob"))

    # then
    assert result == [1, "Bob"]


def test_can_decode_namedtuple_as_class() -> None:
    # given
    class Pet(NamedTuple):
        age: int
        name: str

    # when
    result = decode(["1", "Bob"], Pet)

    # then
    assert result == Pet(1, "Bob")
