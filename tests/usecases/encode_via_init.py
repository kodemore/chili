from chili import decodable, decode, encodable, encode, serializable


def test_can_encode_via_init() -> None:
    # given
    @encodable(use_init=True)
    class Pet:
        def __init__(self, name: str, age: int = 10):
            self._hidden_name = name
            self._hidden_age = age

    pet = Pet("Fido", 3)

    # when
    encoded = encode(pet)

    # then
    assert encoded == {
        "name": "Fido",
        "age": 3,
    }


def test_can_decode_via_init() -> None:
    # given
    @decodable(use_init=True)
    class Pet:
        def __init__(self, name: str, age: int = 10):
            self._hidden_name = name
            self._hidden_age = age

    # when
    decoded = decode(
        {
            "name": "Fido",
            "age": 3,
        },
        Pet,
    )

    # then
    assert isinstance(decoded, Pet)
    assert decoded._hidden_name == "Fido"
    assert decoded._hidden_age == 3


def test_can_serialize_via_init() -> None:
    # given
    @serializable(use_init=True)
    class Pet:
        def __init__(self, name: str, age: int = 10):
            self._hidden_name = name
            self._hidden_age = age

    pet = Pet("Fido", 3)

    # when
    encoded = encode(pet)
    decoded = decode(encoded, Pet)

    # then
    assert isinstance(decoded, Pet)
    assert decoded._hidden_name == "Fido"
    assert decoded._hidden_age == 3
