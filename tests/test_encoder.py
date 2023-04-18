import pytest

from chili import Encoder, encodable
from chili.error import EncoderError


def test_can_instantiate() -> None:
    # given
    @encodable
    class Example:
        ...

    # when
    instance = Encoder[Example]()

    # then
    assert isinstance(instance, Encoder)
    assert instance.__generic__ == Example


def test_fail_encode_non_encodable_type() -> None:
    # given
    class Example:
        name: str
        age: int

    # when
    with pytest.raises(EncoderError.invalid_type):
        Encoder[Example]()
