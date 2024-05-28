import datetime
import enum
import re
import sys
from collections import namedtuple
from dataclasses import dataclass
from typing import Generic, List, Optional, Set, Tuple, TypedDict, TypeVar

import pytest

from chili import encodable, encode
from chili.encoder import encode_regex_to_string


@pytest.mark.parametrize(
    "a_type, given, expected",
    [
        (int, "1", 1),
        (int, 1, 1),
        (int, True, 1),
        (int, False, 0),
        (int, b"12", 12),
        (int, 10.21, 10),
        (str, "a", "a"),
        (str, 1, "1"),
        (str, True, "True"),
        (str, 10.21, "10.21"),
        (float, "1.2", 1.2),
        (float, b"1.2", 1.2),
        (bool, "", False),
        (bool, b"", False),
        (bool, 1, True),
        (bool, 1.2, True),
        (bytes, b"", ""),
        (bytes, b"123", "MTIz"),
        (list, [1, 2, 3], [1, 2, 3]),
        (List, [1, 2, 3], [1, 2, 3]),
        (set, {1, 2, 3}, [1, 2, 3]),
        (Set, {1, 2, 3}, [1, 2, 3]),
        (tuple, (1, 2, 3), [1, 2, 3]),
        (Tuple, (1, 2, 3), [1, 2, 3]),
    ],
)
def test_can_encode_primitive(a_type, given, expected) -> None:
    # when
    result = encode(given, a_type)

    # then
    assert result == expected


def test_encode_typed_list() -> None:
    # when
    values = encode([1, "2", 3.1], List[int])

    # then
    assert values == [1, 2, 3]


def test_encode_dataclass() -> None:
    # given
    @dataclass
    class Pet:
        age: int
        name: str
        favs: List[str]

    fluffy = Pet(10, "Fluffy", ["bone", "ball"])

    # when
    result = encode(fluffy)

    # then
    assert result == {"age": 10, "name": "Fluffy", "favs": ["bone", "ball"]}


def test_encode_enum() -> None:
    # given
    class Colours(enum.Enum):
        RED = "RED"
        GREEN = "GREEN"
        BLUE = "BLUE"

    colour = Colours.RED

    # when
    result = encode(colour)

    # then
    assert result == "RED"


def test_can_encode_empty_encodable_type() -> None:
    # given
    @encodable
    class Example:
        pass

    example_obj = Example()

    # when
    state = encode(example_obj)

    # then
    assert state == {}


def test_can_encode_simple_encodable_type() -> None:
    # given
    @encodable
    class Example:
        name: str
        age: int

        def __init__(self, name: str):
            self.name = name
            self.age = 0

    example_obj = Example("Bob")

    # when
    state = encode(example_obj)

    # then
    assert state == {
        "name": "Bob",
        "age": 0,
    }


def test_can_encode_nested_encodables() -> None:
    # given
    @encodable
    class Child:
        name: str
        value: str

        def __init__(self, name: str, value: str = ""):
            self.name = name
            self.value = value

    @encodable
    class Parent:
        name: str
        children: List[Child]

        def __init__(self, name: str):
            self.name = name
            self.children = []

    unit = Parent("Bob")
    unit.children.append(Child("first"))
    unit.children.append(Child("second_value", "second"))

    # when
    result = encode(unit)

    # then
    assert result == {
        "name": "Bob",
        "children": [
            {"name": "first", "value": ""},
            {"name": "second_value", "value": "second"},
        ],
    }


def test_encode_named_tuple() -> None:
    # given
    Pet = namedtuple("Pet", ["age", "name"])
    pet = Pet(11, "Bobek")

    # when
    result = encode(pet)

    # then
    assert result == [11, "Bobek"]


def test_encode_generic_type() -> None:
    # given
    T = TypeVar("T")

    @dataclass
    class MyList(Generic[T]):
        count: int
        pets: List[T]

    @dataclass
    class Pet:
        name: str
        age: int

    # when
    result = encode(MyList(2, [Pet("Pimpek", 2), Pet("Bobik", 5)]), MyList[Pet])

    # then
    assert result == {
        "count": 2,
        "pets": [
            {"name": "Pimpek", "age": 2},
            {"name": "Bobik", "age": 5},
        ],
    }


def test_encode_optional_type() -> None:
    # given
    a_type = Optional[int]

    # when
    value = encode(None, a_type)

    # then
    assert value is None

    # when
    value = encode("12", a_type)

    # then
    assert value == 12


def test_encode_defined_typed_dict() -> None:
    # given
    class Pet(TypedDict):
        age: int
        name: str

    # when
    result = encode(Pet(age=11, name="Bobik"))

    # then
    assert result == {"age": 11, "name": "Bobik"}


def test_encode_generic_typed_dict() -> None:
    # when
    result = encode(dict(age=11, name="Bobik"))

    # then
    assert result == {"age": 11, "name": "Bobik"}


def test_encode_date() -> None:
    # given
    date = datetime.date(year=2010, month=10, day=1)

    # when
    result = encode(date)

    # then
    assert result == "2010-10-01"


def test_encode_time() -> None:
    # given
    time = datetime.time(hour=15, minute=21, second=11)

    # when
    result = encode(time)

    # then
    assert result == "15:21:11"


def test_extract_timedelta() -> None:
    # given
    time = datetime.timedelta(days=10, seconds=7200)

    # when
    result = encode(time)

    # then
    assert result == "P1W3DT2H"


def test_can_encode_regex_into_string() -> None:
    # given
    pattern_str = "[a-z0-9]+"
    pattern = re.compile(pattern_str)

    # when
    result = encode_regex_to_string(pattern)

    # then
    assert result == pattern_str


def test_can_encode_regex_with_flags_into_string() -> None:
    # given
    pattern_str = "[a-z0-9]+"
    pattern = re.compile(pattern_str, flags=re.I | re.M | re.S | re.X)

    # when
    result = encode_regex_to_string(pattern)

    # then
    assert result == f"/{pattern_str}/imsx"


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="Unsupported python version")
def test_can_encode_new_optional_type_notation() -> None:
    # given
    @encodable
    class Tag:
        value: int | None

        def __init__(self, value: int | None):
            self.value = value

    tag = Tag(None)
    alt_tag = Tag(11)

    # when
    result = encode(tag)
    alt_result = encode(alt_tag)

    # then
    assert result == {"value": None}
    assert alt_result == {"value": 11}
