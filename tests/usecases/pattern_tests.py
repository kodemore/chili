import re
from typing import Pattern

from chili import encode, decode


def test_can_encode_pattern() -> None:
    # given
    pattern = re.compile("[a-z0-9]+")

    # when
    result = encode(pattern)

    # then
    assert result == "[a-z0-9]+"


def test_can_encode_pattern_with_flags() -> None:
    # given
    pattern = re.compile("[a-z0-9]+", flags=re.I|re.M|re.S|re.X)

    # when
    result = encode(pattern)

    # then
    assert result == "/[a-z0-9]+/imsx"


def test_can_decode_with_im_flags() -> None:
    # given
    pattern = "/[a-z0-9]+/im"

    # when
    result = decode(pattern, Pattern)

    # then
    assert isinstance(result, Pattern)
    assert result.flags & re.I
    assert result.flags & re.M


def test_can_decode_without_flags() -> None:
    # given
    pattern = "/[a-z0-9]+/"

    # when
    result = decode(pattern, Pattern)

    # then
    assert isinstance(result, Pattern)
    assert result.pattern == "[a-z0-9]+"


def test_can_decode_without_flags_without_slashes() -> None:
    # given
    pattern = "[a-z0-9]+"

    # when
    result = decode(pattern, Pattern)

    # then
    assert isinstance(result, Pattern)
    assert result.pattern == pattern
