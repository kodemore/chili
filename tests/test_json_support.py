from dataclasses import dataclass
from typing import List
from chili import from_json, as_json


def test_json_support() -> None:
    @dataclass
    class Tag:
        id: str
        name: str

    @dataclass
    class Pet:
        name: str
        tags: List[Tag]

    pet_json = '{"name": "Bobik", "tags": [{"id": "12", "name": "dog"}]}'

    pet = from_json(pet_json, Pet)
    assert isinstance(pet, Pet)
    assert isinstance(pet.tags, List)
    assert isinstance(pet.tags[0], Tag)

    assert pet_json == as_json(pet)
