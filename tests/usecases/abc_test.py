from abc import ABC

from chili.decoder import decodable, decode
from chili.encoder import encodable, encode


def test_can_encode_class_generalizing_abc() -> None:
    # given
    class AbstractPet(ABC):
        name: str

        def __init__(self, name: str):
            self.name = name

    @encodable
    class ConcretePet(AbstractPet):
        age: int

        def __init__(self, name: str, age: int):
            self.age = age
            super().__init__(name)

    pet = ConcretePet("Bob", 4)

    # when
    decoded = encode(pet)

    # then
    assert decoded == {
        "name": "Bob",
        "age": 4,
    }


def test_can_decode_class_generalizing_abc() -> None:
    # given
    class AbstractPet(ABC):
        name: str

        def __init__(self, name: str):
            self.name = name

    @decodable
    class ConcretePet(AbstractPet):
        age: int

        def __init__(self, name: str, age: int):
            self.age = age
            super().__init__(name)

    pet = {
        "name": "Bob",
        "age": 4,
    }

    # when
    decoded = decode(pet, ConcretePet)

    # then
    assert isinstance(decoded, ConcretePet)
