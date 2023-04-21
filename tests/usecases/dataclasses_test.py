from dataclasses import dataclass, field
from typing import List, Generic, TypeVar

import pytest

from chili import Decoder
from chili import Encoder
from chili.decoder import ClassDecoder, decode
from chili.error import DecoderError


def test_can_decode_dataclass() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int
        favourite_food: List[str]

    decoder = Decoder[Pet]()
    data = {"name": "Fido", "age": 3, "favourite_food": [7, "bones"]}

    # when
    result = decoder.decode(data)

    # then
    assert isinstance(result, Pet)
    assert result.name == "Fido"
    assert result.age == 3
    assert result.favourite_food == ["7", "bones"]


def test_can_encode_dataclass() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int
        favourite_food: List[str]

    decoder = Encoder[Pet]()
    pet = Pet("Fido", 3, ["7", "bones"])

    # when
    result = decoder.encode(pet)

    # then
    assert isinstance(result, dict)
    assert result == {"name": "Fido", "age": 3, "favourite_food": ["7", "bones"]}


def test_can_encode_nested_dataclasses() -> None:
    # given
    @dataclass
    class Tag:
        name: str

    @dataclass
    class Author:
        first_name: str
        last_name: str

    @dataclass
    class Book:
        name: str
        author: Author
        tags: List[Tag]

    book = Book(
        "The Hobbit", Author("J.R.R.", "Tolkien"), [Tag("Fantasy"), Tag("Adventure")]
    )

    encoder = Encoder[Book]()

    # when
    result = encoder.encode(book)

    # then
    assert isinstance(result, dict)
    assert result == {
        "name": "The Hobbit",
        "author": {"first_name": "J.R.R.", "last_name": "Tolkien"},
        "tags": [{"name": "Fantasy"}, {"name": "Adventure"}],
    }


def test_can_decode_nested_dataclasses() -> None:
    # given
    @dataclass
    class Tag:
        name: str

    @dataclass
    class Author:
        first_name: str
        last_name: str

    @dataclass
    class Book:
        name: str
        author: Author
        tags: List[Tag]

    book_data = {
        "name": "The Hobbit",
        "author": {"first_name": "J.R.R.", "last_name": "Tolkien"},
        "tags": [{"name": "Fantasy"}, {"name": "Adventure"}],
    }

    decoder = Decoder[Book]()

    # when
    result = decoder.decode(book_data)

    # then
    assert isinstance(result, Book)
    assert isinstance(result.author, Author)
    assert all(isinstance(tag, Tag) for tag in result.tags)
    assert result.tags[0].name == "Fantasy"
    assert result.tags[1].name == "Adventure"


def test_can_decode_with_default_values() -> None:
    # given
    @dataclass
    class Book:
        name: str
        author: str
        tags: List[str] = field(default_factory=list)

    book_data = {"name": "The Hobbit", "author": "J.R.R. Tolkien"}
    decoder = Decoder[Book]()

    # when
    result = decoder.decode(book_data)

    # then
    assert isinstance(result.tags, list)


def test_can_decode_with_default_values_explicit_dataclass_type() -> None:
    # given
    @dataclass
    class Book:
        name: str
        author: str
        tags: List[str] = field(default_factory=list)

    book_data = {"name": "The Hobbit", "author": "J.R.R. Tolkien"}
    decoder = ClassDecoder(Book)

    # when
    result: Book = decoder.decode(book_data)

    # then
    assert isinstance(result.tags, list)


def test_fail_decode_non_parametrized_generic_class() -> None:
    # given
    T = TypeVar("T")

    @dataclass
    class Book(Generic[T]):
        name: str
        author: str
        tags: List[T] = field(default_factory=list)

    class TaggedBook(Book[str]):
        pass

    tagged_book_data = {
        "name": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "tags": ["Fantasy"],
    }

    # when
    with pytest.raises(DecoderError):
        decode(tagged_book_data, TaggedBook)
