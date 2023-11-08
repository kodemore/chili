from chili import Serializer, serializable


def test_can_instantiate() -> None:
    # given
    @serializable
    class Example:
        ...

    # when
    instance = Serializer[Example]()

    # then
    assert isinstance(instance, Serializer)
    assert instance.__generic__ == Example


def test_can_encode_non_serializable_type() -> None:
    # given
    class Example:
        name: str
        age: int

        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

    # when
    serializer = Serializer[Example]()
    value = serializer.encode(Example("bob", 33))

    # then
    assert value == {
        "name": "bob",
        "age": 33,
    }


def test_can_decode_non_serializable_type() -> None:
    # given
    class Example:
        name: str
        age: int

        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

    # when
    serializer = Serializer[Example]()
    value = serializer.decode(
        {
            "name": "bob",
            "age": 33,
        }
    )

    # then
    assert isinstance(value, Example)
    assert value.name == "bob"
    assert value.age == 33
