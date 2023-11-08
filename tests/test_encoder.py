from collections import UserString

from chili import Encoder, Mapper, encodable


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


def test_can_encode_non_encodable_type() -> None:
    # given
    class Example:
        name: str
        age: int

        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

    # when
    encoder = Encoder[Example]()
    value = encoder.encode(Example("bob", 33))

    # then
    assert value == {
        "name": "bob",
        "age": 33,
    }


def test_can_encode_complex_non_encodable_type() -> None:
    # given
    class ExampleName(UserString):
        pass

    class Example:
        name: ExampleName
        age: int

        def __init__(self, name: ExampleName, age: int):
            self.name = name
            self.age = age

    # when
    encoder = Encoder[Example]()
    value = encoder.encode(Example(ExampleName("bob"), 33))

    # then
    assert value == {
        "name": "bob",
        "age": 33,
    }


def test_encode_and_map() -> None:
    # given
    class Example:
        name: str
        age: int

        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

    mapper = Mapper(
        {
            "_name": "name",
            "_age": "age",
        }
    )
    encoder = Encoder[Example](mapper=mapper)

    # when
    data = encoder.encode(Example("Bobik", 11))

    # then
    assert data == {
        "_name": "Bobik",
        "_age": 11,
    }
