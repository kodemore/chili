from typing import TypeVar, Generic, List

from chili import encodable, encode
from chili.error import EncoderError

import pytest


def test_encode_generic_type() -> None:
    # given
    T = TypeVar("T")

    @encodable
    class Book:
        name: str
        pages: int

        def __init__(self, name: str, pages: int):
            self.name = name
            self.pages = pages

    @encodable
    class Author:
        first_name: str
        last_name: str

        def __init__(self, first_name: str, last_name: str):
            self.first_name = first_name
            self.last_name = last_name

    @encodable
    class Array(Generic[T]):
        count: int
        items: List[T]

        def __init__(self, count: int, items: List[T]):
            self.count = count
            self.items = items

    array_of_books = Array[Book](
        count=2, items=[Book("Book 1", 100), Book("Book 2", 200)]
    )

    array_of_authors = Array[Author](
        count=2, items=[Author("John", "Doe"), Author("Jane", "Doe")]
    )

    # when
    books = encode(array_of_books, Array[Book])
    authors = encode(array_of_authors, Array[Author])

    # then
    assert books == {
        "count": 2,
        "items": [{"name": "Book 1", "pages": 100}, {"name": "Book 2", "pages": 200}],
    }
    assert authors == {
        "count": 2,
        "items": [
            {"first_name": "John", "last_name": "Doe"},
            {"first_name": "Jane", "last_name": "Doe"},
        ],
    }


def test_fail_encode_non_parametrized_generic() -> None:
    # given
    T = TypeVar("T")

    @encodable
    class Book:
        name: str
        pages: int

        def __init__(self, name: str, pages: int):
            self.name = name
            self.pages = pages

    @encodable
    class Array(Generic[T]):
        count: int
        items: List[T]

        def __init__(self, count: int, items: List[T]):
            self.count = count
            self.items = items

    array_of_books = Array[Book](
        count=2, items=[Book("Book 1", 100), Book("Book 2", 200)]
    )

    # when
    with pytest.raises(EncoderError):
        encode(array_of_books, Array)


def test_fail_encode_generic_with_non_encondable_type() -> None:
    # given
    T = TypeVar("T")

    class Book:
        name: str
        pages: int

        def __init__(self, name: str, pages: int):
            self.name = name
            self.pages = pages

    @encodable
    class Array(Generic[T]):
        count: int
        items: List[T]

        def __init__(self, count: int, items: List[T]):
            self.count = count
            self.items = items

    array_of_books = Array[Book](
        count=2, items=[Book("Book 1", 100), Book("Book 2", 200)]
    )

    # when
    with pytest.raises(EncoderError):
        encode(array_of_books, Array[Book])
