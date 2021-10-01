from datetime import datetime
from typing import List, Tuple, Any, Optional

from chili import hydrate, asdict
from dataclasses import dataclass, field


def test_can_hydrate_with_flat_mapping() -> None:
    # given
    name_map = {
        "firstName": "first_name",
        "lastName": "last_name",
        "emailAddress": "email"
    }
    raw_data = {
        "firstName": "Bob",
        "lastName": "Fetta",
        "emailAddress": "bob.fetta@universe.com",
    }

    @dataclass
    class User:
        first_name: str
        last_name: str
        email: str

    # when
    instance = hydrate(raw_data, User, mapping=name_map)

    # then
    assert isinstance(instance, User)
    assert instance.first_name == raw_data["firstName"]
    assert instance.last_name == raw_data["lastName"]
    assert instance.email == raw_data["emailAddress"]


def test_can_hydrate_with_nested_mapping() -> None:
    # given
    @dataclass
    class Tag:
        name: str

    @dataclass
    class Pet:
        name: str
        age: int = 1
        tag: Tag = None

    name_map = {
        "pet": "name",
        "petAge": "age",
        "petTag": {
            "__name__": "tag",
            "pet_tag": "name",
        }
    }
    raw_data = {
        "pet": "Pimpek",
        "petAge": 4,
        "petTag": {
            "pet_tag": "tag-1",
        }
    }

    # when
    instance = hydrate(raw_data, Pet, mapping=name_map)

    # then
    assert isinstance(instance, Pet)
    assert isinstance(instance.tag, Tag)


def test_can_hydrate_with_nested_list_mapping() -> None:
    # given
    @dataclass
    class Tag:
        name: str

    @dataclass
    class Pet:
        name: str
        age: int = 1
        tags: List[Tag] = field(default_factory=list)

    name_map = {
        "pet": "name",
        "petAge": "age",
        "tags": {
            "pet_tag": "name",
        }
    }
    raw_data = {
        "pet": "Pimpek",
        "petAge": 4,
        "tags": [
            {"pet_tag": "tag-1", },
            {"pet_tag": "tag-2", },
            {"pet_tag": "tag-3", },
            {"pet_tag": "tag-4", },
        ]
    }

    # when
    instance = hydrate(raw_data, Pet, mapping=name_map)

    # then
    assert isinstance(instance, Pet)
    assert isinstance(instance.tags, List)
    for item in instance.tags:
        assert isinstance(item, Tag)


def test_can_hydrate_with_callable() -> None:
    # given
    @dataclass
    class Tag:
        name: str

    @dataclass
    class Pet:
        name: str
        age: int = 1
        tag: Tag = None

    name_map = {
        "pet": lambda value, _: ("name", value),
        "petAge": "age",
        "petTag": lambda value, _: ("tag", {"name": value["pet_tag"]})
    }
    raw_data = {
        "pet": "Pimpek",
        "petAge": 4,
        "petTag": {
            "pet_tag": "tag-1",
        }
    }

    # when
    instance = hydrate(raw_data, Pet, mapping=name_map)

    # then
    assert isinstance(instance, Pet)
    assert isinstance(instance.tag, Tag)


def test_can_hydrate_with_callable_in_list_mapping() -> None:
    # given
    @dataclass
    class Tag:
        name: str

    @dataclass
    class Pet:
        name: str
        age: int = 1
        tags: List[Tag] = field(default_factory=list)

    def tag_resolver(scope: Any, _: dict) -> Tuple[str, Any]:
        return "tags", [{"name": tag["pet_tag"]} for tag in scope]

    name_map = {
        "pet": "name",
        "petAge": "age",
        "tags": tag_resolver,
    }

    raw_data = {
        "pet": "Pimpek",
        "petAge": 4,
        "tags": [
            {"pet_tag": "tag-1", },
            {"pet_tag": "tag-2", },
            {"pet_tag": "tag-3", },
            {"pet_tag": "tag-4", },
        ]
    }

    # when
    instance = hydrate(raw_data, Pet, mapping=name_map)

    # then
    assert isinstance(instance, Pet)
    assert isinstance(instance.tags, List)
    for item in instance.tags:
        assert isinstance(item, Tag)
