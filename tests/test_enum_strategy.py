from enum import Enum, IntEnum

import pytest

from chili import registry


def test_hydrate_enum() -> None:
    # given
    class Colors(Enum):
        RED = "red"
        YELLOW = "yellow"
        GREEN = "green"
        ORANGE = "orange"

    strategy = registry.get_for(Colors)

    # when
    red = strategy.hydrate("red")
    orange = strategy.hydrate("orange")

    # then
    assert isinstance(red, Colors)
    assert red == Colors.RED
    assert isinstance(orange, Colors)
    assert orange == Colors.ORANGE


def test_hydrate_int_enum() -> None:
    # given
    class Colors(IntEnum):
        RED = 1
        YELLOW = 2
        GREEN = 3
        ORANGE = 4

    strategy = registry.get_for(Colors)

    # when
    red = strategy.hydrate(1)
    orange = strategy.hydrate(4)

    # then
    assert isinstance(red, Colors)
    assert red == Colors.RED
    assert isinstance(orange, Colors)
    assert orange == Colors.ORANGE


def test_extract_enum() -> None:
    # given
    class Colors(Enum):
        RED = "red"
        YELLOW = "yellow"
        GREEN = "green"
        ORANGE = "orange"

    strategy = registry.get_for(Colors)
    red = strategy.hydrate("red")
    orange = strategy.hydrate("orange")

    # when
    extracted_red = strategy.extract(red)
    extracted_orange = strategy.extract(orange)

    # then
    assert extracted_red == "red"
    assert extracted_orange == "orange"


def test_fail_hydrating_invalid_enum() -> None:
    # given
    class Colors(Enum):
        RED = "red"
        YELLOW = "yellow"
        GREEN = "green"
        ORANGE = "orange"

    strategy = registry.get_for(Colors)

    # when
    with pytest.raises(ValueError) as error:
        strategy.hydrate("silver")

    # then
    assert str(error.value)[0:23] == "'silver' is not a valid"
