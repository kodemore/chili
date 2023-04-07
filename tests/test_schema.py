from typing import ClassVar

from chili.typing import create_schema, Property, _PROPERTIES


def test_can_create_schema() -> None:
    # given
    class Pet:
        name: str
        age: int = 10

    # when
    schema = create_schema(Pet)

    # then
    assert schema == {
        "name": Property("name", str),
        "age": Property("age", int)
    }

def test_can_ignore_class_vars() -> None:
    # given
    class Pet:
        name: str
        age: ClassVar[int] = 10

    # when
    schema = create_schema(Pet)

    # then
    assert schema == {
        "name": Property("name", str),
    }


def test_can_compose_schemas_when_inherited() -> None:
    # given
    class Pet:
        name: str
        age: int = 10

    setattr(Pet, _PROPERTIES, create_schema(Pet))

    class DogPet(Pet):
        race: str

    # when
    schema = create_schema(DogPet)

    # then
    assert schema == {
        "name": Property("name", str),
        "age": Property("age", int),
        "race": Property("race", str)
    }
