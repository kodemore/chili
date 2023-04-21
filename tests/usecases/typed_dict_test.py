from dataclasses import dataclass
from typing import TypedDict

from chili import decode, encode


def test_can_encode_typed_dict() -> None:
    # given
    @dataclass
    class Author:
        first_name: str
        last_name: str

    class Book(TypedDict):
        name: str
        author: Author
        no_pages: int

    book = Book(
        name="The Hobbit",
        author=Author(first_name="J.R.R.", last_name="Tolkien"),
        no_pages=295,
    )

    # when
    result = encode(book, Book)

    # then
    assert result == {
        "name": "The Hobbit",
        "author": {"first_name": "J.R.R.", "last_name": "Tolkien"},
        "no_pages": 295,
    }


def test_can_decode_typed_dict() -> None:
    # given
    @dataclass
    class Author:
        first_name: str
        last_name: str

    class Book(TypedDict):
        name: str
        author: Author
        no_pages: int

    raw_book = {
        "name": "The Hobbit",
        "author": {"first_name": "J.R.R.", "last_name": "Tolkien"},
        "no_pages": "295",
    }

    # when
    result = decode(raw_book, Book)

    # then
    assert isinstance(result, dict)
    assert result["name"] == "The Hobbit"
    assert result["no_pages"] == 295
    assert isinstance(result["author"], Author)
    assert result["author"].first_name == "J.R.R."
    assert result["author"].last_name == "Tolkien"
