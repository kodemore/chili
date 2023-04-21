from dataclasses import dataclass
from typing import TypeVar

import pytest

from chili import Encoder, Decoder


def test_can_encode_bound_typevar() -> None:
    # given
    Id = TypeVar("Id", bound=str)

    @dataclass
    class Platform:
        id: Id
        name: str

    decoder = Encoder[Platform]()
    platform = Platform("1", "Test")

    # when
    result = decoder.encode(platform)

    # then
    assert isinstance(result, dict)
    assert result == {"id": "1", "name": "Test"}


def test_fail_encode_generic_non_typed_typevar() -> None:
    # given
    Id = TypeVar("Id")

    @dataclass
    class Platform:
        id: Id
        name: str

    decoder = Encoder[Platform]()
    platform = Platform("1", "Test")

    # when
    with pytest.raises(TypeError):
        decoder.encode(platform)


def test_can_decode_bound_typevar() -> None:
    # given
    Id = TypeVar("Id", bound=str)

    @dataclass
    class Platform:
        id: Id
        name: str

    decoder = Decoder[Platform]()
    data = {"id": "1", "name": "Test"}

    # when
    result = decoder.decode(data)

    # then
    assert isinstance(result, Platform)
    assert result.id == "1"
    assert result.name == "Test"


def test_fail_decode_generic_non_typed_typevar() -> None:
    # given
    Id = TypeVar("Id")

    @dataclass
    class Platform:
        id: Id
        name: str

    decoder = Decoder[Platform]()
    data = {"id": "1", "name": "Test"}

    # when
    with pytest.raises(TypeError):
        decoder.decode(data)
