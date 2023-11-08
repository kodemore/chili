from chili import Decoder, Encoder


def test_can_encode_private_property() -> None:
    # given
    class Pet:
        age: int
        name: str

        def __init__(self, name: str, age: int) -> None:
            self._name = name
            self._age = age

        @property
        def name(self) -> str:
            return self._name

        @property
        def age(self) -> int:
            return self._age

    encoder = Encoder[Pet]()

    # when
    data = encoder.encode(Pet("Bobik", 3))

    # then
    assert data == {
        "age": 3,
        "name": "Bobik",
    }


def test_can_decode_private_property() -> None:
    # given
    class Pet:
        age: int
        name: str

        def __init__(self, name: str, age: int) -> None:
            self._name = name
            self._age = age

        @property
        def name(self) -> str:
            return self._name

        @property
        def age(self) -> int:
            return self._age

    encoder = Decoder[Pet]()

    # when
    pet = encoder.decode(
        {
            "age": 3,
            "name": "Bobik",
        }
    )

    # then
    assert isinstance(pet, Pet)

    print(pet)
