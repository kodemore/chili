import datetime
from typing import Any, List

import pytest

from chili.mapping import KeyMapper, PersistentMapper


def test_can_map_data_with_flat_mapping() -> None:
    # given
    scheme = {
        "first_name": "firstName",
        "last_name": "lastName",
        "email": "emailAddress",
    }

    raw_data = {
        "firstName": "Bob",
        "lastName": "Fetta",
        "emailAddress": "bob.fetta@universe.com",
    }

    # when
    mapper = PersistentMapper(scheme)
    result = mapper.map(raw_data)

    # then
    assert isinstance(result, dict)
    assert result["first_name"] == raw_data["firstName"]
    assert result["last_name"] == raw_data["lastName"]
    assert result["email"] == raw_data["emailAddress"]
    assert result["firstName"] == raw_data["firstName"]
    assert result["lastName"] == raw_data["lastName"]
    assert result["emailAddress"] == raw_data["emailAddress"]


def test_can_map_data_with_nested_mapping_with_persistence() -> None:
    # given
    scheme = {
        "name": "pet",
        "age": "petAge",
        "tag": KeyMapper("petTag", {"name": "pet_tag"}),
    }
    raw_data = {
        "pet": "Pimpek",
        "petAge": 4,
        "petTag": {
            "pet_tag": "tag-1",
        },
    }
    data_mapper = PersistentMapper(scheme)

    # when
    result = data_mapper.map(raw_data)

    # then
    assert result == {
        "name": "Pimpek",
        "age": 4,
        "tag": {"name": "tag-1", "pet_tag": "tag-1"},
        "pet": "Pimpek",
        "petAge": 4,
        "petTag": {
            "pet_tag": "tag-1",
        },
    }


def test_can_map_data_with_nested_list_mapping_with_persistence() -> None:
    scheme = {
        "name": "pet",
        "age": "petAge",
        "tags": KeyMapper("petTags", {"name": "pet_tag"}),
    }
    raw_data = {
        "pet": "Pimpek",
        "petAge": 4,
        "petTags": [
            {
                "pet_tag": "tag-1",
            },
            {
                "pet_tag": "tag-2",
            },
            {
                "pet_tag": "tag-3",
            },
            {
                "pet_tag": "tag-4",
            },
        ],
    }
    data_mapper = PersistentMapper(scheme)

    # when
    result = data_mapper.map(raw_data)

    # then
    assert result == {
        "name": "Pimpek",
        "age": 4,
        "tags": [
            {"name": "tag-1", "pet_tag": "tag-1"},
            {"name": "tag-2", "pet_tag": "tag-2"},
            {"name": "tag-3", "pet_tag": "tag-3"},
            {"name": "tag-4", "pet_tag": "tag-4"},
        ],
        "pet": "Pimpek",
        "petAge": 4,
        "petTags": [
            {
                "pet_tag": "tag-1",
            },
            {
                "pet_tag": "tag-2",
            },
            {
                "pet_tag": "tag-3",
            },
            {
                "pet_tag": "tag-4",
            },
        ],
    }


def test_can_map_data_with_callable_mapper_with_persistence() -> None:
    # given
    scheme = {
        "name": lambda data: data["pet"],
        "age": "petAge",
        "tag": KeyMapper("petTag", {"name": "pet_tag"}),
    }
    raw_data = {
        "pet": "Pimpek",
        "petAge": 4,
        "petTag": {
            "pet_tag": "tag-1",
        },
    }
    data_mapper = PersistentMapper(scheme)

    # when
    result = data_mapper.map(raw_data)

    # then
    assert result == {
        "name": "Pimpek",
        "age": 4,
        "tag": {"name": "tag-1", "pet_tag": "tag-1"},
        "pet": "Pimpek",
        "petAge": 4,
        "petTag": {
            "pet_tag": "tag-1",
        },
    }


def test_can_use_callable_in_key_mapper_with_persistence() -> None:
    # given
    def tag_resolver(data: Any) -> List[dict]:
        return [{"name": tag["pet_tag"]} for tag in data]

    scheme = {
        "name": "pet",
        "age": "petAge",
        "tags": KeyMapper("tags", tag_resolver),
    }

    raw_data = {
        "pet": "Pimpek",
        "petAge": 4,
        "tags": [
            {
                "pet_tag": "tag-1",
            },
            {
                "pet_tag": "tag-2",
            },
            {
                "pet_tag": "tag-3",
            },
            {
                "pet_tag": "tag-4",
            },
        ],
    }
    mapper = PersistentMapper(scheme)

    # when
    result = mapper.map(raw_data)
    print(result)
    # then
    assert result == {
        "name": "Pimpek",
        "age": 4,
        "tags": [
            {"name": "tag-1"},
            {"name": "tag-2"},
            {"name": "tag-3"},
            {"name": "tag-4"},
        ],
        "pet": "Pimpek",
        "petAge": 4,
    }


def test_can_copy_value_with_persistence() -> None:
    # given
    scheme = {
        "name": 1,
        "age": True,
    }

    raw_data = {
        "name": "Pimpek",
        "age": 14,
    }
    mapper = PersistentMapper(scheme)

    # when
    result = mapper.map(raw_data)

    # then
    assert result == {
        "name": "Pimpek",
        "age": 14,
    }


def test_fail_on_invalid_mapping_with_persistence() -> None:
    # given
    scheme = {
        "name": datetime.datetime.now(),
    }

    raw_data = {
        "pet": "Pimpek",
    }
    mapper = PersistentMapper(scheme)

    # then
    with pytest.raises(ValueError):
        mapper.map(raw_data)


def test_can_map_with_persistence() -> None:
    # given
    scheme = {"persistName": "name"}

    raw_data = {
        "name": "Pimpek",
    }
    mapper = PersistentMapper(scheme)

    # when
    result = mapper.map(raw_data)

    # then
    assert result == {
        "name": "Pimpek",
        "persistName": "Pimpek",
    }


def test_can_map_nested_dict_with_persistence() -> None:
    # given
    scheme = {
        "name": 1,
        "tag": {"name": "tagName"},
    }

    raw_data = {
        "name": "Pimpek",
        "tag": {
            "tagName": "puppy",
        },
    }
    mapper = PersistentMapper(scheme)

    # when
    result = mapper.map(raw_data)

    # then
    assert result == {
        "name": "Pimpek",
        "tag": {
            "name": "puppy",
            "tagName": "puppy",
        },
    }
