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


def test_union_simple_type_or_dataclass() -> None:
    # given
    @dataclass
    class EmailAddress:
        address: str
        label: str

    value = "simple@email.com"
    complex_value = {"address": "simple@email.com", "label": ""}

    # when
    result = decode(value, Union[str, EmailAddress])

    # then
    assert result == "simple@email.com"

    # when
    result = decode(complex_value, Union[str, EmailAddress])

    # then
    assert isinstance(result, EmailAddress)


def test_new_union_style_decode() -> None:
    # given
    @dataclass
    class EmailAddress:
        address: str
        label: str

    value = "simple@email.com"
    complex_value = {"address": "simple@email.com", "label": ""}

    # when
    result = decode(value, str | EmailAddress)

    # then
    assert result == "simple@email.com"

    # when
    result = decode(complex_value, str | EmailAddress)

    # then
    assert isinstance(result, EmailAddress)


def test_new_union_style_encode() -> None:
    # given
    @dataclass
    class EmailAddress:
        address: str
        label: str

    value = "simple@email.com"
    complex_value = {"address": "simple@email.com", "label": ""}

    # when
    result = encode(value, str | EmailAddress)

    # then
    assert result == "simple@email.com"

    # when
    result = encode(EmailAddress(address="simple@email.com", label=""), str | EmailAddress)

    # then
    assert result == {"address": "simple@email.com", "label": ""}
