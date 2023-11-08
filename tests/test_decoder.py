from chili import Decoder, Mapper, decodable


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


def test_dencode_and_map() -> None:
    # given
    class Example:
        name: str
        age: int

        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

    mapper = Mapper(
        {
            "name": "_name",
            "age": "_age",
        }
    )
    encoder = Decoder[Example](mapper=mapper)

    # when
    data = encoder.decode(
        {
            "_name": "Bobik",
            "_age": 11,
        }
    )

    # then
    assert isinstance(data, Example)
    assert data.name == "Bobik"
    assert data.age == 11
