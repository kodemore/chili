import datetime
from typing import Any, List

import pytest

from chili.mapper import KeyScheme, Mapper


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
    mapper = Mapper(scheme)
    result = mapper.map(raw_data)

    # then
    assert isinstance(result, dict)
    assert result == {
        "first_name": "Bob",
        "last_name": "Fetta",
        "email": "bob.fetta@universe.com",
    }


def test_can_preserve_keys() -> None:
    # given
    scheme = {
        "first_name": "firstName",
        "last_name": True,
        "email": 1,
    }

    raw_data = {
        "firstName": "Bob",
    }

    # when
    mapper = Mapper(scheme)
    result = mapper.map(raw_data)

    # then
    assert isinstance(result, dict)
    assert result == {
        "first_name": "Bob",
        "last_name": None,
        "email": None,
    }


def test_can_skip_keys() -> None:
    # given
    scheme = {
        "first_name": "firstName",
        "last_name": True,
        "email": 1,
    }

    raw_data = {
        "firstName": "Bob",
    }

    # when
    mapper = Mapper(scheme)
    result = mapper.map(raw_data, skip_keys=True)

    # then
    assert isinstance(result, dict)
    assert result == {
        "first_name": "Bob",
    }


def test_can_include_extra_keys() -> None:
    # given
    scheme = {
        "first_name": "firstName",
        ...: True,
    }

    raw_data = {"firstName": "Bob", "lastName": "Feta", "age": 20}

    # when
    mapper = Mapper(scheme)
    result = mapper.map(raw_data)

    # then
    assert isinstance(result, dict)
    assert result == {"first_name": "Bob", "lastName": "Feta", "age": 20}


def test_can_map_dynamically_keys() -> None:
    # given
    scheme = {
        ...: lambda key, value: (f"mapped_{key}", value),
    }

    raw_data = {"firstName": "Bob", "lastName": "Feta", "age": 20}

    # when
    mapper = Mapper(scheme)
    result = mapper.map(raw_data)

    # then
    assert isinstance(result, dict)
    assert result == {
        "mapped_firstName": "Bob",
        "mapped_lastName": "Feta",
        "mapped_age": 20,
    }


def test_can_map_data_with_nested_mapping() -> None:
    # given
    scheme = {
        "name": "pet",
        "age": "petAge",
        "tag": KeyScheme(key="petTag", scheme={"name": "pet_tag"}),
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
    scheme = {
        "name": "pet",
        "age": "petAge",
        "tags": KeyScheme("petTags", {"name": "pet_tag"}),
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
    data_mapper = Mapper(scheme)

    # when
    result = data_mapper.map(raw_data)

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
    }


def test_can_map_data_with_callable_mapper() -> None:
    # given
    scheme = {
        "name": lambda data: data["pet"],
        "age": "petAge",
        "tag": KeyScheme("petTag", {"name": "pet_tag"}),
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
        "tags": KeyScheme("tags", tag_resolver),
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
        "tags": [
            {"name": "tag-1"},
            {"name": "tag-2"},
            {"name": "tag-3"},
            {"name": "tag-4"},
        ],
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


def test_can_map_complex_format() -> None:
    # given
    raw_data = {
        "Authors": {"SS": ["Author1", "Author2"]},
        "Dimensions": {"S": "8.5 x 11.0 x 1.5"},
        "ISBN": {"S": "333-3333333333"},
        "Id": {"N": "103"},
        "Title": {"S": "Book 103 Title"},
    }

    # when
    result = Mapper(
        {
            ...: lambda key, value: (key.lower(), list(value.values())[0]),
        }
    ).map(raw_data)

    # then
    assert result == {
        "authors": ["Author1", "Author2"],
        "dimensions": "8.5 x 11.0 x 1.5",
        "isbn": "333-3333333333",
        "id": "103",
        "title": "Book 103 Title",
    }
