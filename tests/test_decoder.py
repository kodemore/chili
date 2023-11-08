from chili import Decoder, decodable


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
