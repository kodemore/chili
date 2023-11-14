from dataclasses import dataclass
from typing import Optional

from chili.typing import get_non_optional_fields


def test_get_non_optional_fields_from_data_class() -> None:
    # given
    @dataclass
    class Person:
        name: str
        age: int
        street_name: Optional[str]
        street_number: Optional[int]

    # when
    fields = get_non_optional_fields(Person)

    # then
    assert fields == ["name", "age"]


def test_get_non_optional_fields_from_class() -> None:
    class Person:
        name: str
        age: int
        street_name: Optional[str]
        street_number: Optional[int]

    # when
    fields = get_non_optional_fields(Person)

    # then
    assert fields == ["name", "age"]
