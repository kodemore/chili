from enum import Enum
from typing import Optional

from chili import registry


def test_hydrate_optional_enum() -> None:
    # given
    class MyEnum(Enum):
        ELEMENT = "hello"

    strategy = registry.get_for(Optional[MyEnum])
    expected = MyEnum("hello")

    # when
    result = strategy.hydrate("hello")

    # then
    assert result == expected
