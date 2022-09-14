import datetime
from typing import Any, List

import pytest

from chili.mapping import KeyMapper, Mapper


def test_can_map_data_with_flat_mapping() -> None:
    # given
    scheme = {"first_name": "firstName", "last_name": "lastName", "email": "emailAddress"}

    raw_data = {
        "firstName": "Bob",
        "lastName": "Fetta",
        "emailAddress": "bob.fetta@universe.com",
    }

    # when
    mapper = Mapper(scheme)
    result = mapper.map(raw_data)

    # then
    assert isinstance(result, dict)
    assert result["first_name"] == raw_data["firstName"]
    assert result["last_name"] == raw_data["lastName"]
    assert result["email"] == raw_data["emailAddress"]


def test_can_map_data_with_nested_mapping() -> None:
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
    data_mapper = Mapper(scheme)

    # when
    result = data_mapper.map(raw_data)

    # then
    assert result == {"name": "Pimpek", "age": 4, "tag": {"name": "tag-1"}}


def test_can_map_data_with_nested_list_mapping() -> None:
    scheme = {"name": "pet", "age": "petAge", "tags": KeyMapper("petTags", {"name": "pet_tag"})}
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
    data_mapper = Mapper(scheme)

    # when
    result = data_mapper.map(raw_data)

    # then
    assert result == {
        "name": "Pimpek",
        "age": 4,
        "tags": [{"name": "tag-1"}, {"name": "tag-2"}, {"name": "tag-3"}, {"name": "tag-4"}],
    }


def test_can_map_data_with_callable_mapper() -> None:
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
    data_mapper = Mapper(scheme)

    # when
    result = data_mapper.map(raw_data)

    # then
    assert result == {"name": "Pimpek", "age": 4, "tag": {"name": "tag-1"}}


def test_can_use_callable_in_key_mapper() -> None:
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
    mapper = Mapper(scheme)

    # when
    result = mapper.map(raw_data)

    # then
    assert result == {
        "name": "Pimpek",
        "age": 4,
        "tags": [{"name": "tag-1"}, {"name": "tag-2"}, {"name": "tag-3"}, {"name": "tag-4"}],
    }


def test_can_copy_value() -> None:
    # given
    scheme = {
        "name": 1,
        "age": True,
    }

    raw_data = {
        "name": "Pimpek",
        "age": 14,
    }
    mapper = Mapper(scheme)

    # when
    result = mapper.map(raw_data)

    # then
    assert result == {
        "name": "Pimpek",
        "age": 14,
    }


def test_fail_on_invalid_mapping() -> None:
    # given
    scheme = {
        "name": datetime.datetime.now(),
    }

    raw_data = {
        "pet": "Pimpek",
    }
    mapper = Mapper(scheme)

    # then
    with pytest.raises(ValueError):
        mapper.map(raw_data)


def test_can_map_nested_dict_without_key_change() -> None:
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
    mapper = Mapper(scheme)

    # when
    result = mapper.map(raw_data)

    # then
    assert result == {
        "name": "Pimpek",
        "tag": {
            "name": "puppy",
        },
    }
