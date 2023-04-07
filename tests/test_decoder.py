import pytest

from chili import Decoder, decodable
from chili.error import DecoderError


def test_can_instantiate() -> None:
    # given
    @decodable
    class Example:
        ...

    # when
    instance = Decoder[Example]()

    # then
    assert isinstance(instance, Decoder)
    assert instance.__generic__ == Example


def test_fail_encode_non_encodable_type() -> None:
    # given
    class Example:
        name: str
        age: int

    # when
    with pytest.raises(DecoderError.invalid_type):
        Decoder[Example]()
