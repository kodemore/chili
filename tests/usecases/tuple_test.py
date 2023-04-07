from typing import Tuple

from chili import decode, encode


def test_can_decode_typed_tuple() -> None:
    # given
    values = [1, 2, 3]

    # when
    result = decode(values, Tuple[int, int, int])

    # then
    assert result == (1, 2, 3)


def test_can_decode_variadic_typed_tuple() -> None:
    # given
    values = [1, 2, 3, 4]

    # when
    result = decode(values, Tuple[int, ...])

    # then
    assert result == (1, 2, 3, 4)


def test_can_encode_typed_tuple() -> None:
    # given
    values = (1, 2, 3)

    # when
    result = encode(values, Tuple[int, int, int])

    # then
    assert result == [1, 2, 3]


def test_can_code_variadic_tuple() -> None:
    # given
    values = (1, 2, 3, 4)

    # when
    result = encode(values, Tuple[str, ...])

    # then
    assert result == ["1", "2", "3", "4"]
